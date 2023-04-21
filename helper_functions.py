"""Helper functions for Query Processing."""
import configparser
import os
from datetime import datetime, timedelta
from typing import Tuple, Callable, TypeVar
from time import perf_counter
from constants import ROOT_DIR
import psycopg2
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # This is to avoid circular imports
    from app.querybuilder import QueryBuilder

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


def get_connection() -> psycopg2.extensions.connection:
    """Return a connection to the database."""
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


def get_file_path(path_from_root: str) -> str:
    """Get the path to a file from the root directory.

    Args:
        path_from_root (str): The path to the file from the root directory.
    """
    return os.path.join(ROOT_DIR, f'{path_from_root}')


def get_file_contents(path_from_root: str) -> str:
    """Get the contents of a file from the root directory.

    Args:
        path_from_root (str): The path to the file from the root directory.
    """
    with open(get_file_path(path_from_root), 'r') as f:
        return f.read()


def response(query: str, dw: Session, params: dict) -> list[dict]:
    """
    Return a list of dictionaries from a query.

    Args:
        query (str): The query to execute.
        dw (Session): The data warehouse session.
        params (dict): The parameters to pass to the query.
    """
    df = pd.read_sql(text(query), dw.bind.connect(), params=params)
    return df.to_dict(orient="records")


# The following helper functions are usually used in conjunction with the QueryBuilder class.
def update_params_datetime(param_dict: dict, dt: datetime, from_or_to: str) -> None:
    """
    Update the given parameter dict with the given parameters.

    Args:
        param_dict (dict): The parameter dict to update.
        dt (datetime): The date and time to update the parameter dict with.
        from_or_to (str): A string, either "from" or "to" to indicate if the datetime is the upper or lower bound
         of the temporal bounds.
    """
    if dt:
        param_dict.update({
            f'{from_or_to}_date': int(dt.strftime("%Y%m%d")),
            f'{from_or_to}_time': int(dt.strftime("%H%M%S"))
        })


def update_params_datetime_min_max_if_none(temporal_params: dict, temporal_bounds: bool,
                                           from_datetime: datetime, to_datetime: datetime) -> None:
    """
    Update the temporal parameters to min and max datetime if the temporal bounds are provided, but not complete.

    Args:
        temporal_params (dict): The temporal parameters to update.
        temporal_bounds (bool): If true, the temporal bounds are added to the temporal parameters.
        from_datetime (datetime): The from datetime.
        to_datetime (datetime): The to datetime.
    """
    if temporal_bounds and None in temporal_params.values():
        if from_datetime is None:
            temporal_params["from_date"] = datetime.min.strftime("%Y%m%d")
            temporal_params["from_time"] = datetime.min.strftime("%H%M%S")
        elif to_datetime is None:
            temporal_params["to_date"] = datetime.max.strftime("%Y%m%d")
            temporal_params["to_time"] = datetime.max.strftime("%H%M%S")


def add_filters_to_query_and_param(qb: "QueryBuilder", relation_name: str, filter_params: dict, params: dict) -> None:
    """Add filters to the query builder from the given parameters and add the parameters to the params dict.

    Args:
        qb (QueryBuilder): The query builder object.
        relation_name (str): The name of the relation to add the filters to.
        filter_params (dict): The parameters to add as filters.
        params (dict): The parameters to add the filter parameters to.
    """
    for key, value in filter_params.items():
        if value:  # Only add the filter if the parameter has a value
            param_name = key.rsplit("_", 1)[0]
            qb.add_where(relation_name + param_name, qb.get_sql_operator(key), value, params)
