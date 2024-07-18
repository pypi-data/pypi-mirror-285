import os
from importlib.metadata import Distribution, PackageNotFoundError

import click


def file_relative_path(dunderfile: str, relative_path: str) -> str:
    """Get a path relative to the currently executing Python file."""
    return os.path.join(os.path.dirname(dunderfile), relative_path)


def get_version() -> str:
    try:
        return Distribution.from_name("exponent-run").version
    except PackageNotFoundError as e:
        click.echo(f"Error reading version: {e}", err=True)
        return "unknown"
