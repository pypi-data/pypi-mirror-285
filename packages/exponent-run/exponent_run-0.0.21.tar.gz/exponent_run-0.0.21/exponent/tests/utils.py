import os

import pygit2


def initialize_repo(path: str) -> pygit2.Repository:
    if not os.path.exists(path):
        os.makedirs(path)
    return pygit2.init_repository(path, bare=False)


def stage_file(repo: pygit2.Repository, filepath: str) -> None:
    index = repo.index
    index.add(filepath)
    index.write()


def create_commit(
    repo: pygit2.Repository, message: str, author_name: str, author_email: str
) -> None:
    # Retrieve the index and check if it has changes
    index = repo.index
    if not index.write_tree():
        print("No changes to commit.")
        return

    # Get the tree object
    tree = index.write_tree()

    # Get the current HEAD. It could be a new repo without commits.
    try:
        parents = [repo.head.target]
    except pygit2.GitError:
        parents = []

    # Create the author and committer signatures
    author = pygit2.Signature(author_name, author_email)

    # Do the commit
    repo.create_commit(
        "refs/heads/master",  # the name of the reference to update
        author,  # the author of the commit
        author,  # the committer of the commit
        message,  # the commit message
        tree,  # the tree object this commit points to
        parents,  # parents of this commit (empty list for the first commit)
    )
