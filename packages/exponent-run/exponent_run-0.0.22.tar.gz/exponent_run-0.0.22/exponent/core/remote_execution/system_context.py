import getpass
import os
import platform

from exponent.core.remote_execution.git import get_git_info
from exponent.core.remote_execution.languages import python
from exponent.core.remote_execution.types import (
    SystemContextRequest,
    SystemContextResponse,
    SystemInfo,
)


def get_system_context(
    request: SystemContextRequest, working_directory: str
) -> SystemContextResponse:
    return SystemContextResponse(
        correlation_id=request.correlation_id,
        exponent_txt=_read_exponent_txt(working_directory),
        system_info=get_system_info(working_directory),
    )


def get_system_info(working_directory: str) -> SystemInfo:
    return SystemInfo(
        name=getpass.getuser(),
        cwd=working_directory,
        os=platform.system(),
        shell=_get_user_shell(),
        git=get_git_info(working_directory),
        python_env=python.get_python_env_info(),
    )


def _read_exponent_txt(working_directory: str) -> str | None:
    file_path = os.path.join(working_directory, "exponent.txt")
    if os.path.exists(file_path):
        with open(file_path) as f:
            return f.read()
    return None


def _get_user_shell() -> str:
    return os.environ.get("SHELL", "bash")
