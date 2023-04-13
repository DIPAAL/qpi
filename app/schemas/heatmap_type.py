"""Define the allowed heatmap types."""
from enum import Enum


class HeatmapType(str, Enum):
    """Enum of available heatmap types."""

    count = "count"
    time = "time"
    delta_cog = "delta_cog"
    delta_heading = "delta_heading"
    max_draught = "max_draught"
