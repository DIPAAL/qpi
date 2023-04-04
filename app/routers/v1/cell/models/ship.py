from pydantic import BaseModel

class Ship(BaseModel):
    mmsi: int
    imo: int
    name: str
    type: str
    mobile: str
    flag_state: str