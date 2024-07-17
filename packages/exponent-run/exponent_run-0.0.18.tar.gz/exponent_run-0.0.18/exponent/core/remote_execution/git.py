import os
from collections.abc import Callable
from pathlib import Path

import pygit2
from exponent.core.remote_execution.files import file_walk, normalize_files
from exponent.core.remote_execution.types import (
    GetAllTrackedFilesRequest,
    GetAllTrackedFilesResponse,
    GitInfo,
    RemoteFile,
)
from pygit2 import Repository, Tree


def get_all_tracked_files(
    request: GetAllTrackedFilesRequest,
    working_directory: str,
) -> GetAllTrackedFilesResponse:
    return GetAllTrackedFilesResponse(
        correlation_id=request.correlation_id,
        files=get_all_non_ignored_files(working_directory),
    )


def get_all_non_ignored_files(working_directory: str) -> list[RemoteFile]:
    ignore_extra = None
    if get_repo(working_directory) is None:
        # If we have no git repo then use a default
        # list of ignore patterns to avoid returning
        # a million files
        ignore_extra = DEFAULT_IGNORES
    file_paths = file_walk(working_directory, ignore_extra=ignore_extra)
    return normalize_files(working_directory, file_paths)


def get_repo(working_directory: str) -> Repository | None:
    try:
        return pygit2.Repository(working_directory)
    except pygit2.GitError:
        return None


def get_all_tracked_git_file_paths(
    repo: Repository, working_directory: str
) -> list[RemoteFile]:
    repo = pygit2.Repository(working_directory)
    files = get_tracked_files_in_dir(repo, working_directory)
    return normalize_files(working_directory, files)


def get_git_info(working_directory: str) -> GitInfo | None:
    try:
        repo = pygit2.Repository(working_directory)
    except pygit2.GitError:
        return None

    return GitInfo(
        branch=_get_git_branch(repo) or "<unknown branch>",
        remote=_get_git_remote(repo),
    )


def get_tracked_files_in_dir(
    repo: Repository, dir: str | Path, filter_func: Callable[[str], bool] | None = None
) -> list[str]:
    rel_path = get_path_relative_to_repo_root(repo, dir)
    dir_tree = get_git_subtree_for_dir(repo, dir)
    entries: list[str] = []
    if not dir_tree:
        return entries
    for entry in dir_tree:
        if not entry.name:
            continue
        entry_path = str(Path(f"{repo.workdir}/{rel_path}/{entry.name}"))
        if entry.type_str == "tree":
            entries.extend(get_tracked_files_in_dir(repo, entry_path, filter_func))
        elif entry.type_str == "blob":
            if not filter_func or filter_func(entry.name):
                entries.append(entry_path)
    return entries


def get_git_subtree_for_dir(repo: Repository, dir: str | Path) -> Tree | None:
    rel_path = get_path_relative_to_repo_root(repo, dir)

    try:
        head_commit = repo.head.peel()
    except pygit2.GitError:
        # If the repo is empty, then the head commit will not exist
        return None
    head_tree: Tree = head_commit.tree

    if rel_path == Path("."):
        # If the relative path is the root of the repo, then
        # the head_tree is what we want. Note we do this because
        # Passing "." or "" as the path into the tree will raise.
        return head_tree
    return head_tree[str(rel_path)]


def get_path_relative_to_repo_root(repo: Repository, path: str | Path) -> Path:
    path = Path(path).resolve()
    return path.relative_to(Path(repo.workdir).resolve())


def _get_git_remote(repo: pygit2.Repository) -> str | None:
    if repo.remotes:
        return str(repo.remotes[0].url)
    return None


def _get_git_branch(repo: pygit2.Repository) -> str | None:
    try:
        # Look for HEAD file in the .git directory
        head_path = os.path.join(repo.path, "HEAD")
        with open(head_path) as head_file:
            # The HEAD file content usually looks like: 'ref: refs/heads/branch_name'
            head_content = head_file.read().strip()
            if head_content.startswith("ref:"):
                return head_content.split("refs/heads/")[-1]
            else:
                return None
    except Exception:  # noqa: BLE001
        return None


DEFAULT_IGNORES = [
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    "venv",
    ".pyenv",
    "__pycache__",
    ".ipynb_checkpoints",
    ".vercel",
    "__pycache__/",
    "*.py[cod]",
    "*$py.class",
    ".env",
    "*.so",
    ".Python",
    "build/",
    "develop-eggs/",
    "dist/",
    "downloads/",
    "eggs/",
    ".eggs/",
    "lib/",
    "lib64/",
    "parts/",
    "sdist/",
    "var/",
    "wheels/",
    "pip-wheel-metadata/",
    "share/python-wheels/",
    "*.egg-info/",
    ".installed.cfg",
    "*.egg",
    "MANIFEST",
]
