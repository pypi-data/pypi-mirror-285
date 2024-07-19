"""Notebook-related commands for the adalib CLI.

This submodule focuses on commands that are related to the management of runs in the adalib CLI.
These include triggering single runs and managing schedules.

Functions:
- start-run: Retrieves information for a specific user.
- stop-run: Retrieves information for a specific user.
- start-schedule: Retrieves information for a specific user.

"""

import sys

import typer
from adalib.adaboard import get_user
from adalib.schedules import (
    create_schedule,
    delete_run,
    delete_schedule,
    edit_schedule,
    start_run,
    stop_run,
)
from prompt_toolkit.completion import NestedCompleter
from rich import print as rich_print
from typing_extensions import Annotated

from .completion_tree import completion_tree
from .factory import check_authentication
from .interactive import interactive_mode

schedules_app = typer.Typer()


@schedules_app.command("start-run", no_args_is_help=True)
def notebooks_start_run(
    schedule_id: Annotated[int, typer.Argument(help="ID of the schedule to start run.")]
):
    """Starts a single run of the schedule."""
    try:
        start_run(schedule_id=schedule_id)
        rich_print(f"Start run for schedule {schedule_id} [bold green]succeeded[/bold green].")
    except Exception:  # noqa
        rich_print(f"Start run for schedule {schedule_id} [bold red]failed[/bold red].")
        sys.exit(1)


@schedules_app.command("stop-run", no_args_is_help=True)
def notebooks_stops_run(
    schedule_id: Annotated[
        int, typer.Argument(help="ID of the schedule to stop the associated run.")
    ],
    run_id: Annotated[int, typer.Argument(help="The ID of the run to be stopped.")],
):
    """Stops the specified scheduled run."""
    try:
        stop_run(schedule_id=schedule_id, run_id=run_id)
        rich_print(f"Stop run for run {run_id} [bold green]succeeded[/bold green].")
    except Exception:  # noqa
        rich_print(f"Stop run for run {run_id} [bold red]failed[/bold red].")
        sys.exit(1)


@schedules_app.command("delete-run", no_args_is_help=True)
def notebooks_delete_run(
    schedule_id: Annotated[
        int, typer.Argument(help="The ID of the schedule to delete the associated run.")
    ],
    run_id: Annotated[int, typer.Argument(help="The ID of the run to be deleted.")],
):
    """Deletes the specified scheduled run."""
    try:
        delete_run(schedule_id=schedule_id, run_id=run_id)
        rich_print(f"Delete run for run {run_id} [bold green]succeeded[/bold green].")
    except Exception:  # noqa
        rich_print(f"Delete run for run {run_id} [bold red]failed[/bold red].")
        sys.exit(1)


@schedules_app.command("create-schedule", no_args_is_help=True)
def notebooks_create_schedule(
    card_id: int = typer.Argument(help="The card's ID for the notebook schedule."),
    schedule_name: str = typer.Argument(help="The name of the schedule."),
    schedule: str = typer.Option("00 00 * * *", help="The schedule time string in cron format."),
    pool: str = typer.Option("card-runner-low", "--pool", help="The execution pool."),
    active: bool = typer.Option(True, help="Whether the schedule is active."),
    concurrent: bool = typer.Option(True, help="Whether the schedule can run concurrently."),
    cleanup: bool = typer.Option(True, help="Whether to clean up resources after the schedule."),
    timeout: int = typer.Option(
        3600, "--timeout", help="A dictionary of input parameters for the schedule."
    ),
    timezone: str = typer.Option("Etc/UTC", help="The timezone for the schedule."),
):
    """Creates a notebook schedule of a card in gallery identified with CARD_ID."""
    user = get_user()
    config = {
        "name": schedule_name,
        "card_id": card_id,
        "owner_id": user["username"],
        "runner_id": user["username"],
        "schedule": schedule,
        "pool": pool,
        "active": active,
        "concurrent": concurrent,
        "cleanup": cleanup,
        "timeout": timeout,
        "timezone": timezone,
        "inputs": {},
        "acl_type_view": "userlist",
        "acl_list_view": [user["username"]],
        "acl_type_logs": "userlist",
        "acl_list_logs": [user["username"]],
        "acl_type_edit": "userlist",
        "acl_list_edit": [user["username"]],
        "acl_type_decrypt": "userlist",
        "acl_list_decrypt": [user["username"]],
    }

    try:
        schedule_id = create_schedule(**config)
        rich_print(f"Notebook schedule [bold green]created with id {schedule_id}[/bold green].")
    except Exception:  # noqa
        rich_print(f"Notebook schedule for card {card_id} [bold red]failed[/bold red].")
        sys.exit(1)


@schedules_app.command("update-schedule", no_args_is_help=True)
def notebooks_update_schedule(
    schedule_id: int = typer.Argument(help="The schedule ID to update."),
    schedule_name: str = typer.Option(None, help="The name of the schedule."),
    schedule: str = typer.Option(None, help="The schedule time string in cron format."),
    pool: str = typer.Option(None, "--pool", help="The execution pool."),
    active: bool = typer.Option(True, help="Whether the schedule is active."),
    concurrent: bool = typer.Option(True, help="Whether the schedule can run concurrently."),
    cleanup: bool = typer.Option(True, help="Whether to clean up resources after the schedule."),
    timeout: int = typer.Option(
        None, "--timeout", help="A dictionary of input parameters for the schedule."
    ),
    timezone: str = typer.Option("Etc/UTC", help="The timezone for the schedule."),
):
    """Updates the specified schedule."""
    config = {
        "schedule_id": schedule_id,
        "name": schedule_name,
        "schedule": schedule,
        "pool": pool,
        "active": active,
        "concurrent": concurrent,
        "cleanup": cleanup,
        "timeout": timeout,
        "timezone": timezone,
    }
    try:
        edit_schedule(**config)
        rich_print(f"Schedule {schedule_id} [bold green]updated[/bold green].")
    except Exception:  # noqa
        rich_print(f"Schedule {schedule_id} [bold red]failed[/bold red] to update.")
        sys.exit(1)


@schedules_app.command("delete-schedule", no_args_is_help=True)
def notebooks_delete_schedule(
    schedule_id: Annotated[int, typer.Argument(help="The ID of the schedule to be deleted.")],
):
    """Deletes the specified schedule."""
    try:
        delete_schedule(schedule_id=schedule_id)
        rich_print(f"Notebook schedule {schedule_id} [bold green]deleted[/bold green].")
    except Exception:  # noqa
        rich_print(f"Notebook schedule {schedule_id} [bold red]failed[/bold red] to delete.")
        sys.exit(1)


@schedules_app.callback("interactive", invoke_without_command=True)
def main(
    interactive: bool = typer.Option(
        False, "-i", "--interactive", help="Activate interactive mode"
    )
):
    if interactive:
        interactive_mode(
            this_app=schedules_app,
            title="schedules",
            completion=NestedCompleter.from_nested_dict(completion_tree["schedules"]),
        )
    else:
        check_authentication()
