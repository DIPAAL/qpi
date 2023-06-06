"""Schema representing the content type which the data is in."""
from enum import Enum


class TimeSeriesRepresentation(str, Enum):
    """The content type of the data."""

    GEOJSON = "GeoJSON"
    MFJSON = "MFJSON"
