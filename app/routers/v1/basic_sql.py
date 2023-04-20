"""FastAPI router for basic SQL queries."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies import get_dw
from app.schemas.relations import DWRELATION


router = APIRouter()


@router.get("/")
def table():
    """
    Get a list of tables in the database.

    Returns:
        A list of tables in the database
    """
    return [table.value for table in DWRELATION]


@router.get("/{table}/count")
def count_rows(table: DWRELATION, db: Session = Depends(get_dw)):
    """
    Count the number of rows in a table.

    Args:
        db: A DB session
        table: A table in the database

    Returns:
        The number of rows in the table
    """
    return {
        "count": db.execute(text(f"SELECT COUNT(*) FROM {table.name}")).fetchall()[0][0]
    }


@router.get("/{table}/columns")
def column_names(table: DWRELATION, db=Depends(get_dw)):
    """
    Get the column names of a table.

    Args:
        db: A DB session.
        table: A table in the database

    Returns:
        A list of column names
    """
    return {
        "columns": [column for column in db.execute(text(f"SELECT * FROM {table.name} LIMIT 0")).keys()]
    }
