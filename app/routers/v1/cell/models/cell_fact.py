from datetime import datetime
from typing import List
from pydantic import BaseModel
from app.routers.v1.cell.models.direction import Direction
from app.routers.v1.cell.models.ship import Ship

class FactCell(BaseModel):
    x: int
    y: int
    trajectory_sub_id: int
    entry_timestamp: datetime
    exit_timestamp: datetime
    navigational_status: str
    direction: List[Direction]
    sog: float
    delta_cog: float
    delta_heading: float
    draught: float
    stopped: bool
    ship: Ship