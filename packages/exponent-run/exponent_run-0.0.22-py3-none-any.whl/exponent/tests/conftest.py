import asyncio
import os
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pygit2
import pytest
from click.testing import CliRunner

from exponent.core.remote_execution.languages import python
from exponent.core.remote_execution.types import PythonEnvInfo
from exponent.tests.utils import create_commit, stage_file


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="session", autouse=True)
async def fixture_setup_env() -> None:
    session_mpatch = pytest.MonkeyPatch()
    session_mpatch.setenv("EXPONENT_API_KEY", "123456")
    session_mpatch.setenv("EXPONENT_BASE_URL", "https://exponent.run")
    session_mpatch.setenv("EXPONENT_API_BASE_URL", "https://api.exponent.run")


@pytest.fixture(scope="function")
def temporary_directory() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as test_directory:
        yield test_directory


@pytest.fixture(scope="function")
def temporary_directory_2() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as test_directory:
        yield test_directory


@pytest.fixture(scope="function")
def default_temporary_directory(
    temporary_directory: str, temporary_directory_2: str
) -> Generator[str, None, None]:
    with open(os.path.join(temporary_directory, "test1.py"), "w") as f:
        f.write("print('Hello, world!')")

    with open(os.path.join(temporary_directory, "test2.py"), "w") as f:
        f.write("print('Hello, world!')")

    with open(os.path.join(temporary_directory, "exponent.txt"), "w") as f:
        f.write("Hello, world!")

    symlink_path = os.path.join(temporary_directory_2, "symlink.txt")
    with open(symlink_path, "w") as f:
        f.write("Hello, world!")
    os.symlink(symlink_path, os.path.join(temporary_directory, "symlink.txt"))

    repo = pygit2.init_repository(temporary_directory, bare=False)

    stage_file(repo, "test1.py")
    stage_file(repo, "test2.py")
    stage_file(repo, "exponent.txt")
    create_commit(repo, "Initial commit", "Tester McTesterface", "test@example.com")

    yield temporary_directory


@pytest.fixture(scope="function")
def temporary_directory_no_commit_history(
    temporary_directory: str,
) -> Generator[str, None, None]:
    with open(os.path.join(temporary_directory, "test1.py"), "w") as f:
        f.write("print('Hello, world!')")

    with open(os.path.join(temporary_directory, "test2.py"), "w") as f:
        f.write("print('Hello, world!')")

    with open(os.path.join(temporary_directory, "exponent.txt"), "w") as f:
        f.write("Hello, world!")

    pygit2.init_repository(temporary_directory, bare=False)

    yield temporary_directory


@pytest.fixture(scope="function")
def temporary_directory_no_git(
    temporary_directory: str,
) -> Generator[str, None, None]:
    base_path = Path(temporary_directory)

    test1py = base_path / "test1.py"
    test1py.write_text("print('Hello, world!')")

    test2py = base_path / "test2.py"
    test2py.write_text("print('Hello, world!')")

    exptxt = base_path / "exponent.txt"
    exptxt.write_text("Hello, world!")

    file_in_ignored_pattern = Path(temporary_directory) / "test.pyc"
    file_in_ignored_pattern.write_text("Hello, world!")

    ignored_dir = Path(temporary_directory) / "node_modules"
    ignored_dir.mkdir(parents=True, exist_ok=True)

    file_in_ignored_dir = Path(temporary_directory) / "node_modules" / "nested.js"
    file_in_ignored_dir.write_text('console.log("Hello, world!");')

    not_ignored_dir = Path(temporary_directory) / "node_modules_not_ignored"
    not_ignored_dir.mkdir(parents=True, exist_ok=True)

    file_in_not_ignored_dir = (
        Path(temporary_directory) / "node_modules_not_ignored" / "test3.py"
    )
    file_in_not_ignored_dir.write_text('print("Hello, world!");')

    yield temporary_directory


@pytest.fixture(scope="function")
def temporary_directory_with_folder(
    temporary_directory: str,
) -> Generator[str, None, None]:
    base_path = Path(temporary_directory)

    test1py = base_path / "test1.py"
    test1py.write_text("print('Hello, world!')")

    test2py = base_path / "test2.py"
    test2py.write_text("print('Hello, world!')")

    exptxt = base_path / "exponent.txt"
    exptxt.write_text("Hello, world!")

    nested_path = Path(temporary_directory) / "nested"
    nested_path.mkdir(parents=True, exist_ok=True)

    nested_test1py = nested_path / "test1.py"
    nested_test1py.write_text("print('Hello, nested world!')")

    nested_test2py = nested_path / "test2.py"
    nested_test2py.write_text("print('Hello, nested world!')")

    nested_exptxt = nested_path / "exponent.txt"
    nested_exptxt.write_text("Hello, nested world!")

    repo = pygit2.init_repository(temporary_directory, bare=False)

    stage_file(repo, "test1.py")
    stage_file(repo, "test2.py")
    stage_file(repo, "exponent.txt")
    stage_file(repo, "nested/test1.py")
    stage_file(repo, "nested/test2.py")
    stage_file(repo, "nested/exponent.txt")
    create_commit(repo, "Initial commit", "Tester McTesterface", "test@example.com")

    yield temporary_directory


@pytest.fixture(scope="function", autouse=True)
def mock_cli_heartbeat() -> Generator[None, None, None]:
    patcher = patch(
        "exponent.core.remote_execution.client.RemoteExecutionClient.send_heartbeat"
    )
    patcher.start()
    yield
    patcher.stop()


@pytest.fixture(name="python_env_info", scope="function", autouse=True)
def fixture_python_env_info(
    monkeypatch: pytest.MonkeyPatch,
) -> PythonEnvInfo:
    env_info = PythonEnvInfo(
        interpreter_path="python",
        interpreter_version="3.11.0",
    )

    def get_python_env_info() -> PythonEnvInfo:
        return env_info

    monkeypatch.setattr(
        python,
        "get_python_env_info",
        get_python_env_info,
    )

    return env_info


@pytest.fixture(scope="function")
def temporary_directory_with_bigger_file(
    temporary_directory: str,
) -> Generator[str, None, None]:
    with open(os.path.join(temporary_directory, "test1.py"), "w") as f:
        f.write("""
def subtract(a: int, b: int) -> int:
    return a ++ b

def add(a: int, b: int) -> int:
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b
""")

    repo = pygit2.init_repository(temporary_directory, bare=False)

    stage_file(repo, "test1.py")
    create_commit(repo, "Initial commit", "Tester McTesterface", "test@example.com")

    yield temporary_directory
