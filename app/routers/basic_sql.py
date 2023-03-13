"""FastAPI router for basic SQL queries."""

from fastapi import APIRouter
from app.dependencies import CURSOR, DWTable
# from pydantic import BaseModel


router = APIRouter()


@router.get("/count_row_table/{table}")
def count_row_table(table: DWTable):
    """
    Count the number of rows in a table.

    Args:
        table: A table in the database

    Returns:
        The number of rows in the table
    """
    CURSOR.execute(f"SELECT COUNT(*) FROM {table}")
    return CURSOR.fetchall()


@router.get("/get_coloumn_names/{table}")
def get_column_names(table: DWTable):
    """
    Get the column names of a table.

    Args:
        table: A table in the database

    Returns:
        A list of column names
    """
    CURSOR.execute(f"SELECT * FROM {table} LIMIT 0")
    return [desc[0] for desc in CURSOR.description]
