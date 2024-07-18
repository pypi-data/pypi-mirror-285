import asyncio
import logging
import queue
import re
import subprocess
import threading
import time
from typing import Any

from exponent.core.remote_execution.types import PythonEnvInfo
from jupyter_client.client import KernelClient
from jupyter_client.manager import KernelManager

logger = logging.getLogger(__name__)


class IOChannelHandler:
    ESCAPE_SEQUENCE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

    def __init__(self) -> None:
        self.output_buffer: queue.Queue[str] = queue.Queue()

    def add_message(self, message: dict[str, Any]) -> None:
        logger.debug(f"Jupter kernel message received: {message}")
        output = None
        if message["msg_type"] == "stream":
            output = message["content"]["text"]
        elif message["msg_type"] == "error":
            raw_content = "\n".join(message["content"]["traceback"])
            content = self.ESCAPE_SEQUENCE.sub("", raw_content)
            output = content
        if output:
            print(output)
            self.output_buffer.put(output)

    @staticmethod
    def is_idle(message: dict[str, Any]) -> bool:
        return bool(
            message["header"]["msg_type"] == "status"
            and message["content"]["execution_state"] == "idle"
        )


class Kernel:
    def __init__(self, working_directory: str) -> None:
        self._manager: KernelManager | None = None
        self._client: KernelClient | None = None
        self.io_handler: IOChannelHandler = IOChannelHandler()
        self.should_halt = False
        self.working_directory = working_directory

    @property
    def manager(self) -> KernelManager:
        if not self._manager:
            self._manager = KernelManager(kernel_name="python3")
            self._manager.start_kernel(cwd=self.working_directory)
        return self._manager

    @property
    def client(self) -> KernelClient:
        if not self._client:
            self._client = self.manager.client()
            self._client.start_channels()
        return self._client

    async def wait_for_ready(self, timeout: int = 5) -> None:
        manager = self.manager
        start_time = time.time()
        while not manager.is_alive():
            if time.time() - start_time > timeout:
                raise Exception("Kernel took too long to start")
            await asyncio.sleep(0.05)
        await asyncio.sleep(0.5)

    def iopub_listener(self, client: KernelClient) -> None:
        while True:
            if self.should_halt:
                logger.info("Received halt signal, stoping IO listener thread.")
                break
            try:
                msg = client.iopub_channel.get_msg(timeout=1)
                logger.debug(f"Received message from kernel: {msg}")
                self.io_handler.add_message(msg)
                if self.io_handler.is_idle(msg):
                    logger.debug("Kernel is idle, setting halt signal.")
                    self.should_halt = True
                    break
            except queue.Empty:
                continue
            except Exception as e:  # noqa: BLE001 - TODO: Deep audit potential exceptions
                logger.info(
                    f"Error getting message from kernel, halting io thread: {e}"
                )
                self.should_halt = True

    async def execute_code(self, code: str) -> str:
        # Make sure to clear this flag just in case
        self.should_halt = False
        # Grab the client and make sure it's ready
        await self.wait_for_ready()
        client = self.client
        client.connect_iopub()
        # Start separate thread for buffering kernel output
        iopub_thread = threading.Thread(target=self.iopub_listener, args=(client,))
        logger.info("Starting IO listener thread.")
        iopub_thread.start()

        logger.info("Executing code in kernel.")
        client.execute(code)

        results = []
        while True:
            if not self.io_handler.output_buffer.empty():
                output = self.io_handler.output_buffer.get()
                logger.info("Execution output: %s", output)
                results.append(output)
            if self.should_halt:
                break
            await asyncio.sleep(0.05)

        return "\n".join(results)

    def close(self) -> None:
        if self._client:
            self._client.stop_channels()
            self._client = None
        if self._manager:
            self._manager.shutdown_kernel()
            self._manager = None


async def execute_python(code: str, kernel: Kernel) -> str:
    return await kernel.execute_code(code)


### Environment Helpers


def get_python_env_info() -> PythonEnvInfo:
    return PythonEnvInfo(
        interpreter_path=get_active_python_interpreter_path(),
        interpreter_version=get_active_python_interpreter_version(),
    )


def get_active_python_interpreter_path() -> str | None:
    # Run the command `which python`
    result = subprocess.run(
        ["which", "python"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def get_active_python_interpreter_version() -> str | None:
    try:
        # Run the command `python -V`
        result = subprocess.run(
            ["python", "-V"], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        # Python is not installed?
        return None
    # Capture the standard output and standard error
    stdout = result.stdout.strip()
    match = re.search(r"Python (\d+\.\d+\.\d+)", stdout)
    if match:
        return match.group(1)
    return None
