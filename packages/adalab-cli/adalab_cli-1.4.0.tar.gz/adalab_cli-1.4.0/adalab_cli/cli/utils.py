"""
utils.py - Utility functions for data analysis and manipulation.

This module provides a collection of utility functions to assist in various data analysis and
manipulation tasks. It includes functions for handling environment variables, checking SQL queries
in datasets, filtering datasets by database ID, and retrieving datasets from different sources.

Functions:
- get_environment_variable(var_name): Retrieve environment variable by name.
- has_sql_query(sql): Check if a given SQL string is non-empty and a string.
- get_datasets(include_nonpublic=False): Get datasets, optionally including non-public datasets.
- filter_datasets_by_database_id(dataset_list, database_id): Filter datasets by a specific database
  ID or return the original list.
- check_sql(dataset_list, include_sql): Check for the presence of SQL queries in a dataset list and
  optionally include SQL.

Dependencies:
- os: Provides access to operating system environment variables.
- sys: Provides access to system-specific functionality.

"""

import os
import sys

import pandas as pd
from adalib.superset import databases, datasets
from rich.console import Console
from rich.table import Table
from supersetapiclient.datasets import Dataset
from tabulate import tabulate


def get_environment_variable(var_name):
    """Retrieve environment variable."""
    try:
        return os.environ[var_name]
    except KeyError:
        sys.exit(f"Error: Environment variable {var_name} not set.")


def has_sql_query(sql):
    """Check if a given SQL string is non-empty and a string

    :param sql: The SQL string to check.
    :type sql: str
    :return: True if the SQL string is non-empty and a string, otherwise False.
    :rtype: bool
    """
    sql_exist = bool(sql)
    sql_is_string = isinstance(sql, str)
    return sql_exist and sql_is_string


def get_datasets():
    """Get all public datasets.

    :return: A DataFrame containing datasets.
    :rtype: pandas.DataFrame
    """
    all_datasets = datasets.all().as_df()
    return all_datasets.query("schema == 'public'")


def filter_datasets_by_database_id(dataset_list, database_id=None):
    """Filter datasets by a specific database ID or return the original list.

    :param dataset_list: The list of datasets to filter.
    :type dataset_list: list or pandas.DataFrame
    :param database_id: The database ID to filter by.
    :type database_id: int or None
    :return: A filtered list of datasets or False if the database ID is not found.
    :rtype: list or pandas.DataFrame or bool
    """
    if database_id is None:
        return dataset_list

    if database_id in databases.all().as_df().index:
        return dataset_list.query(f"database_id == {database_id}")

    return False


def check_sql(dataset_list, include_sql):
    """Check for the presence of SQL queries in a dataset list and optionally include SQL.

    :param dataset_list: The list of datasets to check.
    :type dataset_list: list or pandas.DataFrame
    :param include_sql: Whether to include SQL queries in the result.
    :type include_sql: bool
    :return: A dataset list with an added column indicating the presence of SQL queries.
    :rtype: pandas.DataFrame
    """
    # Make sure dataset_list is a DataFrame if it isn't already
    if not isinstance(dataset_list, pd.DataFrame):
        dataset_list = pd.DataFrame(dataset_list)

    # Use copy() to avoid modifying the original DataFrame
    dataset_list = dataset_list.copy()

    # Add a new column to indicate the presence of SQL queries
    dataset_list["has_sql_query"] = dataset_list["sql"].apply(has_sql_query)

    # Optionally drop the 'sql' column
    if not include_sql:
        dataset_list = dataset_list.drop("sql", axis=1)

    return dataset_list


def print_dataframe(dataframe: pd.DataFrame, pretty: bool, title: str = None):
    """
    Print a DataFrame in a specified format.

    :param dataframe: The DataFrame to be printed.
    :type dataframe: pandas.DataFrame
    :param pretty: Whether to display the output in a nice tabular view.
    :type pretty: bool
    """
    if pretty:
        console = Console()
        table = Table("Index", *dataframe.columns, title=title)
        for row in dataframe.itertuples(index=True):
            entries = [str(entry) for entry in row]
            table.add_row(*entries)
        console.print(table)
    else:
        print(tabulate(dataframe, dataframe.columns))


def retrieve_physical_dataset(my_dataset: Dataset, head: int):
    """
    Retrieve a physical dataset and return it as a DataFrame.

    :param my_dataset: The physical dataset to retrieve.
    :type my_dataset: supersetapiclient.datasets.Dataset
    :param head: Number of rows to retrieve (default is 10).
    :type head: int, optional
    :return: The retrieved dataset as a DataFrame.
    :rtype: pandas.DataFrame
    """
    my_db = databases.get(id=my_dataset.database_id)
    table_name = my_dataset.table_name
    if head:
        my_df = my_db.run(query=f"SELECT * FROM {table_name} LIMIT {head};").as_df()
    else:
        my_df = my_db.run(query=f"SELECT * FROM {table_name};").as_df()
    return my_df


def retrieve_virtual_dataset(my_dataset: Dataset, head=int):
    """
    Retrieve a virtual dataset and return it as a DataFrame.

    :param my_dataset: The physical dataset to retrieve.
    :type my_dataset: supersetapiclient.datasets.Dataset
    :param head: Number of rows to retrieve (default is 10).
    :type head: int, optional
    :return: The retrieved dataset as a DataFrame.
    :rtype: pandas.DataFrame
    """
    my_df = my_dataset.run().as_df().head(head) if head else my_dataset.run().as_df()
    return my_df
