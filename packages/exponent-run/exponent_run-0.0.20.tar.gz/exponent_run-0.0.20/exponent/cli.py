import _thread
import asyncio
import json
import logging
import os
import sys
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

import click
import httpx
from dotenv import load_dotenv
from pydantic import ValidationError

from exponent.cli_utils import (
    check_exponent_version,
    launch_exponent_browser,
    print_editable_install_forced_prod_warning,
    print_editable_install_warning,
    print_exponent_message,
    write_template_exponent_cloud_config,
)
from exponent.core.config import (
    Environment,
    ExponentCloudConfig,
    Settings,
    get_settings,
    is_editable_install,
)
from exponent.core.remote_execution.client import RemoteExecutionClient
from exponent.core.remote_execution.exceptions import ExponentError
from exponent.core.remote_execution.types import (
    RemoteExecutionRequestType,
    RemoteExecutionResponse,
    UseToolsConfig,
)
from exponent.core.runloop import RunloopClient
from exponent.version import get_version

load_dotenv()


def use_settings(f: Callable[..., Any]) -> Callable[..., Any]:
    @click.option(
        "--prod",
        is_flag=True,
        hidden=True,
        help="Use production URLs even if in editable mode",
    )
    @click.option(
        "--staging",
        is_flag=True,
        hidden=True,
        help="Use staging URLs even if in editable mode",
    )
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        prod = kwargs.pop("prod", False)
        staging = kwargs.pop("staging", False)
        settings = get_settings(use_prod=prod, use_staging=staging)

        if is_editable_install() and not (prod or staging):
            assert settings.environment == Environment.development
            print_editable_install_warning(settings)

        return f(*args, settings=settings, **kwargs)

    return decorated_function


