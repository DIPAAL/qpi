from pydantic import BaseModel

class Message(BaseModel):
    """Message model for health check response."""
    message: str