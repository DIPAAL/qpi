"""Dependencies used by the API endpoints."""

from qpi.helper_functions import get_connection
from constants import ROOT_DIR
from enum import Enum
import os


CONN = get_connection()
CURSOR = CONN.cursor()


class DWTable(str, Enum):
    """All data warehouse tables."""

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


class MiscTable(str, Enum):
    """All miscellaneous tables."""

    audit_log = "audit_log"
    benchmark_result = "benchmark_result"


def readfile(path_from_root):
    """Read a file from the root directory."""
    path = os.path.join(ROOT_DIR, f'{path_from_root}')
    with open(path, "r") as f:
        return f.read()
