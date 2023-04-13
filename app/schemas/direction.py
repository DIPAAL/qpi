"""Model representing a direction in the DIPAAL data warehouse."""
from pydantic import BaseModel, Field


class Direction(BaseModel):
    """Direction model."""

    begin: str = Field(description='The coordinal direction where the ship entered the cell, '
                                   'unknown indicates the ship started in the cell')
    end: str = Field(description='The coordinal direction where the ship exited the cell, '
                                 'unknown indicates the ship ended in the cell')
