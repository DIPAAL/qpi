from pydantic import BaseModel
from app.routers.v1.heatmap.models.mobile_type import MobileType
from app.routers.v1.heatmap.models.ship_type import ShipType

class ShipModel(BaseModel):
    mmsi: int
    imo: int
    name: str
    type: ShipType
    mobile_type: MobileType
    flag_state: str