def use_prod_settings(f: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        settings = get_settings(use_prod=True)

        if is_editable_install():
            print_editable_install_forced_prod_warning(settings)

        return f(*args, settings=settings, **kwargs)

    return decorated_function


@click.group()
@click.version_option(get_version(), prog_name="Exponent CLI")
def cli() -> None:
    """Exponent CLI group."""
    set_log_level()
    if not is_editable_install():
        check_exponent_version()


@cli.command()
@use_settings
def config(settings: Settings) -> None:
    config_file_settings = settings.get_config_file_settings()

    click.secho(
        json.dumps(config_file_settings, indent=2),
        fg="green",
    )


@cli.command()
@click.option("--key", help="Your Exponent API Key")
@use_settings
def login(settings: Settings, key: str) -> None:
    if not key:
        redirect_to_login(settings, "provided")
        return

    click.echo(f"Saving API Key to {settings.config_file_path}")

    if settings.api_key and settings.api_key != key:
        click.confirm("Detected existing API Key, continue? ", default=True, abort=True)

    settings.update_api_key(key)
    settings.write_settings_to_config_file()

    click.echo("API Key saved.")


@cli.command()
@click.option(
    "--chat-id",
    help="ID of an existing chat session to reconnect",
    required=False,
)
@click.option(
    "--prompt",
    help="Start a chat with a given prompt.",
)
@click.option(
    "--benchmark",
    is_flag=True,
    help="Enable benchmarking mode",
)
@use_settings
def run(
    settings: Settings,
    chat_id: str | None = None,
    prompt: str | None = None,
    benchmark: bool = False,
) -> None:
    chat_uuid = chat_id

    if not settings.api_key:
        redirect_to_login(settings)
        return

    api_key = settings.api_key

    loop = asyncio.get_event_loop()
    task = loop.create_task(
        start_client(
            settings.environment,
            api_key,
            settings.base_url,
            settings.base_api_url,
            chat_uuid=chat_uuid,
            prompt=prompt,
            benchmark=benchmark,
        )
    )
    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        task.cancel()
        try:
            loop.run_until_complete(task)
        except asyncio.CancelledError:
            pass
    except ExponentError as e:
        click.secho(f"Encountered error: {e}", fg="red")
        click.secho(
            "The Exponent team has been notified, "
            "please try again and reach out if the problem persists.",
            fg="yellow",
        )
        sys.exit(1)


@cli.command()
@click.option(
    "--prompt",
    help="Start a chat with a given prompt.",
)
@use_prod_settings
def cloud(
    settings: Settings,
    prompt: str | None = None,
) -> None:
    if not settings.api_key:
        redirect_to_login(settings)
        return

    api_key = settings.api_key

    loop = asyncio.get_event_loop()
    task = loop.create_task(
        start_cloud(
            settings.environment,
            api_key,
            settings.base_url,
            settings.base_api_url,
            prompt=prompt,
        )
    )
    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        task.cancel()
        try:
            loop.run_until_complete(task)
        except asyncio.CancelledError:
            pass


async def start_cloud(
    environment: Environment,
    api_key: str,
    base_url: str,
    base_api_url: str,
    prompt: str | None = None,
) -> None:
    current_working_directory = os.getcwd()

    # Check if an `.exponent.cloud.json` file exists.
    # If so, use it. If not, write a template file and exit.
    file_path = os.path.join(current_working_directory, ".exponent.cloud.json")
    if not os.path.exists(file_path):
        click.secho("No `.exponent.cloud.json` file found, creating one to fill out...")
        write_template_exponent_cloud_config(file_path)
        click.secho(
            "`.exponent.cloud.json` file created, fill out the required fields "
            "and run this command again."
        )
        return

    with open(file_path) as f:
        try:
            exponent_cloud_config = ExponentCloudConfig.model_validate_json(f.read())
        except ValidationError as e:
            click.secho(f"Error in parsing `.exponent.cloud.json`: {e}", fg="red")
            return

    # Step 1. Create a chat
    try:
        async with RemoteExecutionClient.session(
            api_key, base_api_url, current_working_directory
        ) as client:
            chat = await client.create_chat()
            chat_uuid = chat.chat_uuid
    except httpx.ConnectError as e:
        click.secho(f"Error: {e}", fg="red")
        return

    click.secho(
        "Chat created. Waiting for cloud container to spin up...", fg="green", bold=True
    )

    runloop_client = RunloopClient(
        api_key=exponent_cloud_config.runloop_api_key,
    )

    def join_commands(commands: list[str]) -> str:
        return " && ".join(commands)

    if prompt:
        exponent_command = (
            f'exponent run --prod --chat-id {chat_uuid} --prompt \\"{prompt}\\"'
        )
    else:
        exponent_command = f"exponent run --prod --chat-id {chat_uuid}"

    devbox = await runloop_client.create_devbox(
        entrypoint="/home/user/run.sh",
        environment_variables={"GH_TOKEN": exponent_cloud_config.gh_token},
        setup_commands=[
            join_commands(exponent_cloud_config.repo_specific_setup_commands),
            f'echo "cd /home/user/{exponent_cloud_config.repo_name} && source .venv/bin/activate && uv pip install exponent-run && exponent login --prod --key {api_key} && {exponent_command}" > /home/user/run.sh',
            "chmod +x /home/user/run.sh",
        ],
    )

    # Step 3. Poll Runloop for container spinup and log status
    while True:
        current_devbox = await runloop_client.get_devbox(devbox["id"])
        if current_devbox["status"] != "running":
            print(
                f"Container {devbox['id']} is loading, waiting.... Current status is {current_devbox['status']}"
            )
        elif current_devbox["status"] == "failure":
            click.secho("Devbox failed to start", fg="red", bold=True)
            sys.exit(1)
        else:
            break

        time.sleep(1)

    # Step 4. Open the chat in the browser
    print_exponent_message(base_url, chat_uuid)
    launch_exponent_browser(environment, base_url, chat_uuid)

    # Step 5. Wait for user input with the message "Stop Runloop?"
    input("Stop cloud container?: [press enter to continue]")

    # Step 6. Stop Runloop
    await runloop_client.shutdown_devbox(devbox["id"])
    click.secho("Cloud container stopped", fg="green", bold=True)


@cli.command()
@click.option(
    "--devbox-id",
    type=str,
    help="Devbox ID to get logs from.",
    required=True,
    prompt=True,
)
@use_prod_settings
def cloud_logs(
    devbox_id: str,
    settings: Settings,
) -> None:
    loop = asyncio.get_event_loop()
    task = loop.create_task(start_cloud_logs(devbox_id))
    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        task.cancel()
        try:
            loop.run_until_complete(task)
        except asyncio.CancelledError:
            pass


async def start_cloud_logs(
    devbox_id: str,
) -> None:
    current_working_directory = os.getcwd()

    # Check if an `.exponent.cloud.json` file exists.
    # If so, use it. If not, write a template file and exit.
    file_path = os.path.join(current_working_directory, ".exponent.cloud.json")
    if not os.path.exists(file_path):
        click.secho("No `.exponent.cloud.json` file found, creating one to fill out...")
        write_template_exponent_cloud_config(file_path)
        click.secho(
            "`.exponent.cloud.json` file created, fill out the required fields "
            "and run this command again."
        )
        return

    with open(file_path) as f:
        try:
            exponent_cloud_config = ExponentCloudConfig.model_validate_json(f.read())
        except ValidationError as e:
            click.secho(f"Error in parsing `.exponent.cloud.json`: {e}", fg="red")
            return

    runloop_client = RunloopClient(
        api_key=exponent_cloud_config.runloop_api_key,
    )

    response = await runloop_client.devbox_logs(devbox_id)
    for log in response["logs"]:
        click.secho(log["message"])


async def start_client(  # noqa: PLR0913
    environment: Environment,
    api_key: str,
    base_url: str,
    base_api_url: str,
    chat_uuid: str | None = None,
    prompt: str | None = None,
    benchmark: bool = False,
) -> None:
    if benchmark is True and prompt is None:
        click.secho("Error: Benchmark mode requires a prompt.", fg="red")
        return

    current_working_directory = os.getcwd()

    original_chat_uuid = chat_uuid
    if not chat_uuid:
        try:
            async with RemoteExecutionClient.session(
                api_key, base_api_url, current_working_directory
            ) as client:
                chat = await client.create_chat()
                chat_uuid = chat.chat_uuid
        except httpx.ConnectError as e:
            click.secho(f"Error: {e}", fg="red")
            return

    print_exponent_message(base_url, chat_uuid)

    # Open the chat in the browser
    if not benchmark and not prompt and not original_chat_uuid:
        launch_exponent_browser(environment, base_url, chat_uuid)

    use_tools_config = UseToolsConfig()
    async with RemoteExecutionClient.session(
        api_key, base_api_url, current_working_directory
    ) as client:
        if benchmark:
            assert prompt is not None
            await asyncio.gather(
                start_chat(
                    client, chat_uuid, prompt, use_tools_config=use_tools_config
                ),
                run_execution_client(client, chat_uuid),
                benchmark_mode_exit(client, chat_uuid),
                heartbeat_thread(client, chat_uuid),
                signal_listener_thread(client, chat_uuid),
            )
        elif prompt:
            await asyncio.gather(
                start_chat(
                    client, chat_uuid, prompt, use_tools_config=use_tools_config
                ),
                run_execution_client(client, chat_uuid),
                heartbeat_thread(client, chat_uuid),
                signal_listener_thread(client, chat_uuid),
            )
        else:
            await asyncio.gather(
                run_execution_client(client, chat_uuid),
                heartbeat_thread(client, chat_uuid),
                signal_listener_thread(client, chat_uuid),
            )


async def run_execution_client(client: RemoteExecutionClient, chat_uuid: str) -> None:
    async def handle_request(
        execution_request: RemoteExecutionRequestType,
    ) -> RemoteExecutionResponse:
        print(f"handling request: {execution_request}")
        click.echo(f"Handling {execution_request.namespace} request:")
        click.echo(f"  - {execution_request}")
        execution_response = await client.handle_request(execution_request)
        click.echo(f"Posting {execution_request.namespace} response.")
        return execution_response

    await client.for_each_execution_request(chat_uuid, handle_request)


async def start_chat(
    client: RemoteExecutionClient,
    chat_uuid: str,
    prompt: str,
    use_tools_config: UseToolsConfig,
) -> None:
    click.secho("Starting chat...")
    await client.start_chat(chat_uuid, prompt, use_tools_config=use_tools_config)
    click.secho("Chat started. Open the link to join the chat.")


async def benchmark_mode_exit(client: RemoteExecutionClient, chat_uuid: str) -> None:
    while True:
        await asyncio.sleep(5)
        if await client.check_remote_end_event(chat_uuid):
            sys.exit(0)


async def heartbeat_thread(client: RemoteExecutionClient, chat_uuid: str) -> None:
    await client.send_heartbeats(chat_uuid)


async def signal_listener_thread(client: RemoteExecutionClient, chat_uuid: str) -> None:
    await client.wait_for_disconnect_signal(chat_uuid)
    click.secho("Disconnect signaled. Exiting.")
    _thread.interrupt_main()


def set_log_level() -> None:
    settings = get_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level), stream=sys.stdout)


def redirect_to_login(settings: Settings, cause: str = "detected") -> None:
    if inside_ssh_session():
        click.echo(f"No API Key {cause}, run 'exponent login --key <API-KEY>'")
    else:
        click.echo("No API Key detected, redirecting to login...")
        click.launch(f"{settings.base_url}/")


def inside_ssh_session() -> bool:
    return (os.environ.get("SSH_TTY") or os.environ.get("SSH_TTY")) is not None


if __name__ == "__main__":
    cli()
