"""Main module for the adalib CLI.

This module initializes the Typer application and integrates various
submodules that handle different command groups for the adalib CLI.

Submodules:
- oci_commands: Handles commands related to Open Container Initiative (OCI).
- gallery_commands: Manages commands for gallery operations.
- kernel_commands: Contains commands for kernel-related operations.
- user_commands: Deals with user-related commands.
"""

import importlib.metadata
import os

import requests
import typer
from loguru import logger
from prompt_toolkit.completion import NestedCompleter
from rich import print as rich_print
from rich.console import Console
from rich.table import Table

from . import authentication_flows as auth
from .completion_tree import completion_tree
from .databases_commands import db_app
from .gallery_commands import gallery_app
from .interactive import interactive_mode
from .logger import Logger
from .login_commands import load_config
from .schedule_commands import schedules_app
from .user_commands import user_app

app = typer.Typer(no_args_is_help=False)


@app.callback("adalab", invoke_without_command=True, no_args_is_help=True)
def main(
    token: str = typer.Option(None, help="User token for authentication"),
    adalab_url: str = typer.Option(None, help="URL of the AdaLab server"),
    adalab_secret: str = typer.Option(None, help="Client secret for AdaLab"),
    interactive: bool = typer.Option(
        False, "-i", "--interactive", help="Activate interactive mode"
    ),
    verbose: int = typer.Option(
        0,
        "-v",
        count=True,
        help="Verbosity level of the logs: -v (default): INFO | -vv: DEBUG | -vvv: TRACE",
        min=0,
        max=3,
    ),
    no_output: bool = typer.Option(False, "--no-output", help="Disable output from the CLI."),
):
    if no_output:
        logger.remove()
    else:
        Logger(verbosity=verbose)
    logger.info("Starting adalab CLI.")
    logger.debug("Debugging mode activated.")
    logger.trace("Tracing mode activated.")

    # Attempt to configure adalib with user token.
    # This works when token is either provided or stored in environment.
    try:
        auth.in_line_authentication(adalab_url, adalab_secret, token)
    except AssertionError as e:
        logger.info(f"{str(e)}")

    # Start the interactive mode
    if interactive:
        rich_print("🏡 Welcome to AdaLab CLI interactive mode.")
        rich_print("👋 Type 'exit' to quit.")
        rich_print("ℹ️  Type 'help' for help.")
        interactive_mode(
            this_app=app,
            title="adalab",
            nested=True,
            color="seagreen",
            completion=NestedCompleter.from_nested_dict(completion_tree),
        )


@app.command("login")
def login_commands(
    auth_flow: str = typer.Option(
        default="browser",
        help="Authentication flow. Options: browser, device-code, user-token",
    ),
    token: str = typer.Option(None, help="Token for authentication"),
):
    """
    Login to adalab
    """
    stored_configuration = load_config()
    adalab_server_url = stored_configuration.get(
        "adalab_url"
    )  # Look for the URL in the config file
    if adalab_server_url is None:
        adalab_server_url = os.getenv("ADALAB_URL")  # Look for the URL in env vars
        if adalab_server_url is None:
            adalab_server_url = typer.prompt("What is the AdaLab url?")  # Ask for the URL
    logger.info(f"AdaLab server URL: {adalab_server_url}")

    adalab_client_secret = stored_configuration.get(
        "adalab_secret"
    )  # Look for the client secret in the config file
    if adalab_client_secret is None:
        adalab_client_secret = os.getenv("ADALAB_CLIENT_SECRET")
        if "ADALAB_CLIENT_SECRET" not in os.environ:
            adalab_client_secret = typer.prompt(
                "What is the AdaLab client secret?", hide_input=True
            )
    logger.info("AdaLab client secret: ********")
    # Check validity of URL
    response = requests.get(adalab_server_url + "/adaboard/api", timeout=10)
    if response.status_code != 200:
        typer.echo("Invalid URL. Please try again.")
        raise typer.Exit()

    # Check which of the three kinds of authentication flows was set
    if auth_flow == "browser":
        auth.start_browser_auth(
            adalab_server_url=adalab_server_url, adalab_client_secret=adalab_client_secret
        )
    elif auth_flow == "user-token":
        auth.start_user_token_auth(
            adalab_server_url=adalab_server_url,
            token=token,
            adalab_client_secret=adalab_client_secret,
        )
    elif auth_flow == "device-code":
        auth.start_device_code_auth(
            adalab_server_url=adalab_server_url, adalab_client_secret=adalab_client_secret
        )

    else:
        typer.echo(
            "Invalid authentication flow. Please try again."
            "Options: browser, device-code, user-token"
        )
        raise typer.Exit()


@app.command("version")
def get_version():
    """
    Prints the version of adalib.
    """

    version_string_adalib = importlib.metadata.version("adalib")
    version_string_adalib_auth = importlib.metadata.version("adalib-auth")
    version_string_adalab_cli = importlib.metadata.version("adalab-cli")

    table = Table("Package", "Version")
    table.add_row("adalib", version_string_adalib)
    table.add_row("adalib-auth", version_string_adalib_auth)
    table.add_row("adalab-cli", version_string_adalab_cli)

    console = Console()

    console.print(table)


app.add_typer(
    db_app,
    name="databases",
    help="Commands for interacting with databases.",
    no_args_is_help=True,
)

app.add_typer(
    gallery_app,
    name="cards",
    help="Commands for interacting with the gallery.",
    no_args_is_help=True,
)

app.add_typer(
    user_app,
    name="user",
    help="Commands for interacting with user information.",
    no_args_is_help=True,
)

app.add_typer(
    schedules_app,
    name="schedules",
    help="Commands for interacting with schedules.",
    no_args_is_help=True,
)
