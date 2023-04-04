"""Enum representing the cell sizes in the DIPAAL data warehouse."""
from enum import IntEnum


class CellSize(IntEnum):
    """Cell size enum."""

    meter_50 = 50,
    meter_200 = 200,
    meter_1000 = 1000,
    meter_5000 = 5000
