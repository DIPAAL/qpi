"""Define the allowed output formats for single heatmaps."""
from enum import Enum


class SingleOutputFormat(str, Enum):
    """Output format for rasters enum."""

    png = "png"
    tiff = "tiff"
