import asyncio
import os
import shlex

COMMAND_TIMEOUT = 30
TIMEOUT_MESSAGE = f"Command timed out after {COMMAND_TIMEOUT} seconds"


async def execute_shell(code: str, working_directory: str) -> str:
    shell_path = os.environ.get("SHELL", None)
    full_command = code
    if shell_path:
        full_command = f"{shell_path} -i -c {shlex.quote(full_command)}"

    process = await asyncio.create_subprocess_shell(
        full_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=working_directory,
        start_new_session=True,
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
