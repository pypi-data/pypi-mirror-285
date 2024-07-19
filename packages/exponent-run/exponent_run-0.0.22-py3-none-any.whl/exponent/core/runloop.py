import json
import logging
from typing import Any

from httpx import (
    AsyncClient,
    Response,
)

logger = logging.getLogger(__name__)
_timeout = 30


class RunloopClient:
    def __init__(self, api_key: str, base_url: str = "https://api.runloop.ai"):
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.base_url = base_url

    async def create_devbox(
        self,
        entrypoint: str | None | None = None,
        environment_variables: dict[str, str] | None = None,
        setup_commands: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Create a running devbox.

        Args:
            entrypoint: (Optional) When specified, the Devbox will run this script as its main executable.
                The devbox lifecycle will be bound to entrypoint, shutting down when the process is complete.

            environment_variables: (Optional) Environment variables used to configure your Devbox.

            setup_commands: (Optional) List of commands needed to set up your Devbox. Examples might include
                fetching a tool or building your dependencies. Runloop will look optimize these steps for you.
        Returns:
            Devbox instance in the form of:
            {
                "id": str,
                "status": str (provisioning, initializing, running, failure,  shutdown),
                "create_time_ms": long
            }
        """

        async with AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/devboxes/",
                headers=self.headers,
                json={
                    "entrypoint": entrypoint,
                    "environment_variables": environment_variables,
                    "setup_commands": setup_commands,
                },
                # This is 30 seconds because the devbox might not be waricl
                timeout=_timeout,
            )
        return self._response_json(response)

    async def get_devbox(self, id: str) -> dict[str, Any]:
        """
        Get updated devbox.

        Args:
            id: Id of the devbox instance.
        Returns:
            Devbox instance in the form of:
            {
                "id": str,
                "status": str (provisioning, initializing, running, failure,  shutdown),
                "create_time_ms": long
            }
        """
        async with AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v1/devboxes/{id}",
                headers=self.headers,
            )
        return self._response_json(response)

    async def shutdown_devbox(self, id: str) -> dict[str, Any]:
        """
        Shutdown devbox.

        Args:
            id: Id of the devbox instance.
        Returns:
            Updated devbox instance in the form of:
            {
                "id": str,
                "status": str (provisioning, initializing, running, failure,  shutdown),
                "create_time_ms": long
            }
        """
        async with AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/devboxes/{id}/shutdown",
                headers=self.headers,
            )
        return self._response_json(response)

    async def list_devboxes(self) -> dict[str, Any]:
        """
        List previously created devboxes.

        Returns:
            A list of devbox instances in the form of:
            {
                "devboxes: [
                    "id": str,
                    "status": str (provisioning, initializing, running, failure,  shutdown),
                    "create_time_ms": long
                ]
            }
        """
        async with AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v1/devboxes/",
                headers=self.headers,
            )
        return self._response_json(response)

    async def devbox_logs(self, id: str) -> dict[str, Any]:
        """
        Get logs from a particular devbox instance.

        Args:
            id: Id of the devbox instance.
        Returns:
            A devbox object of the following shape:
            {
                "logs: [
                    "message": str,
                    "level": str,
                    "timestamp_ms": long
                ]
            }
        """
        async with AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v1/devboxes/{id}/logs",
                headers=self.headers,
            )
        return self._response_json(response)

    def _response_json(self, response: Response) -> dict[str, Any]:
        try:
            response_json = response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing response: {e}")
            logger.error(
                f"Raw response: [status-{response.status_code}] {response.text}"
            )
            raise e

        return dict(response_json)
