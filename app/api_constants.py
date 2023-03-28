"""Constants used within the API module."""
from enum import Enum
from sqlalchemy.ext.declarative import declarative_base

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

# All column names in the dim_ship and dim_ship_type attributes
class DIMSHIP(str, Enum):
    a = "a"
    b = "b"
    c = "c"
    d = "d"
    ship_id = "ship_id"
    ship_type_id = "ship_type_id"
    imo = "imo"
    mmsi = "mmsi"
    name = "name"
    callsign = "callsign"
    location_system_type = "location_system_type"
    mobile_type = "mobile_type"
    ship_type = "ship_type"