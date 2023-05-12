"""Model representing a ship in the DIPAAL data warehouse."""
from pydantic import BaseModel
from app.schemas.mobile_type import MobileType
from app.schemas.ship_type import ShipType


class Ship(BaseModel):
    """Ship Model."""

    ship_id: int = 1
    name: str = "DANPILOT BRAVO"
    callsign: str = "OXKI2"
    mmsi: int = 219022257
    imo: int = 9812092
    flag_region: str = 219
    flag_state: str = "Denmark"
    mobile_type: MobileType = MobileType.class_a
    ship_type: ShipType = ShipType.pilot
    location_system_type: str = "AIS"
    a: int = 17
    b: int = 3
    c: int = 2
    d: int = 4
