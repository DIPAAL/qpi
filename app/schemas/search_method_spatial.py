"""Schema for spatial search methods."""
from enum import Enum

class SearchMethodSpatial(str, Enum):
    """Enum for all search methods."""

    cell_50m = "cell_50m"
    cell_200m = "cell_200m"
    cell_1000m = "cell_1000m"
    cell_5000m = "cell_5000m"
    trajectories = "trajectories"