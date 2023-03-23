"""Define the allowed heatmap types."""
from enum import Enum


class HeatmapType(str, Enum):
    """Enum of available heatmap types."""

    count = "count"
