"""Model representing a direction in the DIPAAL data warehouse."""
from pydantic import BaseModel


class Direction(BaseModel):
    """Direction model."""

    begin: str
    end: str
