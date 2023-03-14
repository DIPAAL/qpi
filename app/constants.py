"""Constants used within the API module."""
from enum import Enum
from helper_functions import get_connection

CONN = get_connection()
CURSOR = CONN.cursor()


class DWTABLE(str, Enum):
    """Enum for all data warehouse tables."""

    dim_cell_50m = "dim_cell_50m"
    dim_cell_200m = "dim_cell_200m"
    dim_cell_1000m = "dim_cell_1000m"
    dim_cell_5000m = "dim_cell_5000m"
    dim_date = "dim_date"
    dim_direction = "dim_direction"
    dim_heatmap_type = "dim_heatmap_type"
    dim_nav_status = "dim_nav_status"
    dim_raster = "dim_raster"
    dim_ship = "dim_ship"
    dim_ship_type = "dim_ship_type"
    dim_time = "dim_time"
    dim_trajectory = "dim_trajectory"
    fact_cell_50m = "fact_cell_50m"
    fact_cell_200m = "fact_cell_200m"
    fact_cell_1000m = "fact_cell_1000m"
    fact_cell_5000m = "fact_cell_5000m"
    fact_cell_heatmap = "fact_cell_heatmap"
    fact_trajectory = "fact_trajectory"


class MISCTABLE(str, Enum):
    """All miscellaneous tables."""

    audit_log = "audit_log"
    benchmark_result = "benchmark_result"
