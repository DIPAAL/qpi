"""Define the allowed spatial resolutions."""
from enum import Enum


class SpatialResolution(str, Enum):
    """Enum of available temporal resolutions."""

    five_kilometers = "5000m"
    kilometer = "1000m"
    two_hundred_meters = "200m"
    fifty_meters = "50m"

    def __int__(self):
        """Return the spatial resolution as an integer."""
        return int(self.value[:-1])
