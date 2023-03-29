"""Pydantic models/schemas, defining valid data shapes for ship API endpoints."""
from pydantic import BaseModel


class DimShipBase(BaseModel):
    name: str
    callsign: str
    location_system_type: str
    flag_region: str
    flag_state: str
    a: float
    b: float
    c: float
    d: float
    ship_type_id: int
    imo: int
    mid: int


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

class DimShipDetail(DimShip):
    dim_ship_type: DimShipType

    class Config:
        orm_mode = True
    pass


