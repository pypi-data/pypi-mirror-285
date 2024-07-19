import os

from exponent.core.remote_execution.file_write import (
    execute_search_replace_edit,
    execute_udiff_edit,
)
from exponent.core.remote_execution.languages.shell import execute_shell


async def test_execute_shell(default_temporary_directory: str) -> None:
    output = await execute_shell(
        code="ls -1v", working_directory=default_temporary_directory
    )
    output_lines = output.strip().split("\n")
    expected_lines = 4
    assert len(output_lines) == expected_lines
    assert output_lines == [
        "exponent.txt",
        "symlink.txt",
        "test1.py",
        "test2.py",
    ]

    output = await execute_shell(
        code="true && echo 'hi' || echo \"boo\"",
        working_directory=default_temporary_directory,
    )

    assert output.strip() == "hi"


async def test_execute_udiff(temporary_directory_with_bigger_file: str) -> None:
    diff = (
        "@@ ... @@\n"
        " def subtract(a: int, b: int) -> int:\n"
        "-    return a ++ b\n"
        "+    return a - b\n"
        " \n"
        " def add(a: int, b: int) -> int:\n"
    )
    execute_udiff_edit(
        file_path="test1.py",
        content=diff,
        working_directory=temporary_directory_with_bigger_file,
    )

    contents = None
    with open(os.path.join(temporary_directory_with_bigger_file, "test1.py")) as f:
        contents = f.read()

    assert (
        contents
        == """
def subtract(a: int, b: int) -> int:
    return a - b

def add(a: int, b: int) -> int:
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b
"""
    )


async def test_execute_udiff_fuzzy(temporary_directory_with_bigger_file: str) -> None:
    diff = (
        "@@ ... @@\n"
        " def subtract(a: int, b: int) -> int:\n"
        "-    return a ++ b\n"
        "+    return a - b\n"
        " def add(a: int, b: int) -> int:\n"
    )
    execute_udiff_edit(
        file_path="test1.py",
        content=diff,
        working_directory=temporary_directory_with_bigger_file,
    )

    contents = None
    with open(os.path.join(temporary_directory_with_bigger_file, "test1.py")) as f:
        contents = f.read()

    assert (
        contents
        == """
def subtract(a: int, b: int) -> int:
    return a - b

def add(a: int, b: int) -> int:
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b
"""
    )


async def test_execute_search_replace(
    temporary_directory_with_bigger_file: str,
) -> None:
    diff = (
        "<<<<< SEARCH\n"
        "def subtract(a: int, b: int) -> int:\n"
        "    return a ++ b\n"
        "======\n"
        "def subtract(a: int, b: int) -> int:\n"
        "    return a - b\n"
        ">>>>>> REPLACE\n"
    )
    execute_search_replace_edit(
        file_path="test1.py",
        content=diff,
        working_directory=temporary_directory_with_bigger_file,
    )

    contents = None
    with open(os.path.join(temporary_directory_with_bigger_file, "test1.py")) as f:
        contents = f.read()

    assert (
        contents
        == """
def subtract(a: int, b: int) -> int:
    return a - b

def add(a: int, b: int) -> int:
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b
"""
    )


async def test_execute_search_replace_fuzzy(
    temporary_directory_with_bigger_file: str,
) -> None:
    diff = (
        "<<<<SEARCH\n"
        "def subtract(a: int, b: int) -> int:\n"
        "    return a ++ b\n"
        "======\n"
        "def subtract(a: int, b: int) -> int:\n"
        "    return a - b\n"
        ">>>>>>>>>> REPLACE\n"
    )
    execute_search_replace_edit(
        file_path="test1.py",
        content=diff,
        working_directory=temporary_directory_with_bigger_file,
    )

    contents = None
    with open(os.path.join(temporary_directory_with_bigger_file, "test1.py")) as f:
        contents = f.read()

    assert (
        contents
        == """
def subtract(a: int, b: int) -> int:
    return a - b

def add(a: int, b: int) -> int:
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b
"""
    )
