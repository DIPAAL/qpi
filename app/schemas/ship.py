"""Model representing a ship in the DIPAAL data warehouse."""
from pydantic import BaseModel, Field
from app.schemas.mobile_type import MobileType
from app.schemas.ship_type import ShipType


class Ship(BaseModel):
    """Ship Model."""

    ship_id: int = Field(description='The id of the ship.')
    name: str = Field(description='The name of the ship.')
    callsign: str = Field(description='The callsign of the ship.')
    mmsi: int = Field(description='The mmsi of the ship.')
    imo: int = Field(description='The imo of the ship.')
    flag_region: str = Field(description='The flag region of the ship.')
    flag_state: str = Field(description='The flag state of the ship.')
    mobile_type: MobileType = Field(description='The mobile type of the ship.')
    ship_type: ShipType = Field(description='The ship type of the ship.')
    location_system_type: str = Field(description='The location system type of the ship.')
    a: int = Field(description='The distance from the bow to the antenna.')
    b: int = Field(description='The distance from the stern to the antenna.')
    c: int = Field(description='The distance from the port side to the antenna.')
    d: int = Field(description='The distance from the starboard side to the antenna.')
    length: int = Field(description='The length of the ship.')
    width: int = Field(description='The width of the ship.')
