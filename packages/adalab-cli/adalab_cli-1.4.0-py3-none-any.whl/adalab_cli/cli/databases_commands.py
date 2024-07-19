""" docstrings"""

import sys

import typer
from loguru import logger
from prompt_toolkit.completion import NestedCompleter
from rich import print as rich_print
from rich.progress import Progress, SpinnerColumn, TextColumn

# from adalib.superset import databases, datasets
from typing_extensions import Annotated

from .completion_tree import completion_tree
from .factory import check_authentication

# from . import utils
from .interactive import interactive_mode

db_app = typer.Typer()


@db_app.command("list-databases")
def database_list_databases(
    pretty: Annotated[
        bool,
        typer.Option(help="Set this flag to get the output in a nice tabular view."),
    ] = True
):
    """Prints all databases available."""
    from adalib.superset import databases  # noqa: E402

    from . import utils

    try:
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True
        ) as progress:
            progress.add_task(description="Fetching data...", total=None)
            my_databases = databases.all().as_df()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)
    # my_databases = databases.all().as_df()
    utils.print_dataframe(dataframe=my_databases, pretty=pretty, title="Databases")


@db_app.command("list-datasets")
def database_list_datasets(
    database_id: Annotated[
        int,
        typer.Argument(help="Specific database from which datasets are listed."),
    ] = None,
    return_sql: Annotated[
        bool,
        typer.Option(help="Set this flag to get the SQL query in the output."),
    ] = False,
    pretty: Annotated[
        bool,
        typer.Option(help="Set this flag to get the output in a nice tabular view."),
    ] = True,
):
    """
    Prints all datasets available in the databases DATABASE_ID.
    If DATABASE_ID is not specified then datasets in all available databases are returned.

    Example usage:

    adalab databases list-datasets --return-sql --pretty 1

    will print the available datasets in the database identified with DATABASE_ID=1, including
    the SQL query (if available) in a nice tabular view.
    """
    from . import utils

    try:
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True
        ) as progress:
            progress.add_task(description="Fetching data...", total=None)
            my_datasets = utils.get_datasets()

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

    filtered_datasets = utils.filter_datasets_by_database_id(
        dataset_list=my_datasets, database_id=database_id
    )

    if filtered_datasets is False:
        rich_print(f"The database with index {database_id} is not available.")

    else:
        format_datasets = utils.check_sql(dataset_list=filtered_datasets, include_sql=return_sql)
        utils.print_dataframe(
            dataframe=format_datasets,
            pretty=pretty,
            title=(
                f"Datasets in database {database_id}"
                if (database_id is not None)
                else "All Datasets"
            ),
        )


@db_app.command("view-dataset", no_args_is_help=True)
def database_view_dataset_by_index(
    ds_index: Annotated[int, typer.Argument(help="Index of the dataset to print.")] = None,
    head: Annotated[
        int,
        typer.Option(help="Set --head N for printing the first N elements in the dataframe."),
    ] = 10,
    pretty: Annotated[
        bool,
        typer.Option(help="Set this flag to get the output in a nice tabular view."),
    ] = True,
):
    """
    Prints the first elements of the dataset indexed by DS_INDEX, by
    default it prints the first 10 elements.

    Example usage:

    adalab databases view-dataset 15 --head 11 --pretty

    will print the first 11 elements of the dataset with index 15
    in a nice tabular view.
    """
    from adalib.superset import datasets

    from . import utils

    if ds_index not in datasets.all().as_df().index:
        return rich_print(
            f"Dataset with index {ds_index} [bold red]not available[/bold red].\n"
            + "Run [bold blue]list-datasets[/bold blue] for available options"
        )

    try:
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True
        ) as progress:
            progress.add_task(description="Fetching data...", total=None)
            my_dataset = datasets.get(id=ds_index)

            if my_dataset.kind == "virtual":
                my_df = utils.retrieve_virtual_dataset(my_dataset=my_dataset, head=head)
            elif my_dataset.kind == "physical":
                my_df = utils.retrieve_physical_dataset(my_dataset=my_dataset, head=head)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

    utils.print_dataframe(dataframe=my_df, pretty=pretty, title=f"Dataset {ds_index}")


@db_app.command("list-tables", no_args_is_help=True)
def list_tables(
    db_index: Annotated[int, typer.Argument(help="Database index.")] = None,
    pretty: Annotated[
        bool,
        typer.Option(help="Set this flag to get the output in a nice tabular view."),
    ] = True,
):
    """
    List tables in the database with the specified index.

    Example usage:

    adalab databases list-tables 1 --pretty

    will print the tables in the databes with database index 1 in a nice tabular view.
    """
    from adalib.superset import databases

    from . import utils

    try:
        available_index = databases.all().as_df().index
        assert db_index in available_index, (
            f"Database with index {db_index} not available."
            + " Run list-databases for available options"
        )
    except AssertionError as ae:
        logger.error(f"Error: {str(ae)}")
        sys.exit(1)

    try:
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True
        ) as progress:
            progress.add_task(description="Fetching data...", total=None)
            db = databases.get(id=db_index)
            tables = db.run(
                query="SELECT table_name "
                "FROM information_schema.tables  "
                "WHERE table_schema = 'public';"
            ).as_df()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)
    utils.print_dataframe(dataframe=tables, pretty=pretty, title=f"Tables in database {db_index}")


@db_app.callback("callback", invoke_without_command=True)
def main(
    interactive: bool = typer.Option(
        False, "-i", "--interactive", help="Activate interactive mode"
    )
):
    if interactive:
        interactive_mode(
            this_app=db_app,
            title="databases",
            color="maroon",
            completion=NestedCompleter.from_nested_dict(completion_tree["databases"]),
        )
    else:
        check_authentication()
