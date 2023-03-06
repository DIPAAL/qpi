"""Helper functions for Query Processing."""
import configparser
import os
from datetime import datetime, timedelta
from typing import Tuple, Callable, TypeVar
from time import perf_counter
import psycopg2


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
        path = './config.properties'
        local_path = './config-local.properties'
        if os.path.isfile(local_path):
            path = local_path
        config = configparser.ConfigParser()
        config.read(path)

    return config


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
