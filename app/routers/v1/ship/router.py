"""
Ship router

Contains endpoints to retrieve information about a specific ship or a set of ships.
"""

from fastapi import APIRouter, Depends, Path, HTTPException
from app.dependencies import get_dw_cursor
from app.api_constants import DWTABLE
from sqlalchemy.orm import Session
from app.routers.v1.ship import models, schemas, crud
from app.datawarehouse import engine

models.Base.metadata.create_all(bind=engine)

router = APIRouter()

@router.get("/", response_model=list[schemas.DimShip])
def ships(skip: int = 0, limit: int = 100, dw: Session = Depends(get_dw_cursor)):
    ships = crud.get_ships(dw, skip=skip, limit=limit)
    return ships

@router.get("/{mmsi}", response_model=schemas.DimShip)
async def test(
        mmsi: int = Path(..., le=999_999_999),
        dw : Session = Depends(get_dw_cursor)
):
    dw_ship = crud.get_ship_by_mmsi(dw, mmsi)
    if dw_ship is None:
        raise HTTPException(status_code=404, detail="Ship not found")
    return dw_ship


dim_ship = DWTABLE.dim_ship
dim_ship_type = DWTABLE.dim_ship_type

@router.get("/old/{mmsi}")
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
