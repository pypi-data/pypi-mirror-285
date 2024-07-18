import asyncio
import os
import shutil

COMMAND_TIMEOUT = 30
TIMEOUT_MESSAGE = f"Command timed out after {COMMAND_TIMEOUT} seconds"


async def execute_shell(code: str, working_directory: str) -> str:
    shell_path = (
        os.environ.get("SHELL")
        or shutil.which("bash")
        or shutil.which("sh")
        or "/bin/sh"
    )

    process = await asyncio.create_subprocess_exec(
        shell_path,
        "-l",
        "-c",
        code,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=working_directory,
    )
    try:
        coro = process.communicate()
        stdout_data, stderr_data = await asyncio.wait_for(coro, COMMAND_TIMEOUT)
    except (TimeoutError, asyncio.TimeoutError):  # noqa: UP041
        process.kill()
        return TIMEOUT_MESSAGE
    decoded_stdout = stdout_data.decode()
    decoded_stderr = stderr_data.decode()
    output = []
    if decoded_stdout:
        output.append(decoded_stdout)
    if decoded_stderr:
        output.append(decoded_stderr)
    shell_output = "\n".join(output)
    return shell_output
