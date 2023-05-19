"""Model partly representing a ship in the DIPAAL data warehouse."""
from pydantic import BaseModel, Field
from app.schemas.mobile_type import MobileType
from app.schemas.ship_type import ShipType


class CellShip(BaseModel):
    """Partly ship model."""

    mmsi: int = Field(description='The ships Maritime Mobile Service Identity.')
    imo: int = Field(description='The ships unique identifier provided by the International Maritime Organization.')
    name: str = Field(description='The name of the ship.')
    type: ShipType = Field(description='The type of the ship.')
    mobile: MobileType = Field(description='The class of the AIS transponder equipped on the ship.')
    flag_state: str = Field(description='The flag state that the ship currently sails under.')
