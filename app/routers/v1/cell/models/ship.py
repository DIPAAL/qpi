"""Model partly representing a ship in the DIPAAL data warehouse."""
from pydantic import BaseModel
from app.routers.v1.heatmap.models.mobile_type import MobileType
from app.routers.v1.heatmap.models.ship_type import ShipType


class Ship(BaseModel):
    """Partly ship model."""

    mmsi: int
    imo: int
    name: str
    type: ShipType
    mobile: MobileType
    flag_state: str
