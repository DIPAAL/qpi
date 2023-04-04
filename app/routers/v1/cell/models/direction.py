from pydantic import BaseModel

class Direction(BaseModel):
    begin: str
    end: str