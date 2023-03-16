"""
Ship router

Contains endpoints to retrieve information about a specific ship or a set of ships.
"""

from fastapi import APIRouter, Depends
from app.dependencies import get_dw_cursor
from app.api_constants import DWTABLE

router = APIRouter()

dim_ship = DWTABLE.dim_ship
dim_ship_type = DWTABLE.dim_ship_type


@router.get("/{mmsi}")
def mmsi(mmsi: int, dw_cursor=Depends(get_dw_cursor)):
    """"""
    dw_cursor.execute(f"SELECT * FROM {dim_ship} INNER JOIN {dim_ship_type} ON {dim_ship}.ship_type_id = {dim_ship_type}.ship_type_id WHERE mmsi = {mmsi}")
    return dw_cursor.fetchone()
