"""Model representing a message."""
from pydantic import BaseModel


class Message(BaseModel):
    """Message model for simple message responses."""

    message: str
