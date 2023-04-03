from pydantic import BaseModel
from datetime import datetime
from app.routers.v1.cell.models.direction import DirectionModel
from app.routers.v1.cell.models.ship import ShipModel

class CellFact(BaseModel):
    x: int
    y: int
    trajectory_sub_id: int
    entry_timestamp: datetime
    exit_timestamp: datetime
    navigational_status: str
    direction: DirectionModel
    sog: float
    delta_cog: float
    draught: int
    stopped: bool
    ship: ShipModel