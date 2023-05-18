"""Pydantic model for portraying the column names of a relation."""""
from pydantic import BaseModel, Field


class ColumnNames(BaseModel):
    """Pydantic model for portraying the column names of a relation."""

    columns: list[str] = Field(description='The column names of the table.')
