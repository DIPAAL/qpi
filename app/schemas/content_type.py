"""Schema representing the content type which the data is in."""
from enum import Enum


class ContentType(str, Enum):
    """The content type of the data."""

    GEOJSON = "GEOJSON"
    MFJSON = "MFJSON"
