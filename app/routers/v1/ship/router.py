"""
Ship router.

Contains endpoints to retrieve information about a specific ship or a set of ships.
"""

from fastapi import APIRouter, Depends, Path, HTTPException, Query
from app.dependencies import get_dw
from sqlalchemy.orm import Session
from app.routers.v1.ship import models, schemas, crud
from app.datawarehouse import engine

models.Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.get("/", response_model=list[schemas.Ship])
async def ships(
        skip: int = 0,
        limit: int = 100,
        ship_id: int | None = None,
        mmsi_in: list[int] | None = Query(default=None),
        mmsi_nin: list[int] | None = Query(default=None),
        mmsi_gt: int | None = Query(default=None),
        mmsi_gte: int | None = Query(default=None),
        mmsi_lte: int | None = Query(default=None),
        mmsi_lt: int | None = Query(default=None),
        mid_in: list[int] | None = Query(default=None),
        mid_nin: list[int] | None = Query(default=None),
        mid_gt: int | None = Query(default=None),
        mid_gte: int | None = Query(default=None),
        mid_lte: int | None = Query(default=None),
        mid_lt: int | None = Query(default=None),
        imo_in: list[int] | None = Query(default=None),
        imo_nin: list[int] | None = Query(default=None),
        imo_gt: int | None = Query(default=None),
        imo_gte: int | None = Query(default=None),
        imo_lte: int | None = Query(default=None),
        imo_lt: int | None = Query(default=None),
        a_in: list[int] | None = Query(default=None),
        a_nin: list[int] | None = Query(default=None),
        a_gt: int | None = Query(default=None),
        a_gte: int | None = Query(default=None),
        a_lte: int | None = Query(default=None),
        a_lt: int | None = Query(default=None),
        b_in: list[int] | None = Query(default=None),
        b_nin: list[int] | None = Query(default=None),
        b_gt: int | None = Query(default=None),
        b_gte: int | None = Query(default=None),
        b_lte: int | None = Query(default=None),
        b_lt: int | None = Query(default=None),
        c_in: list[int] | None = Query(default=None),
        c_nin: list[int] | None = Query(default=None),
        c_gt: int | None = Query(default=None),
        c_gte: int | None = Query(default=None),
        d_in: list[int] | None = Query(default=None),
        d_nin: list[int] | None = Query(default=None),
        d_gt: int | None = Query(default=None),
        d_gte: int | None = Query(default=None),
        d_lte: int | None = Query(default=None),
        d_lt: int | None = Query(default=None),
        name_in: list[str] | None = Query(default=None),
        name_nin: list[str] | None = Query(default=None),
        callsign_in: list[str] | None = Query(default=None),
        callsign_nin: list[str] | None = Query(default=None),
        location_system_type_in: list[str] | None = Query(default=None),
        location_system_type_nin: list[str] | None = Query(default=None),
        flag_region_in: list[str] | None = Query(default=None),
        flag_region_nin: list[str] | None = Query(default=None),
        flag_state_in: list[str] | None = Query(default=None),
        flag_state_nin: list[str] | None = Query(default=None),
        mobile_type_in: list[str] | None = Query(default=None),
        mobile_type_nin: list[str] | None = Query(default=None),
        ship_type_in: list[str] | None = Query(default=None),
        ship_type_nin: list[str] | None = Query(default=None),
        dw: Session = Depends(get_dw)
):
    """
    Returns a dictionary with information about a specific ship or a set of ships.

    Args:
        skip (int, optional): Number of records to skip. Defaults to 0.
        limit (int, optional): Number of records to return. Defaults to 100.
        ship_id (int, optional): ID of the ship to return. Defaults to None.
        mmsi_(filter) : MMSI of the ship. Can be filtered with the following operators: in, nin, gt, gte, lte, lt.
        mid_(filter) : MID of the ship. Can be filtered with the following operators: in, nin, gt, gte, lte, lt.
        imo_(filter) : IMO of the ship. Can be filtered with the following operators: in, nin, gt, gte, lte, lt.
        a_(filter) : Distance from the transponder to the bow of the ship. Can be filtered with the following operators: in, nin, gt, gte, lte, lt.
        b_(filter) : Distance from the transponder to the stern of the ship. Can be filtered with the following operators: in, nin, gt, gte, lte, lt.
        c_(filter) : Distance from the transponder to the port side of the ship. Can be filtered with the following operators: in, nin, gt, gte, lte, lt.
        d_(filter) : Distance from the transponder to the starboard side of the ship. Can be filtered with the following operators: in, nin, gt, gte, lte, lt.
        name_(filter) : Name of the ship. Can be filtered with the following operators: in, nin.
        callsign_(filter) : Callsign of the ship. Can be filtered with the following operators: in, nin.
        location_system_type_(filter) : Location system type of the ship. Can be filtered with the following operators: in, nin.
        flag_region_(filter) : Flag region of the ship. Can be filtered with the following operators: in, nin.
        flag_state_(filter) : Flag state of the ship. Can be filtered with the following operators: in, nin.
        mobile_type_(filter) : Mobile type of the ship. Can be filtered with the following operators: in, nin.
        ship_type_(filter) : Ship type of the ship. Can be filtered with the following operators: in, nin.
    Returns:
        dict: Dictionary with information about a specific ship or a set of ships.
    """
    # Copy all parameters to a dictionary
    params = locals().copy()
    query = dw.query(models.DimShip).join(models.DimShipType)

    # If ship_id is specified, only return that ship
    if ship_id is not None:
        query = query.filter(models.DimShip.ship_id == ship_id)

    else:
        # Remove parameters that are not part of the model and ship_id
        rem_list = ["dw", "skip", "limit", "ship_id"]

        for key in rem_list:
            del params[key]

        for attr in params:
            if params[attr] is not None:
                # Check if the attribute is a dim ship type attribute
                if "mobile_type" or "ship_type" in attr:
                    if "_in" in attr:
                        query = query.filter(getattr(models.DimShipType, attr[:-3]).in_(params[attr]))
                    elif "_nin" in attr:
                        query = query.filter(getattr(models.DimShipType, attr[:-4]).not_in(params[attr]))
                elif "_in" in attr:
                    query = query.filter(getattr(models.DimShip, attr[:-3]).in_(params[attr]))
                elif "_nin" in attr:
                    query = query.filter(getattr(models.DimShip, attr[:-4]).not_in(params[attr]))
                elif "_gt" in attr:
                    query = query.filter(getattr(models.DimShip, attr[:-3]) > params[attr])
                elif "_gte" in attr:
                    query = query.filter(getattr(models.DimShip, attr[:-4]) >= params[attr])
                elif "_lt" in attr:
                    query = query.filter(getattr(models.DimShip, attr[:-3]) < params[attr])
                elif "_lte" in attr:
                    query = query.filter(getattr(models.DimShip, attr[:-4]) <= params[attr])
                else:
                    raise HTTPException(status_code=400, detail=f"Invalid filter: {attr}")

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

