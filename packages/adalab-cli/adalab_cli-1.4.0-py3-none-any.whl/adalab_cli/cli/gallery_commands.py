"""Gallery command group for the adalib CLI.

This submodule encompasses commands related to Gallery functionalities
in the adalib CLI. It uses Typer for command line interface implementation,
providing functionalities like viewing card contents, managing cards, etc.

Functions:
- list_cards: Lists all available cards in the gallery.
- get-card: Displays contents of a specific card.
- approve-card: Approves a card in Gallery
- expose-card: Exposes a card in Gallery
- hide-card: Hides a card in Gallery
"""

import sys

import typer
from adalib.cards import approve_card, expose_card, get_card_contents, get_cards, hide_card
from loguru import logger
from prompt_toolkit.completion import NestedCompleter
from rich import print as rich_print
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from typing_extensions import Annotated

from .completion_tree import completion_tree
from .factory import check_authentication
from .interactive import interactive_mode

gallery_app = typer.Typer()


@gallery_app.command("list-cards", no_args_is_help=True)
def gallery_list_cards(
    card_type: Annotated[
        str,
        typer.Argument(
            help="The type of cards to list. " "Choose from [all, notebook, voila, url, group].",
        ),
    ]
):
    """
    Prints all cards from the Gallery with the type CARD_TYPE.
    """
    try:
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True
        ) as progress:
            progress.add_task(description="Fetching data...", total=None)
            cards = get_cards(card_type=card_type)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit()

    rich_print(f"Card type: {card_type} ({len(cards)})")

    table = Table("Card id", "Card type", "Card name", "Card author", title="Cards")
    for card in cards:
        table.add_row(str(card[0]), card[1], card[2], card[3])
    console = Console()
    console.print(table)


@gallery_app.command("get-card", no_args_is_help=True)
def gallery_get_card(
    card_id: Annotated[
        int,
        typer.Argument(
            help="The ID of the card you want to retrieve.",
        ),
    ],
):
    """
    Gets the contents of a card identified by CARD_ID.
    """
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Fetching data...", total=None)
            card = get_card_contents(card_id=card_id)
    except Exception:
        rich_print(f"Card {card_id} [bold red]failed[/bold red] to retrieve.")
        sys.exit(1)

    rich_print(card)


@gallery_app.command("approve-card", no_args_is_help=True)
def gallery_approve_card(
    card_id: Annotated[
        int,
        typer.Argument(
            help="The ID of the card you want to retrieve.",
        ),
    ],
):
    """
    Approves a card in gallery identify with CARD_ID.
    """
    try:
        approve_card(card_id=card_id)
    except Exception:
        rich_print(f"Card {card_id} [bold red]failed[/bold red] to approve.")
        sys.exit(1)
    rich_print(f"Card {card_id} [bold green]approved[/bold green] successfully.")


@gallery_app.command("expose-card", no_args_is_help=True)
def gallery_expose_card(
    card_id: Annotated[
        int,
        typer.Argument(
            help="The ID of the card you want to retrieve.",
        ),
    ],
):
    """
    Exposes a card in gallery identify with CARD_ID.
    """
    try:
        expose_card(card_id=card_id)
    except Exception:
        rich_print(f"Card {card_id} [bold red]failed[/bold red] to expose.")
        sys.exit(1)
    rich_print(f"Card {card_id} [bold green]exposed[/bold green] successfully.")


@gallery_app.command("hide-card")
def gallery_hide_card(
    card_id: Annotated[
        int,
        typer.Argument(
            help="The ID of the card you want to retrieve.",
        ),
    ],
):
    """
    Hides a card in gallery identify with CARD_ID.
    """
    try:
        hide_card(card_id=card_id)
    except Exception:
        rich_print(f"Card {card_id} [bold red]failed[/bold red] to hide.")
        sys.exit(1)
    rich_print(f"Card {card_id} [bold green]hidden[/bold green] successfully.")


@gallery_app.callback("callback", invoke_without_command=True)
def main(
    interactive: bool = typer.Option(
        False, "-i", "--interactive", help="Activate interactive mode"
    )
):
    if interactive:
        interactive_mode(
            this_app=gallery_app,
            title="cards",
            color="maroon",
            completion=NestedCompleter.from_nested_dict(completion_tree["cards"]),
        )
    else:
        check_authentication()
