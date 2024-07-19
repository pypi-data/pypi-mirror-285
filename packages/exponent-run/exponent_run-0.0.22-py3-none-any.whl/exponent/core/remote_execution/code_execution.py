from exponent.core.remote_execution.languages.python import execute_python
from exponent.core.remote_execution.languages.shell import execute_shell
from exponent.core.remote_execution.session import RemoteExecutionClientSession
from exponent.core.remote_execution.types import (
    CodeExecutionRequest,
    CodeExecutionResponse,
)
from exponent.core.remote_execution.utils import assert_unreachable


async def execute_code(
    request: CodeExecutionRequest,
    session: RemoteExecutionClientSession,
    working_directory: str,
) -> CodeExecutionResponse:
    try:
        if request.language == "python":
            result = await execute_python(request.content, session.kernel)
        elif request.language == "shell":
            result = await execute_shell(request.content, working_directory)
        else:
            return assert_unreachable(request.language)
        if not result:
            result = "<No output>"
        return CodeExecutionResponse(
            content=result,
            correlation_id=request.correlation_id,
        )
    except Exception as e:  # noqa: BLE001 - TODO (Josh): Specialize errors for execution
        return CodeExecutionResponse(
            content="An error occurred while executing the code: " + str(e),
            correlation_id=request.correlation_id,
        )
