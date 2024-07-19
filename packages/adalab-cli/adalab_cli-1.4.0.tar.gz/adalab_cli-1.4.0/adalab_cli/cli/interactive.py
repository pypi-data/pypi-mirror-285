import os
import shlex

import typer
from loguru import logger
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory

NEST = {}


def interactive_mode(
    this_app: typer.Typer,
    title: str,
    nested: bool = False,
    color: typer.colors = "maroon",
    completion=None,
):
    # session = PromptSession()
    home_dir = os.path.expanduser("~")
    history_file = "history.log"
    history_path = os.path.join(home_dir, ".adalab", history_file)
    os.makedirs(os.path.dirname(history_path), exist_ok=True)

    file_history = FileHistory(history_path)
    session = PromptSession(history=file_history)
    NEST[title] = color
    cmd_title = ""
    for key, value in NEST.items():
        cmd_title += f"<{value}><b>{key}></b></{value}> "

    while True:
        try:
            user_input = session.prompt(
                HTML(cmd_title),
                completer=completion,
                # complete_while_typing=True,
                complete_in_thread=True,
                auto_suggest=AutoSuggestFromHistory(),
            )
            if user_input.lower() == "exit":
                NEST.pop(title)
                break  # Exit the interactive mode
            if user_input.lower() == "help":
                this_app(["--help"])
                continue
            # Splitting the input to pass as arguments
            args = shlex.split(user_input)
            if len(args) == 1 and nested:
                if args[0] not in [command.name for command in this_app.registered_commands]:
                    args.append("-i")

            # Executing the Typer command based on user input
            this_app(args)

        except SystemExit:
            # Handle any sys.exit() calls in the commands
            continue
        except Exception as e:
            # Remove the title from NEST
            NEST.pop(title)
            logger.error(f"Error: {str(e)}")
            break
