from pydantic import BaseModel

class DirectionModel(BaseModel):
    begin: str
    end: str