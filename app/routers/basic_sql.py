"""FastAPI router for basic SQL queries."""

from fastapi import APIRouter, Depends
from ..dependencies import get_dw_cursor
from ..api_constants import DWTABLE


router = APIRouter()

@router.get("api/v1/misc/{table}/count_rows")
def count_row_table(table: DWTABLE, dw_cursor=Depends(get_dw_cursor)):
    """
    Count the number of rows in a table.

    Args:
        dw_cursor: A cursor to the data warehouse database
        table: A table in the database

    Returns:
        The number of rows in the table
    """
    dw_cursor.execute(f"SELECT COUNT(*) FROM {table}")
    return dw_cursor.fetchall()


@router.get("api/v1/misc/{table}/column_names")
def get_column_names(table: DWTABLE, dw_cursor=Depends(get_dw_cursor)):
    """
    Get the column names of a table.

    Args:
        dw_cursor: A cursor to the data warehouse database
        table: A table in the database

    Returns:
        A list of column names
    """
    dw_cursor.execute(f"SELECT * FROM {table} LIMIT 0")
    return [desc[0] for desc in dw_cursor.description]
