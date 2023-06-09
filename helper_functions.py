"""Helper functions for Query Processing."""
import configparser
import os
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta
from typing import Tuple, Callable, TypeVar, Any, List, Type
from enum import Enum
from time import perf_counter
from constants import ROOT_DIR
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

# Type variable for the return type of the function passed to wrap_with_timings.
wraps_result = TypeVar('wraps_result')


def wrap_with_timings(name: str, func: Callable[[], wraps_result]) -> wraps_result:
    """
    Execute a given function and prints the time it took the function to execute.

    Keyword arguments:
        name: identifier for the function execution, used to identify it in the output
        func: the zero argument function to execute

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


def get_config() -> configparser.ConfigParser:
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


def readfile(path_from_root) -> str:
    """Read a file from the root directory."""
    path = os.path.join(ROOT_DIR, f'{path_from_root}')
    with open(path, "r") as f:
        return f.read()


def get_file_path(path_from_root: str) -> str:
    """Get the path to a file from the root directory.

    Args:
        path_from_root: The path to the file from the root directory.
    """
    return os.path.join(ROOT_DIR, f'{path_from_root}')


def get_file_contents(path_from_root: str) -> str:
    """Get the contents of a file from the root directory.

    Args:
        path_from_root: The path to the file from the root directory.
    """
    with open(get_file_path(path_from_root), 'r') as f:
        return f.read()


def response_json(query: str, dw: Session, params: dict) -> Any:
    """
    Convert the response from a query to JSON compatible format.

    Args:
        query: The query to execute.
        dw: The data warehouse session.
        params: The parameters to pass to the query.

    Returns:
        A JSON compatible response.
    """
    return jsonable_encoder(response_dict(query, dw, params))


def response_dict(query: str, dw: Session, params: dict) -> list[dict]:
    """
    Return a list of dictionaries from a query.

    Args:
        query: The query to execute.
        dw: The data warehouse session.
        params: The parameters to pass to the query.
    """
    df = pd.read_sql(text(query), dw.bind.connect(), params=params)
    return df.to_dict(orient="records")


def get_values_from_enum_list(enum_list: List[Enum], enum_type: Type[Enum]) -> List[Any]:
    """
    Get a list of values from a list of enums.

    Args:
        enum_list: A list of enums.
        enum_type: The type of the enums in the list.

    Returns: A list of values from an enum list.
    """
    return [enum_type(value).value for value in enum_list]
