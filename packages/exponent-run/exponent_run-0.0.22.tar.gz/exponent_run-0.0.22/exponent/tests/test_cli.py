import getpass
import os
import platform
from pathlib import Path
from unittest import mock
from unittest.mock import mock_open

import pytest
from click.testing import CliRunner

from exponent.cli import login
from exponent.core.remote_execution import files, git
from exponent.core.remote_execution.client import RemoteExecutionClient
from exponent.core.remote_execution.languages.python import Kernel, get_python_env_info
from exponent.core.remote_execution.system_context import get_system_context
from exponent.core.remote_execution.types import (
    FileWriteRequest,
    FileWriteResponse,
    GetAllTrackedFilesRequest,
    GetAllTrackedFilesResponse,
    GetFileAttachmentRequest,
    GetFileAttachmentResponse,
    GetMatchingFilesRequest,
    GetMatchingFilesResponse,
    GitInfo,
    ListFilesRequest,
    PythonEnvInfo,
    RemoteFile,
    SystemContextRequest,
    SystemContextResponse,
    SystemInfo,
)


@pytest.mark.skip
async def test_exponent_login(cli_runner: CliRunner) -> None:
    with mock.patch("builtins.open", new_callable=mock_open):
        result = cli_runner.invoke(
            login, ["--key", "123456"], env={"EXPONENT_API_KEY": "123456"}
        )
        assert result.exit_code == 0
        assert "Saving API Key" in result.output


async def test_list_files(default_temporary_directory: str) -> None:
    request = ListFilesRequest(
        correlation_id="123456", directory=default_temporary_directory
    )

    response = files.list_files(request)

    assert response.correlation_id == "123456"
    assert sorted(response.files) == [
        RemoteFile(
            file_path=".git",
            working_directory=default_temporary_directory,
        ),
        RemoteFile(
            file_path="exponent.txt",
            working_directory=default_temporary_directory,
        ),
        RemoteFile(
            file_path="symlink.txt",
            working_directory=default_temporary_directory,
        ),
        RemoteFile(
            file_path="test1.py",
            working_directory=default_temporary_directory,
        ),
        RemoteFile(
            file_path="test2.py",
            working_directory=default_temporary_directory,
        ),
    ]


async def test_get_system_context(
    default_temporary_directory: str, python_env_info: PythonEnvInfo
) -> None:
    request = SystemContextRequest(correlation_id="123456")

    response = get_system_context(request, default_temporary_directory)

    assert response == SystemContextResponse(
        correlation_id="123456",
        exponent_txt="Hello, world!",
        system_info=SystemInfo(
            name=getpass.getuser(),
            cwd=default_temporary_directory,
            shell=os.environ.get("SHELL", "bash"),
            os=platform.system(),
            git=GitInfo(branch="master", remote=None),
            python_env=python_env_info,
        ),
    )


async def test_get_file_attachment(default_temporary_directory: str) -> None:
    request = GetFileAttachmentRequest(
        correlation_id="123456",
        file=RemoteFile(
            file_path="test1.py",
            working_directory=default_temporary_directory,
        ),
    )

    response = files.get_file_attachment(request)

    assert response == GetFileAttachmentResponse(
        correlation_id="123456",
        file=RemoteFile(
            file_path="test1.py",
            working_directory=default_temporary_directory,
        ),
        content="print('Hello, world!')",
    )


async def test_get_matching_files(default_temporary_directory: str) -> None:
    request1 = GetMatchingFilesRequest(correlation_id="123456", search_term="tes")
    request2 = GetMatchingFilesRequest(correlation_id="123456", search_term="test1")

    response1 = files.get_matching_files(
        request1, files.FileCache(default_temporary_directory)
    )

    assert response1.correlation_id == "123456"

    assert sorted(response1.files) == [
        RemoteFile(
            file_path="exponent.txt",
            working_directory=default_temporary_directory,
        ),
        RemoteFile(
            file_path="test1.py",
            working_directory=default_temporary_directory,
        ),
        RemoteFile(
            file_path="test2.py",
            working_directory=default_temporary_directory,
        ),
    ]

    response2 = files.get_matching_files(
        request2, files.FileCache(default_temporary_directory)
    )

    assert response2.correlation_id == "123456"

    assert sorted(response2.files) == [
        RemoteFile(
            file_path="exponent.txt",
            working_directory=default_temporary_directory,
        ),
        RemoteFile(
            file_path="test1.py",
            working_directory=default_temporary_directory,
        ),
        RemoteFile(
            file_path="test2.py",
            working_directory=default_temporary_directory,
        ),
    ]


