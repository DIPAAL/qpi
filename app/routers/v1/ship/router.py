"""
Ship router

Contains endpoints to retrieve information about a specific ship or a set of ships.
"""

from fastapi import APIRouter, Depends, Path, HTTPException, Query
from app.dependencies import get_dw
from sqlalchemy.orm import Session
from app.routers.v1.ship import models, schemas, crud
from app.datawarehouse import engine
from helper_functions import query_apply_filters

models.Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.get("/", response_model=list[schemas.DimShip])
async def ships(
        skip: int = 0,
        limit: int = 100,
        ship_id: int | None = None,
        mmsi: list[int] | None = Query(default=None),
        mid: list[int] | None = Query(default=None),
	    imo: list[int] | None = Query(default=None),
	    a: list[int] | None = Query(default=None),
	    b: list[int] | None = Query(default=None),
	    c: list[int] | None = Query(default=None),
	    d: list[int] | None = Query(default=None),
	    name: list[str] | None = Query(default=None),
	    callsign: list[str] | None = Query(default=None),
	    location_system_type: list[str] | None = Query(default=None),
	    flag_region: list[str] | None = Query(default=None),
	    flag_state: list[str] | None = Query(default=None),
	    mobile_type: list[str] | None = Query(default=None),
	    ship_type: list[str] | None = Query(default=None),
        dw: Session = Depends(get_dw)
):
    # construct query based on parameters
    params = locals().copy()
    query = dw.query(models.DimShip)

    if ship_id is not None:
        query = query.filter(models.DimShip.ship_id == ship_id)

    else:
        rem_list = ["dw", "skip", "limit", "ship_id"]

        for key in rem_list:
            del params[key]

        for attr in params:
            if params[attr] is not None:
                query = query.filter(getattr(models.DimShip, attr).in_(params[attr]))

    return query.offset(skip).limit(limit).all()


@router.get("/{limit}", response_model=list[schemas.DimShip])
async def limit(skip: int = 0, limit: int = 100, dw: Session = Depends(get_dw)):
    ships = crud.get_ships(dw, skip=skip, limit=limit)
    return ships

@router.get("/{mmsi}", response_model=schemas.DimShip)
async def mmsi(
        mmsi: int = Path(..., le=999_999_999),
        dw : Session = Depends(get_dw)
):
    """
    Get information about a ship by MMSI.
    Args:
        mmsi: The MMSI of the ship
        dw: A session to the data warehouse

    Returns: A list containing information about the ship

    """
    dw_ship = crud.get_ship_by_mmsi(dw, mmsi)
    if dw_ship is None:
        raise HTTPException(status_code=404, detail="Ship not found")
    return dw_ship

