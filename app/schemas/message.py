"""Model representing a message."""
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Message model for simple message responses."""

    message: str = Field(description='The message')