async def test_get_matching_files_nested(temporary_directory: str) -> None:
    # Setup test directory to look like this:
    # /folder
    #   /subfolder
    #     test1.py
    #     test2.py
    # /main
    #   core.java
    # random.tsx
    # .env
    # .gitignore (contains .env ignored)

    # Test queries for:
    # .env
    # random
    # test1
    # test2
    # .tsx
    # mjava
    import os

    # Create the necessary files and folders in the temporary directory
    os.makedirs(os.path.join(temporary_directory, "folder", "subfolder"))
    os.makedirs(os.path.join(temporary_directory, "main"))

    with open(
        os.path.join(temporary_directory, "folder", "subfolder", "test1.py"),
        "w",
    ) as f:
        f.write("# test1.py")

    with open(
        os.path.join(temporary_directory, "folder", "subfolder", "test2.py"),
        "w",
    ) as f:
        f.write("# test2.py")

    with open(os.path.join(temporary_directory, "main", "core.java"), "w") as f:
        f.write("// core.java")

    with open(os.path.join(temporary_directory, "random.tsx"), "w") as f:
        f.write("// random.tsx")

    with open(os.path.join(temporary_directory, ".env"), "w") as f:
        f.write("SECRET_KEY=123456")

    with open(os.path.join(temporary_directory, ".gitignore"), "w") as f:
        f.write(".env")

    # Test queries for various search terms
    test_cases = [
        # ("tes", ["folder/subfolder/test1.py", "folder/subfolder/test2.py"]),
        ("random", ["random.tsx"]),
        (".env", []),
        ("core", ["main/core.java"]),
        (".tsx", ["random.tsx"]),
        ("java", ["main/core.java"]),
        ("nonexistent", []),
        ("folder", ["folder/subfolder/test1.py", "folder/subfolder/test2.py"]),
        ("subfolder", ["folder/subfolder/test1.py", "folder/subfolder/test2.py"]),
        ("test1", ["folder/subfolder/test1.py"]),
        ("test2", ["folder/subfolder/test2.py"]),
    ]

    for search_term, _ in test_cases:
        request = GetMatchingFilesRequest(
            correlation_id="123456", search_term=search_term
        )

        response = files.get_matching_files(
            request, files.FileCache(temporary_directory)
        )

        assert isinstance(response, GetMatchingFilesResponse)
        assert response.correlation_id == "123456"


@pytest.mark.skip
async def test_python_kernel() -> None:
    kernel = Kernel(os.getcwd())
    result = await kernel.execute_code("print('Hello, world!')")
    assert result == "Hello, world!\n"


async def test_execute_code_diff(tmpdir: Path) -> None:
    os.chdir(tmpdir)

    request = FileWriteRequest(
        correlation_id="123456",
        file_path="echo_server.py",
        language="python",
        write_strategy="FULL_FILE_REWRITE",
        content='from fastapi import FastAPI\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\nclass Message(BaseModel):\n    content: str\n\n@app.get("/echo")\ndef echo(message: Message):\n    return {"Echo": message.content}\n\nif __name__ == "__main__":\n    import uvicorn\n    uvicorn.run(app, host="127.0.0.1", port=8000)\n',
    )

    async with RemoteExecutionClient.session(
        api_key="123456",
        base_url="https://example.com",
        working_directory=str(tmpdir),
    ) as client:
        response = await client.handle_request(request)

        assert response == FileWriteResponse(
            correlation_id="123456", content="Created file echo_server.py"
        )

        with open("echo_server.py") as f:
            contents = f.read()
        assert (
            contents
            == 'from fastapi import FastAPI\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\nclass Message(BaseModel):\n    content: str\n\n@app.get("/echo")\ndef echo(message: Message):\n    return {"Echo": message.content}\n\nif __name__ == "__main__":\n    import uvicorn\n    uvicorn.run(app, host="127.0.0.1", port=8000)\n'
        )


async def test_get_all_tracked_files(temporary_directory_with_folder: str) -> None:
    request = GetAllTrackedFilesRequest(correlation_id="123456")

    response = git.get_all_tracked_files(request, temporary_directory_with_folder)

    assert response == GetAllTrackedFilesResponse(
        correlation_id="123456",
        files=[
            RemoteFile(
                file_path="exponent.txt",
                working_directory=temporary_directory_with_folder,
            ),
            RemoteFile(
                file_path="nested/exponent.txt",
                working_directory=temporary_directory_with_folder,
            ),
            RemoteFile(
                file_path="nested/test1.py",
                working_directory=temporary_directory_with_folder,
            ),
            RemoteFile(
                file_path="nested/test2.py",
                working_directory=temporary_directory_with_folder,
            ),
            RemoteFile(
                file_path="test1.py",
                working_directory=temporary_directory_with_folder,
            ),
            RemoteFile(
                file_path="test2.py",
                working_directory=temporary_directory_with_folder,
            ),
        ],
    )

    response = git.get_all_tracked_files(
        request, f"{temporary_directory_with_folder}/nested"
    )

    assert response == GetAllTrackedFilesResponse(
        correlation_id="123456",
        files=[
            RemoteFile(
                file_path="nested/exponent.txt",
                working_directory=temporary_directory_with_folder,
            ),
            RemoteFile(
                file_path="nested/test1.py",
                working_directory=temporary_directory_with_folder,
            ),
            RemoteFile(
                file_path="nested/test2.py",
                working_directory=temporary_directory_with_folder,
            ),
        ],
    )


def test_get_python_env_info() -> None:
    venv_info = get_python_env_info()
    assert venv_info.interpreter_path
    assert venv_info.interpreter_version
    assert venv_info.interpreter_path.endswith("python")
    assert venv_info.interpreter_version == platform.python_version()
