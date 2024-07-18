import json
from collections.abc import AsyncIterable
from typing import NoReturn, TypeGuard, TypeVar, cast, overload

from exponent.core.remote_execution.types import (
    CLIErrorLog,
    CodeExecutionRequest,
    CodeExecutionResponse,
    FileWriteRequest,
    FileWriteResponse,
    GetAllTrackedFilesRequest,
    GetAllTrackedFilesResponse,
    GetFileAttachmentRequest,
    GetFileAttachmentResponse,
    GetMatchingFilesRequest,
    GetMatchingFilesResponse,
    ListFilesRequest,
    ListFilesResponse,
    RemoteExecutionMessage,
    RemoteExecutionMessageData,
    RemoteExecutionRequest,
    RemoteExecutionRequestData,
    RemoteExecutionRequestType,
    RemoteExecutionResponse,
    RemoteExecutionResponseData,
    RemoteExecutionResponseType,
    SystemContextRequest,
    SystemContextResponse,
)
from httpx import Response
from pydantic import BaseModel
from sentry_sdk.serializer import serialize
from sentry_sdk.utils import (
    event_from_exception,
    exc_info_from_error,
)

### Serde


def deserialize_message_data(
    message_data: RemoteExecutionMessageData | str,
) -> RemoteExecutionMessage:
    if isinstance(message_data, str):
        message_data = RemoteExecutionMessageData.model_validate_json(message_data)
    if message_data.direction == "request":
        return deserialize_request_data(cast(RemoteExecutionRequestData, message_data))
    elif message_data.direction == "response":
        return deserialize_response_data(
            cast(RemoteExecutionResponseData, message_data)
        )
    else:
        # type checking trick, if you miss a namespace then
        # this won't typecheck due to the input parameter
        # having a potential type other than no-return
        assert_unreachable(message_data.direction)


def deserialize_request_data(
    request_data: RemoteExecutionRequestData | str,
) -> RemoteExecutionRequestType:
    request: RemoteExecutionRequestType
    if isinstance(request_data, str):
        request_data = RemoteExecutionRequestData.model_validate_json(request_data)
    if request_data.direction != "request":
        raise ValueError(f"Expected request, but got {request_data.direction}")
    if request_data.namespace == "code_execution":
        request = CodeExecutionRequest.model_validate_json(request_data.message_data)
    elif request_data.namespace == "file_write":
        request = FileWriteRequest.model_validate_json(request_data.message_data)
    elif request_data.namespace == "list_files":
        request = ListFilesRequest.model_validate_json(request_data.message_data)
    elif request_data.namespace == "get_file_attachment":
        request = GetFileAttachmentRequest.model_validate_json(
            request_data.message_data
        )
    elif request_data.namespace == "get_matching_files":
        request = GetMatchingFilesRequest.model_validate_json(request_data.message_data)
    elif request_data.namespace == "system_context":
        request = SystemContextRequest.model_validate_json(request_data.message_data)
    elif request_data.namespace == "get_all_tracked_files":
        request = GetAllTrackedFilesRequest.model_validate_json(
            request_data.message_data
        )
    else:
        # type checking trick, if you miss a namespace then
        # this won't typecheck due to the input parameter
        # having a potential type other than no-return
        request = assert_unreachable(request_data.namespace)
    return truncate_message(request)


def deserialize_response_data(
    response_data: RemoteExecutionResponseData | str,
) -> RemoteExecutionResponseType:
    response: RemoteExecutionResponseType
    if isinstance(response_data, str):
        response_data = RemoteExecutionResponseData.model_validate_json(response_data)
    if response_data.direction != "response":
        raise ValueError(f"Expected response, but got {response_data.direction}")
    if response_data.namespace == "code_execution":
        response = CodeExecutionResponse.model_validate_json(response_data.message_data)
    elif response_data.namespace == "file_write":
        response = FileWriteResponse.model_validate_json(response_data.message_data)
    elif response_data.namespace == "list_files":
        response = ListFilesResponse.model_validate_json(response_data.message_data)
    elif response_data.namespace == "get_matching_files":
        response = GetMatchingFilesResponse.model_validate_json(
            response_data.message_data
        )
    elif response_data.namespace == "get_file_attachment":
        response = GetFileAttachmentResponse.model_validate_json(
            response_data.message_data
        )
    elif response_data.namespace == "system_context":
        response = SystemContextResponse.model_validate_json(response_data.message_data)
    elif response_data.namespace == "get_all_tracked_files":
        response = GetAllTrackedFilesResponse.model_validate_json(
            response_data.message_data
        )
    else:
        # type checking trick, if you miss a namespace then
        # this won't typecheck due to the input parameter
        # having a potential type other than no-return
        response = assert_unreachable(response_data.namespace)
    return truncate_message(response)


def serialize_message(response: RemoteExecutionMessage) -> str:
    truncated_response = truncate_message(response)
    message = RemoteExecutionMessageData(
        namespace=response.namespace,
        direction=response.direction,
        message_data=truncated_response.model_dump_json(),
    )
    return message.model_dump_json()


### API Serde


TModel = TypeVar("TModel", bound=BaseModel)


async def deserialize_list_api_response(
    response_data: Response,
) -> list[RemoteExecutionRequestType]:
    response_json = response_data.json()
    results = []
    for result in response_json:
        results.append(deserialize_request_data(result))
    return results


