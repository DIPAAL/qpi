"""Pydantic models/schemas, defining valid data shapes for ship API endpoints."""
from pydantic import BaseModel
from enum import Enum

# Enums
class SearchMethodSpatial(str, Enum):
    """Enum for all search methods."""
    cell_50m = "cell_50m"
    cell_200m = "cell_200m"
    cell_1000m = "cell_1000m"
    cell_5000m = "cell_5000m"
    trajectories = "trajectories"


# ORM Schemas/Models
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

