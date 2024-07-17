from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from exponent.core.remote_execution.languages.python import Kernel
from exponent.core.remote_execution.utils import format_error_log
from httpx import AsyncClient, Request, Response


class SessionLog:
    def __init__(self) -> None:
        self.log_buffer: list[str] = []
        self.max_size = 5

    def append_log(self, log: str) -> None:
        self.log_buffer.append(log)
        self.log_buffer = self.log_buffer[-self.max_size :]

    def get_logs(self) -> list[str]:
        return self.log_buffer

    async def log_request(self, request: Request) -> None:
        self.append_log(f"Request: {request.method} {request.url}")

    async def log_response(self, response: Response) -> None:
        request = response.request
        await response.aread()
        self.append_log(
            f"Response for request: {request.method} {request.url}\n"
            f"Response: {response.status_code}, {response.text}"
        )


class RemoteExecutionClientSession:
    def __init__(self, working_directory: str, base_url: str, api_key: str):
        self.working_directory = working_directory
        self.kernel = Kernel(working_directory=working_directory)
        self.api_log = SessionLog()
        self.api_client = AsyncClient(
            base_url=base_url,
            headers={"API-KEY": api_key},
            event_hooks={
                "request": [self.api_log.log_request],
                "response": [self.api_log.log_response],
            },
        )

    async def send_exception_log(self, exc: Exception) -> None:
        error_log = format_error_log(exc, self.api_log.get_logs())
        if not error_log:
            return
        await self.api_client.post(
            "/api/remote_execution/log_error",
            content=error_log.model_dump_json(),
            timeout=60,
        )


@asynccontextmanager
async def get_session(
    working_directory: str,
    base_url: str,
    api_key: str,
) -> AsyncGenerator[RemoteExecutionClientSession, None]:
    session = RemoteExecutionClientSession(working_directory, base_url, api_key)
    try:
        yield session
    except Exception as exc:
        await session.send_exception_log(exc)
        raise exc
    finally:
        session.kernel.close()
        await session.api_client.aclose()
