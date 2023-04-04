"""Helper functions for Query Processing."""
import configparser
import os
from datetime import datetime, timedelta
from typing import Tuple, Callable, TypeVar
from time import perf_counter
import psycopg2
from constants import ROOT_DIR
from sqlalchemy import text


def wrap_with_timings(name: str, func, audit_etl_stage: str = None):
    """
    Execute a given function and prints the time it took the function to execute.

    Keyword arguments:
        name: identifier for the function execution, used to identify it in the output
        func: the zero argument function to execute
        audit_etl_stage: name of the ETL stage, must be a valid ETL stage name. If used, the ETL stage will be logged.
            (default: None)

    Examples
    --------
    >>> wrap_with_timings('my awesome addition', lambda: 2+3)
    my awesome addition started at 01/01/2021 00:00:00.00000
    my awesome addition finished at 01/01/2021 00:00:00.00003
    my awesome addition took 0:00:00.00003
    """
    print(f"{name} started at {datetime.now()}")
    start = perf_counter()
    result = func()
    end = perf_counter()
    print(f"{name} finished at {datetime.now()}")
    print(f"{name} took {timedelta(seconds=(end - start))}")

    return result


# Type variable for the return type of the function passed to measure_time.
# Used to indicate same return type as the function parameter
T = TypeVar('T')


def measure_time(func: Callable[[], T]) -> Tuple[T, float]:
    """
    Execute a given function and return a tuple with the result and the time it took to execute.

    Keyword arguments:
        func: the zero argument function to execute
    """
    start = perf_counter()
    result = func()
    end = perf_counter()
    return result, end - start


config = None  # Global configuration variable


def get_config():
    """Get the application configuration."""
    global config

    if config is None:
        path = os.path.join(ROOT_DIR, 'config.properties')
        local_path = os.path.join(ROOT_DIR, 'config-local.properties')
        config = configparser.ConfigParser()

        if os.path.isfile(local_path):
            config.read(local_path)
        elif os.path.isfile(path):
            config.read(path)
        else:
            raise FileNotFoundError('Configuration file not found')

    return config


def readfile(path_from_root):
    """Read a file from the root directory."""
    path = os.path.join(ROOT_DIR, f'{path_from_root}')
    with open(path, "r") as f:
        return f.read()


def get_connection():
    """
    Return a connection to the database.

    Keyword arguments:
        config: the application configuration
        database: the name of the database (default None)
        host: host and port of the database concatenated using ':' (default None)
        user: username for the database user to use (default None)
        password: password for the database user (defualt None)
    """
    config = get_config()
    host, port = config['Database']['host'].split(':')
    database = config['Database']['database']
    user = config['Database']['user']
    password = config['Database']['password']
    return psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port
    )


def query_apply_filters(query, filters):
    """
    Apply filters to a query.

    Keyword arguments:
        query: the query to apply the filters to
        filters: the filters to apply
    """
    for filter in filters:
        query = query.filter(filter)

    return query


def get_sql_file_path(path_from_root):
    return os.path.join(ROOT_DIR, f'{path_from_root}')

def get_sql_file_contents(path_from_root):
    with open(get_sql_file_path(path_from_root), 'r') as f:
        return f.read()

def get_sql_file_contents_as_text(path_from_root):
    return text(get_sql_file_contents(path_from_root))

def run_sql_file(path_from_root, dw):
    return dw.execute(get_sql_file_contents_as_text(path_from_root))

def run_sql_file_with_params(path_from_root, dw, params):
    return dw.execute(get_sql_file_contents_as_text(path_from_root), params)