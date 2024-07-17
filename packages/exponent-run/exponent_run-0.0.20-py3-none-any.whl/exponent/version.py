import os

import click
import toml


def file_relative_path(dunderfile: str, relative_path: str) -> str:
    """Get a path relative to the currently executing Python file."""
    return os.path.join(os.path.dirname(dunderfile), relative_path)


def get_version() -> str:
    try:
        pyproject_path = file_relative_path(__file__, "../pyproject.toml")

        if not os.path.exists(pyproject_path):
            click.echo(
                f"pyproject.toml not found at {os.path.abspath(pyproject_path)}",
                err=True,
            )
            return "unknown"

        with open(pyproject_path) as pyproject_file:
            pyproject_data = toml.load(pyproject_file)

        version = pyproject_data.get("tool", {}).get("poetry", {}).get("version")
        return str(version) if version is not None else "unknown"
    except (OSError, toml.TomlDecodeError) as e:
        click.echo(f"Error reading version: {e}", err=True)
        return "unknown"
