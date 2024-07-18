from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import TypeVar

import websockets
from exponent.core.remote_execution import files, git, system_context
from exponent.core.remote_execution.code_execution import execute_code
from exponent.core.remote_execution.file_write import execute_file_write
from exponent.core.remote_execution.session import (
    RemoteExecutionClientSession,
    get_session,
)
from exponent.core.remote_execution.types import (
    CLIConnectedState,
    CodeExecutionRequest,
    CreateChatResponse,
    ExecutionEndResponse,
    FileWriteRequest,
    GetAllTrackedFilesRequest,
    GetFileAttachmentRequest,
    GetMatchingFilesRequest,
    HeartbeatInfo,
    ListFilesRequest,
    RemoteExecutionRequestType,
    RemoteExecutionResponse,
    RemoteExecutionResponseType,
    StartChatRequest,
    StartChatResponse,
    SystemContextRequest,
    UseToolsConfig,
)
from exponent.core.remote_execution.utils import (
    aenumerate,
    deserialize_api_response,
    deserialize_request_data,
    serialize_message,
)
from httpx import (
    AsyncClient,
    codes as http_status,
)
from pydantic import BaseModel

logger = logging.getLogger(__name__)


TModel = TypeVar("TModel", bound=BaseModel)


class RemoteExecutionClient:
    def __init__(
        self,
        session: RemoteExecutionClientSession,
    ):
        self.current_session = session

        self.file_cache: files.FileCache = files.FileCache(session.working_directory)

    @property
    def working_directory(self) -> str:
        return self.current_session.working_directory

    @property
    def api_client(self) -> AsyncClient:
        return self.current_session.api_client

    async def for_each_execution_request(
        self,
        chat_uuid: str,
        callback: Callable[
            [RemoteExecutionRequestType], Awaitable[RemoteExecutionResponse]
        ],
    ) -> None:
        async for websocket in self.ws_connect_with_retry(
            f"/api/ws/chat/{chat_uuid}/requests",
            connection_name="Execution-request",
        ):
            while True:
                request_json = str(await websocket.recv())
                request = deserialize_request_data(request_json)
                response = await callback(request)
                await websocket.send(serialize_message(response))

    async def check_remote_end_event(self, chat_uuid: str) -> bool:
        response = await self.api_client.get(
            f"/api/remote_execution/{chat_uuid}/execution_end",
        )
        execution_end_response = await deserialize_api_response(
            response, ExecutionEndResponse
        )
        return execution_end_response.execution_ended

    async def create_chat(self) -> CreateChatResponse:
        response = await self.api_client.post(
            "/api/remote_execution/create_chat",
        )
        return await deserialize_api_response(response, CreateChatResponse)

    async def start_chat(
        self, chat_uuid: str, prompt: str, use_tools_config: UseToolsConfig
    ) -> StartChatResponse:
        response = await self.api_client.post(
            "/api/remote_execution/start_chat",
            json=StartChatRequest(
                chat_uuid=chat_uuid,
                prompt=prompt,
                use_tools_config=use_tools_config,
            ).model_dump(),
            timeout=60,
        )
        return await deserialize_api_response(response, StartChatResponse)

    def get_heartbeat_info(self) -> HeartbeatInfo:
        return HeartbeatInfo(
            system_info=system_context.get_system_info(self.working_directory),
        )

    async def send_heartbeat(self, chat_uuid: str) -> CLIConnectedState:
        logger.info(f"Sending heartbeat for chat_uuid {chat_uuid}")
        heartbeat_info = self.get_heartbeat_info()
        response = await self.api_client.post(
            f"/api/remote_execution/{chat_uuid}/heartbeat",
            content=heartbeat_info.model_dump_json(),
            timeout=60,
        )
        if response.status_code != http_status.OK:
            raise Exception(
                f"Heartbeat failed with status code {response.status_code} and response {response.text}"
            )
        connected_state = await deserialize_api_response(response, CLIConnectedState)
        logger.info(f"Heartbeat response: {connected_state}")
        return connected_state

    async def send_heartbeats(self, chat_uuid: str) -> None:
        async for websocket in self.ws_connect_with_retry(
            f"/api/ws/chat/{chat_uuid}/heartbeats",
            connection_name="Heartbeat",
        ):
            while True:
                heartbeat_info = self.get_heartbeat_info()
                await websocket.send(heartbeat_info.model_dump_json())
                _response = await websocket.recv()
                await asyncio.sleep(1)

    async def wait_for_disconnect_signal(self, chat_uuid: str) -> None:
        async for websocket in self.ws_connect_with_retry(
            f"/api/ws/chat/{chat_uuid}/signals/disconnect",
            connection_name="Signal-listener",
        ):
            _response = await websocket.recv()
            await websocket.send("")
            await websocket.close()
            break

    async def handle_request(
        self, request: RemoteExecutionRequestType
    ) -> RemoteExecutionResponseType:
        response: RemoteExecutionResponseType
        if isinstance(request, CodeExecutionRequest):
            response = await execute_code(
                request, self.current_session, working_directory=self.working_directory
            )
        if isinstance(request, FileWriteRequest):
            response = execute_file_write(
                request, working_directory=self.working_directory
            )
        elif isinstance(request, ListFilesRequest):
            response = files.list_files(request)
        elif isinstance(request, GetFileAttachmentRequest):
            response = files.get_file_attachment(request)
        elif isinstance(request, GetMatchingFilesRequest):
            response = files.get_matching_files(request, self.file_cache)
        elif isinstance(request, SystemContextRequest):
            response = system_context.get_system_context(
                request, self.working_directory
            )
        elif isinstance(request, GetAllTrackedFilesRequest):
            response = git.get_all_tracked_files(request, self.working_directory)
        return response

    async def ws_connect_with_retry(
        self, path: str, connection_name: str, max_retries: int = 5
    ) -> AsyncGenerator[websockets.WebSocketClientProtocol, None]:
        connection_name = connection_name.capitalize()
        reconnect_msg = f"{connection_name} connection closed, re-establishing..."
        disconnect_msg = (
            f"{connection_name} connection closed {max_retries} times, exiting."
        )

        async for i, websocket in aenumerate(self.ws_connect(path)):
            try:
                yield websocket
            except websockets.ConnectionClosed:
                if i >= max_retries:
                    logger.warning(disconnect_msg)
                    raise
                logger.warning(reconnect_msg)
                continue

    def ws_connect(self, path: str) -> websockets.connect:
        base_url = (
            str(self.api_client.base_url)
            .replace("http://", "ws://")
            .replace("https://", "wss://")
        )

        url = f"{base_url}{path}"
        headers = {"api-key": self.api_client.headers["api-key"]}

        return websockets.connect(url, extra_headers=headers)

    @staticmethod
    @asynccontextmanager
    async def session(
        api_key: str, base_url: str, working_directory: str
    ) -> AsyncGenerator[RemoteExecutionClient, None]:
        async with get_session(working_directory, base_url, api_key) as session:
            yield RemoteExecutionClient(session)
