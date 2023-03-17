"""
Ship router

Contains endpoints to retrieve information about a specific ship or a set of ships.
"""

from fastapi import APIRouter, Depends, Path
from app.dependencies import get_dw_cursor
from app.api_constants import DWTABLE
from helper_functions import create_session_to_dw

router = APIRouter()

dim_ship = DWTABLE.dim_ship
dim_ship_type = DWTABLE.dim_ship_type

session_dw = create_session_to_dw()


@router.get("/{mmsi}")
def mmsi(mmsi: int=Path(..., le=999_999_999), dw_cursor=Depends(get_dw_cursor)):
    """
    Get information about a ship by MMSI.
    Args:
        mmsi: The MMSI of the ship
        dw_cursor: A cursor to the data warehouse database

    Returns: A list containing information about the ship

    """
    dw_cursor.execute(f"SELECT * FROM {dim_ship} INNER JOIN {dim_ship_type} ON {dim_ship}.ship_type_id = {dim_ship_type}.ship_type_id WHERE mmsi = {mmsi}")
    return dw_cursor.fetchone()

