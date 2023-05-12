"""Modules for output of basic SQL queries."""
from pydantic import BaseModel


class CountRows(BaseModel):
    """Pydantic model for portraying the number of rows in a table."""

    count: int = 234


class ColumnNames(BaseModel):
    """Pydantic model for portraying the column names of a table."""

    columns: list[str] = ["time", "time_id", "hour_of_day", "minute_of_hour", "second_of_minute"]
