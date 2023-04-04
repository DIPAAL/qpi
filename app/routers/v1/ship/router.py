"""
Ship router.

Contains endpoints to retrieve information about a specific ship or a set of ships.
"""
from fastapi import APIRouter, Depends, Path, HTTPException, Query
from app.dependencies import get_dw
from sqlalchemy.orm import Session
from app.routers.v1.ship import models, schemas, crud
from app.datawarehouse import engine
import datetime
import pandas as pd

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
        mmsi_(filter) (list[int], int, optional): MMSI of the ship. Can be filtered with the following operators: in, nin, gt, gte, lte, lt.
        mid_(filter) (list[int], int, optional): MID of the ship. Can be filtered with the following operators: in, nin, gt, gte, lte, lt.
        imo_(filter) (list[int], int, optional): IMO of the ship. Can be filtered with the following operators: in, nin, gt, gte, lte, lt.
        a_(filter) (list[int], int, optional): Distance from the transponder to the bow of the ship. Can be filtered with the following operators: in, nin, gt, gte, lte, lt.
        b_(filter) (list[int], int, optional): Distance from the transponder to the stern of the ship. Can be filtered with the following operators: in, nin, gt, gte, lte, lt.
        c_(filter) (list[int], int, optional): Distance from the transponder to the port side of the ship. Can be filtered with the following operators: in, nin, gt, gte, lte, lt.
        d_(filter) (list[int], int, optional): Distance from the transponder to the starboard side of the ship. Can be filtered with the following operators: in, nin, gt, gte, lte, lt.
        name_(filter) (list[str], optional): Name of the ship. Can be filtered with the following operators: in, nin.
        callsign_(filter) (list[str], optional): Callsign of the ship. Can be filtered with the following operators: in, nin.
        location_system_type_(filter) (list[str], optional): Location system type of the ship. Can be filtered with the following operators: in, nin.
        flag_region_(filter) (list[str], optional): Flag region of the ship. Can be filtered with the following operators: in, nin.
        flag_state_(filter) (list[str], optional): Flag state of the ship. Can be filtered with the following operators: in, nin.
        mobile_type_(filter) (list[str], optional): Mobile type of the ship. Can be filtered with the following operators: in, nin.
        ship_type_(filter) (list[str], optional): Ship type of the ship. Can be filtered with the following operators: in, nin.
    Returns:

        dict: Dictionary with information about a specific ship or a set of ships.
    """
    # Copy all local variables to a dictionary.
    # Done first to avoid copying variables that are not defined by the client.
    params = locals().copy()

    # Join the dim ship and dim ship type tables to get the ship type information for each ship
    query = dw.query(models.DimShip).join(models.DimShipType)

    # If ship_id is specified, only return information about that ship.
    if ship_id is not None:
        query = query.filter(models.DimShip.ship_id == ship_id)

    else:
        # List of parameters that are not part of the dim_ship or dim_ship_type and ship_id
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

@router.get("/bounds")
async def bounds(
        # Temporal bounds
        from_date: datetime.datetime = Query(default="2022-01-02T00:00:00Z"),
        to_date: datetime.datetime = Query(default="2022-01-02T00:00:00Z"),

        # Spatial bounds
        search_method : schemas.SearchMethodSpatial = Query(default="trajectories"),
        min_x: int = Query(default=None),
        min_y: int = Query(default=None),
        max_x: int = Query(default=None),
        max_y: int = Query(default=None),


        dw: Session = Depends(get_dw)

):
    params = {
        "from_date": int(from_date.strftime("%Y%m%d")),
        "to_date": int(to_date.strftime("%Y%m%d"))
    }
    df = pd.read_sql(crud.get_ships_by_temporal_bounds(dw, params["from_date"], params["to_date"]), dw.bind.connect())
    return df.to_dict(orient="records")


@router.get("/{limit}", response_model=list[schemas.Ship])
async def limit(skip: int = 0, limit: int = 100, dw: Session = Depends(get_dw)):
    ships = crud.get_ships(dw, skip=skip, limit=limit)
    return ships

@router.get("/{mmsi}", response_model=schemas.Ship)
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

