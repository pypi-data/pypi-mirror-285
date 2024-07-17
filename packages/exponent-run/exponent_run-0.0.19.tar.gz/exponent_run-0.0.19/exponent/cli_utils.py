import os
import subprocess
import sys
from importlib.metadata import Distribution, PackageNotFoundError
from json import JSONDecodeError

import click
import httpx
from packaging.version import Version

from exponent.core.config import Environment, ExponentCloudConfig, Settings


def print_editable_install_forced_prod_warning(settings: Settings) -> None:
    click.secho(
        "Detected local editable install, but this command only works against prod.",
        fg="red",
        bold=True,
    )
    click.secho("Using prod settings:", fg="red", bold=True)
    click.secho("- base_url=", fg="yellow", bold=True, nl=False)
    click.secho(f"{settings.base_url}", fg=(100, 200, 255), bold=False)
    click.secho("- base_api_url=", fg="yellow", bold=True, nl=False)
    click.secho(f"{settings.base_api_url}", fg=(100, 200, 255), bold=False)
    click.secho()


def print_editable_install_warning(settings: Settings) -> None:
    click.secho(
        "Detected local editable install, using local URLs", fg="yellow", bold=True
    )
    click.secho("- base_url=", fg="yellow", bold=True, nl=False)
    click.secho(f"{settings.base_url}", fg=(100, 200, 255), bold=False)
    click.secho("- base_api_url=", fg="yellow", bold=True, nl=False)
    click.secho(f"{settings.base_api_url}", fg=(100, 200, 255), bold=False)
    click.secho()


def print_exponent_message(base_url: str, chat_uuid: str) -> None:
    click.echo()
    click.secho("△ Exponent v1.0.0", fg=(180, 150, 255), bold=True)
    click.echo()
    click.echo(
        " - Link: " + click.style(f"{base_url}/chats/{chat_uuid}", fg=(100, 200, 255))
    )
    click.echo(click.style("  - Shell: /bin/zsh", fg="white"))
    click.echo()
    click.echo(click.style("✓", fg="green", bold=True) + " Ready in 1401ms")


def is_exponent_app_installed() -> bool:
    if sys.platform == "darwin":  # macOS
        return os.path.exists("/Applications/Exponent.app")

    # TODO: Add support for Windows and Linux
    return False


def launch_exponent_browser(
    environment: Environment, base_url: str, chat_uuid: str
) -> None:
    if is_exponent_app_installed() and environment == Environment.production:
        url = f"exponent://chats/{chat_uuid}"
    else:
        url = f"{base_url}/chats/{chat_uuid}"
    click.launch(url)


def write_template_exponent_cloud_config(file_path: str) -> None:
    exponent_cloud_config = ExponentCloudConfig(
        repo_name="your_repo_name",
        repo_specific_setup_commands=[
            "cd /home/user",
            "gh repo clone https://github.com/<org>/<repo>.git",
            "cd <repo>",
            "# Any additional setup commands",
        ],
        gh_token="ghp_your_token_here",
        runloop_api_key="ak_your_runloop_api_key_here",
    )
    with open(file_path, "w") as f:
        f.write(exponent_cloud_config.model_dump_json(indent=2))


def get_exponent_version_for_update() -> str | None:
    """
    Check if there's a newer version of Exponent available on PyPI.
    """
    try:
        dist = Distribution.from_name("exponent-run")
    except PackageNotFoundError:
        return None
    installed_version = dist.version

    try:
        pypi_package_info = httpx.get("https://pypi.org/pypi/exponent-run/json").json()
    except (httpx.ConnectError, JSONDecodeError):
        return None
    pypi_version = pypi_package_info.get("info", {}).get("version")

    if not pypi_version or not installed_version:
        # If we can't get the concrete version info,
        # we can't tell if it's outdated
        return None
    elif Version(pypi_version) > Version(installed_version):
        return str(pypi_version)
    return None


def check_exponent_version() -> None:
    """
    Print a message to the user if there's a newer
    version of Exponent available on PyPI.
    """
    version = get_exponent_version_for_update()
    if not version:
        return

    upgrade_command = ["pip", "install", "--upgrade", "exponent-run"]
    click.secho(
        f"New version available: exponent-run=={version}\n"
        f"Update command: `{' '.join(upgrade_command)}`",
        fg="yellow",
        bold=True,
    )
    confirmed = click.confirm("Update now?", default=True, show_default=True)
    if not confirmed:
        click.secho("Not updating.", fg="red")
        return

    click.secho("Updating...", bold=True, fg="yellow")
    subprocess.check_call(upgrade_command)
    invoking_command = subprocess.list2cmdline(["exponent", *sys.argv[1:]])
    click.secho(
        "\nUpdate complete! Please re-run command: ",
        fg="green",
        nl=False,
    )
    click.secho(
        invoking_command,
        bold=True,
    )
    sys.exit(0)
