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
# FIXME: This is a temporary fix to get the sql files to work
from helper_functions import brackets_and_content_to_string, get_file_contents
from sqlalchemy import text
import os

models.Base.metadata.create_all(bind=engine)

router = APIRouter()

SQL_PATH = os.path.join(os.path.dirname(__file__), "sql")
SQL_PATH_CELLS = os.path.join(SQL_PATH, "cells")
SQL_PATH_TRAJECTORIES = os.path.join(SQL_PATH, "trajectories")

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
        skip: int = 0,
        limit: int = 100,

        # Temporal bounds
        from_date: datetime.datetime = Query(default="2021-01-02T00:00:00Z"),
        to_date: datetime.datetime = Query(default="2022-01-02T00:00:00Z"),

        # Spatial bounds
        search_method : schemas.SearchMethodSpatial = Query(default="cell_1000m"),
        min_x: int = Query(default=4050000),
        min_y: int = Query(default=4051000),
        max_x: int = Query(default=3075000),
        max_y: int = Query(default=3076000),

        dw: Session = Depends(get_dw)

):
    params = {
        "xmin": min_x,
        "ymin": min_y,
        "xmax": max_x,
        "ymax": max_y,
        "from_date": int(from_date.strftime("%Y%m%d")),
        "to_date": int(to_date.strftime("%Y%m%d")),
        "limit": limit,
        "offset": skip,
    }
    query_type = []

    # FIXME: Reimplement this with a more elegant solution using dictionaries
    # Check if only temporal bounds are specified
    temporal_params = [params["from_date"], params["to_date"]]
    if None not in temporal_params:
        query_type.append("Temporal")

    # Check if only spatial bounds are specified
    spatial_params = [params["xmin"], params["ymin"], params["xmax"], params["ymax"]]
    if None not in spatial_params:
        query_type.append("Spatial")
        if None in spatial_params:
            raise HTTPException(status_code=400, detail="Spatial bounds are not fully specified.")

    if query_type:
        if "Temporal" in query_type and "Spatial" in query_type:
            if search_method is "trajectories":
                path = os.path.join(SQL_PATH_TRAJECTORIES, "spatial_temporal_bounds.sql")
            else:
                path = os.path.join(SQL_PATH_CELLS, "spatial_temporal_bounds.sql")
        elif "Temporal" in query_type:
            if search_method is "trajectories":
                path = os.path.join(SQL_PATH_TRAJECTORIES, "temporal_bounds.sql")
            else:
                path = os.path.join(SQL_PATH_CELLS, "temporal_bounds.sql")
        elif "Spatial" in query_type:
            if search_method is "trajectories":
                path = os.path.join(SQL_PATH_TRAJECTORIES, "spatial_bounds.sql")
            else:
                path = os.path.join(SQL_PATH_CELLS, "spatial_bounds.sql")
        else:
            # TODO: Add filter support so simple queries can be performed
            raise HTTPException(status_code=400, detail="Invalid query")

    query = get_file_contents(path)
    if search_method is not "trajectories":
        query = brackets_and_content_to_string(query, "CELL_SIZE", search_method.value)
    df = pd.read_sql(text(query), dw.bind.connect(), params=params)
    return df.to_dict(orient="records")


@router.get("/{mmsi}")
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
    path = os.path.join(SQL_PATH, "ship_by_mmsi.sql")
    query = get_file_contents(path)
    df = pd.read_sql(text(query), dw.bind.connect(), params={"mmsi": mmsi})
    return df.to_dict(orient="records")

