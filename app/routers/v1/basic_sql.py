"""FastAPI router for basic SQL queries."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies import get_dw
from app.schemas.relations import DWRELATION
from app.schemas.basic_output import CountRows, ColumnNames

router = APIRouter()


@router.get("/", response_model=list[str])
def table():
    """
    Get a list of tables in the database.
    """
    return [table.value for table in DWRELATION]

class count_rows():
    pass

@router.get("/{table}/count", response_model=CountRows)
def count_rows(table: DWRELATION, db: Session = Depends(get_dw)):
    """
    Get the number of rows in the given table.
    """
    return {
        "count": db.execute(text(f"SELECT COUNT(*) FROM {table.name}")).fetchall()[0][0]
    }


@router.get("/{table}/columns", response_model=ColumnNames)
def column_names(table: DWRELATION, db=Depends(get_dw)):
    """
    Get the column names of a given table.
    """
    return {
        "columns": [column for column in db.execute(text(f"SELECT * FROM {table.name} LIMIT 0")).keys()]
    }
