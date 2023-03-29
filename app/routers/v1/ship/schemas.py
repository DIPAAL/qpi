"""Pydantic models/schemas, defining valid data shapes for ship API endpoints."""
from pydantic import BaseModel


class DimShipBase(BaseModel):
    ship_type_id: int
    imo: int
    name: str
    callsign: str
    a: float
    b: float
    c: float
    d: float
    location_system_type: str


class DimShip(DimShipBase):
    ship_id: int
    mmsi: int
    
    class Config:
        orm_mode = True
    pass


class DimShipTypeBase(BaseModel):
    mobile_type: str
    ship_type: str


class DimShipType(DimShipTypeBase):
    ship_type_id: int

    class Config:
        orm_mode = True
    pass