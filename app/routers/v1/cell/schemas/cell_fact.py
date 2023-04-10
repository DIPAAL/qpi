"""Model representing a cell fact in the DIPAAL data warehouse."""

from datetime import datetime
from pydantic import BaseModel, Field
from app.routers.v1.cell.schemas.direction import Direction
from app.routers.v1.cell.schemas.ship import Ship


class FactCell(BaseModel):
    """Fact cell model."""

    x: int = Field(description='The x-coordinate of the DIPAAL cell that contains the cell fact')
    y: int = Field(description='The y-coordinate of the DIPAAL cell that contains the cell fact')
    trajectory_sub_id: int = Field(description='The id that together with a date uniquely identifies a trajectory')
    entry_timestamp: datetime = Field(description='Timestamp that specifies when the ship entered the cell')
    exit_timestamp: datetime = Field(description='Timestamp that specifies when the ship left the cell')
    navigational_status: str = Field(description='The navigational status of the ship during its stay in the cell')
    direction: Direction = Field(description='Describes the coordinal direction which the ship entered and exited the cell')
    sog: float = Field(description='The speed over ground of the ship while within the cell')
    delta_cog: float = Field(description='Describes how much the course over ground of the ship changed while within the cell')
    delta_heading: float = Field(description='Describes how much the heading of the ship changed while within the cell')
    draught: float | None = Field(description='The maximum draught set by the ship while within the cell')
    stopped: bool = Field(description='Indicated whether the ship has been inferred to be stopped within the cell')
    ship: Ship = Field(description='Information about the cell that created the cell fact')
