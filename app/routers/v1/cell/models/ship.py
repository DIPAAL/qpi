"""Model partly representing a ship in the DIPAAL data warehouse."""
from pydantic import BaseModel


class Ship(BaseModel):
    """Partly ship model."""

    mmsi: int
    imo: int
    name: str
    type: str
    mobile: str
    flag_state: str