async def deserialize_api_response(
    response: Response,
    data_model: type[TModel],
) -> TModel:
    response_json = response.json()
    return data_model.model_validate(response_json)


### Validation


ResponseT = TypeVar("ResponseT", bound=RemoteExecutionResponse)


def response_type_is_valid_for_request(
    response: RemoteExecutionResponseType, request: RemoteExecutionRequest[ResponseT]
) -> TypeGuard[ResponseT]:
    if request.namespace != response.namespace or response.direction != "response":
        raise ValueError(
            f"Expected {request.namespace}.response, but got {response.namespace}.{response.direction}"
        )
    return True


def assert_unreachable(x: NoReturn) -> NoReturn:
    assert False, f"Unhandled type: {type(x).__name__}"


### Truncation


OUTPUT_CHARACTER_MAX = 30_000
TRUNCATION_MESSAGE_CHARS = (
    "(Output truncated, only showing the first {remaining_chars} characters)"
)
TRUNCATION_MESSAGE_LINES = (
    "(Output truncated, only showing the first {remaining_lines} lines)"
)
LONGEST_TRUNCATION_MESSAGE_LEN = (
    len(TRUNCATION_MESSAGE_CHARS.format(remaining_chars=OUTPUT_CHARACTER_MAX)) + 1
)


def truncate_output(output: str, character_limit: int = OUTPUT_CHARACTER_MAX) -> str:
    output_length = len(output)
    # When under the character limit, return the output as is.
    # Note we're adding the length of the truncation message + 1
    # to the character limit to account for the fact that the
    # truncation message will be added to the output + a newline.
    # In case we want to run truncation logic both client side
    # and server side, we want to account for the truncation
    # message length to avoid weird double truncation overlap.
    if output_length <= character_limit + LONGEST_TRUNCATION_MESSAGE_LEN:
        return output

    # Attempt to trim whole lines until we're under
    # the character limit.
    lines = output.split("\n")
    while output_length > character_limit:
        last_line = lines.pop()
        # +1 to account for the newline
        output_length -= len(last_line) + 1

    if not lines:
        # If we truncated all the lines, then we have
        # have some ridiculous long line at the start
        # of the output so we'll just truncate by
        # character count to retain something.
        output = output[:character_limit]
        # Format the truncation message accordingly
        truncation_message = TRUNCATION_MESSAGE_CHARS.format(
            remaining_chars=character_limit,
        )
    else:
        # Otherwise, just join the lines back together
        output = "\n".join(lines)
        truncation_message = TRUNCATION_MESSAGE_LINES.format(
            remaining_lines=len(lines),
        )

    return f"{output}\n{truncation_message}"


@overload
def truncate_message(response: CodeExecutionRequest) -> CodeExecutionRequest: ...
@overload
def truncate_message(response: CodeExecutionResponse) -> CodeExecutionResponse: ...
@overload
def truncate_message(response: FileWriteRequest) -> FileWriteRequest: ...
@overload
def truncate_message(response: FileWriteResponse) -> FileWriteResponse: ...
@overload
def truncate_message(
    response: GetFileAttachmentRequest,
) -> GetFileAttachmentRequest: ...
@overload
def truncate_message(
    response: GetFileAttachmentResponse,
) -> GetFileAttachmentResponse: ...
@overload
def truncate_message(response: ListFilesRequest) -> ListFilesRequest: ...
@overload
def truncate_message(response: ListFilesResponse) -> ListFilesResponse: ...
@overload
def truncate_message(response: GetMatchingFilesRequest) -> GetMatchingFilesRequest: ...
@overload
def truncate_message(
    response: GetMatchingFilesResponse,
) -> GetMatchingFilesResponse: ...
@overload
def truncate_message(response: SystemContextRequest) -> SystemContextRequest: ...
@overload
def truncate_message(response: SystemContextResponse) -> SystemContextResponse: ...
@overload
def truncate_message(
    response: RemoteExecutionRequestType,
) -> RemoteExecutionRequestType: ...
@overload
def truncate_message(
    response: RemoteExecutionResponseType,
) -> RemoteExecutionResponseType: ...
@overload
def truncate_message(response: RemoteExecutionMessage) -> RemoteExecutionMessage: ...


def truncate_message(
    response: RemoteExecutionMessage,
) -> RemoteExecutionMessage:
    if isinstance(response, CodeExecutionResponse | GetFileAttachmentResponse):
        response.content = truncate_output(response.content)
    return response


### Error Handling


def format_attachment_data(attachment_lines: list[str] | None = None) -> str | None:
    if not attachment_lines:
        return None
    log_attachment_str = "\n".join(attachment_lines)
    return log_attachment_str


def format_error_log(
    exc: Exception,
    attachment_lines: list[str] | None = None,
) -> CLIErrorLog | None:
    exc_info = exc_info_from_error(exc)
    event, _ = event_from_exception(exc_info)
    attachment_data = format_attachment_data(attachment_lines)
    try:
        event_data = json.dumps(serialize(event))
    except json.JSONDecodeError:
        return None
    return CLIErrorLog(event_data=event_data, attachment_data=attachment_data)


### Misc


T = TypeVar("T")


async def aenumerate(async_iter: AsyncIterable[T]) -> AsyncIterable[tuple[int, T]]:
    i = 0
    async for item in async_iter:
        yield i, item
        i += 1
