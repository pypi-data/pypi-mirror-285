"""User-related commands for the adalib CLI.

This submodule focuses on commands that are related to user management in the adalib CLI.
These include viewing user information, managing user settings, and other user-specific operations.

Functions:
- whoami: Retrieves information for a specific user.
- update-settings: Updates settings for a user. (TODO)
- list-users: Lists all users in the system. (TODO, admin mode)
"""

import json
import sys

import typer
from adalib.adaboard import get_user
from prompt_toolkit.completion import NestedCompleter
from rich.console import Console
from rich.table import Table

from .completion_tree import completion_tree
from .factory import check_authentication
from .interactive import interactive_mode

user_app = typer.Typer()


def format_roles(roles):
    """Formats roles for display."""
    return ", ".join([f"{role}: {', '.join(roles_list)}" for role, roles_list in roles.items()])


@user_app.command("whoami")
def user_who_am_i_in_adalab(
    full_information: bool = typer.Option(False, "--full-information"),
    with_notifications: bool = typer.Option(False, "--with-notifications"),
):
    """Shows the current authenticated user information."""
    try:
        user = get_user(include_notification_preferences=with_notifications)
    except Exception as e:
        sys.exit(f"Error: {str(e)}")

    if full_information:
        print(json.dumps(user, indent=2))
        return

    basic_information = ["name", "username", "email", "image_id", "roles"]
    user_basic = {key: user[key] for key in basic_information if key in user}

    if "roles" in user_basic:
        user_basic["roles"] = format_roles(user_basic["roles"])

    console = Console()
    table = Table("Key", "Value", title="User Information")
    for key, value in user_basic.items():
        table.add_row(key, str(value))
    console.print(table)


@user_app.callback("interactive", invoke_without_command=True)
def main(
    interactive: bool = typer.Option(
        False, "-i", "--interactive", help="Activate interactive mode"
    )
):
    if interactive:
        interactive_mode(
            this_app=user_app,
            title="user",
            color="maroon",
            completion=NestedCompleter.from_nested_dict(completion_tree["user"]),
        )
    else:
        check_authentication()
