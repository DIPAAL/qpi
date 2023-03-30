"""Pydantic models/schemas, defining valid data shapes for ship API endpoints."""
from pydantic import BaseModel

class DimShipType(BaseModel):
    # ship_type_id: int
    mobile_type: str
    ship_type: str

    class Config:
        orm_mode = True
    pass

class DimShip(BaseModel):
    ship_id: int
    # ship_type_id: int
    imo: int
    mmsi: int
    mid: int
    a: float
    b: float
    c: float
    d: float
    name: str
    callsign: str
    flag_region: str
    flag_state: str
    location_system_type: str

    class Config:
        orm_mode = True
    pass

class Ship(DimShip):
    dim_ship_type: DimShipType

    class Config:
        orm_mode = True
    pass

