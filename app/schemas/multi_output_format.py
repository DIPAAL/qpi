"""Define the allowed output formats for multi heatmaps."""
from enum import Enum


class MultiOutputFormat(str, Enum):
    """Output format for rasters enum."""

    mp4 = "mp4"
    gif = "gif"
