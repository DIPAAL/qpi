"""Model representing a ship in the DIPAAL data warehouse."""
from pydantic import BaseModel, Field
from app.schemas.mobile_type import MobileType
from app.schemas.ship_type import ShipType

class Ship(BaseModel):
    """Ship Model."""

    ship_id: int
    name: str
    callsign: str
    mmsi: int
    imo: int
    flag_region: str
    flag_state: str
    mobile_type: MobileType
    ship_type: ShipType
    location_system_type: str
    a: int
    b: int
    c: int
    d: int