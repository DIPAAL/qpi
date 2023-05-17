"""Pydantic model representing the number of rows in a relation."""
from pydantic import BaseModel, Field


class CountRows(BaseModel):
    """Pydantic model for portraying the number of rows in a relation."""

    count: int = Field(description='The number of rows in the relation')
