"""
Ship router.

Contains endpoints to retrieve information about a specific ship or a set of ships.
"""
from fastapi import APIRouter, Depends, Path, HTTPException, Query
from sqlalchemy.orm import Session
from app.dependencies import get_dw
from app.querybuilder import get_sql_operator, QueryBuilder
from app.routers.v1.ship import schemas
import datetime
import pandas as pd
from sqlalchemy import text
import os

router = APIRouter()

SQL_PATH = os.path.join(os.path.dirname(__file__), "sql")


def response(query: str, dw: Session, params: dict):
    """
    Return a response from a query.

    Args:
        query (str): The query to execute.
        dw (Session): The data warehouse session.
        params (dict): The parameters to pass to the query.
    """
    df = pd.read_sql(text(query), dw.bind.connect(), params=params)
    return df.to_dict(orient="records")


@router.get("/")
async def ships(  # noqa: C901
        # Pagination
        skip: int = 0,
        limit: int = 10,
        # Filter for a specific ship
        ship_id: int | None = None,
        # Filters for ships
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
        c_lte: int | None = Query(default=None),
        c_lt: int | None = Query(default=None),
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

        # Filters for ship type
        mobile_type_in: list[str] | None = Query(default=None),
        mobile_type_nin: list[str] | None = Query(default=None),
        ship_type_in: list[str] | None = Query(default=None),
        ship_type_nin: list[str] | None = Query(default=None),
        # Temporal bounds
        from_datetime: datetime.datetime = Query(default=None),
        to_datetime: datetime.datetime = Query(default=None),
        # Spatial bounds
        search_method: schemas.SearchMethodSpatial = Query(default="cell_1000m"),
        min_x: int = Query(default=None),
        min_y: int = Query(default=None),
        max_x: int = Query(default=None),
        max_y: int = Query(default=None),
        # Data warehouse Session
        dw: Session = Depends(get_dw)
):
    """
    Return a dictionary with information about a specific ship or a set of ships.

    Args:

        skip (int, optional): Number of records to skip. Defaults to 0.
        limit (int, optional): Number of records to return. Defaults to 10.

        ship_id (int, optional): ID of the ship to return. Defaults to None.

        The following parameters can be filtered with the following operators: in, nin, gt, gte, lte, lt.
        mmsi_(filter) (list[int], int, optional): MMSI of the ship.
        mid_(filter) (list[int], int, optional): MID of the ship.
        imo_(filter) (list[int], int, optional): IMO of the ship.
        a_(filter) (list[int], int, optional): Distance from the transponder to the bow of the ship.
        b_(filter) (list[int], int, optional): Distance from the transponder to the stern of the ship.
        c_(filter) (list[int], int, optional): Distance from the transponder to the port side of the ship.
        d_(filter) (list[int], int, optional): Distance from the transponder to the starboard side of the ship.

        The following parameters can be filtered with the following operators: in, nin.
        name_(filter) (list[str], optional): Name of the ship.
        callsign_(filter) (list[str], optional): Callsign of the ship.
        location_system_type_(filter) (list[str], optional): Location system type of the ship.
        flag_region_(filter) (list[str], optional): Flag region of the ship.
        flag_state_(filter) (list[str], optional): Flag state of the ship.
        mobile_type_(filter) (list[str], optional): Mobile type of the ship.
        ship_type_(filter) (list[str], optional): Ship type of the ship.

        from_datetime (datetime.datetime, optional): Start date of the temporal filter. Defaults to None.
        to_datetime (datetime.datetime, optional): End date of the temporal filter. Defaults to None.
        Example: from_datetime=2021-01-01T00:00:00Z&to_datetime=2022-01-01T00:00:00Z

        search_method (enumerate): Spatial search method. Defaults to "cell_1000m".
        min_x (int, optional): Minimum x coordinate of the spatial filter. Defaults to None.
        min_y (int, optional): Minimum y coordinate of the spatial filter. Defaults to None.
        max_x (int, optional): Maximum x coordinate of the spatial filter. Defaults to None.
        max_y (int, optional): Maximum y coordinate of the spatial filter. Defaults to None.


    Returns:

        dict: Dictionary with information about a specific ship or a set of ships.
    """  # noqa: D412
    # Query builder instantiated and ship select statement added to query
    QB = QueryBuilder(SQL_PATH)

    # Parameters to be added to final query.
    params = {
        "offset": skip,
        "limit": limit
    }

    # If ship_id is provided, only one ship can be found, done by a simple query.
    if ship_id:
        QB.add_sql("select_ship.sql", new_line=False)
        QB.add_sql("ship_by_id.sql")
        return response(QB.get_query_str(), dw, {"id": ship_id})

    # If ship_id is not provided, a more complex query is needed.
    # First, the select statement is added to the query, which is the same for all queries.
    QB.add_sql("select_ship.sql", new_line=False)

    # Filters for temporal/spatial bounds are assumed to be false until proven otherwise.
    temporal_bounds = False
    spatial_bounds = False

    spatial_params = {"xmin": min_x, "ymin": min_y, "xmax": max_x, "ymax": max_y}

    if None not in spatial_params.values():
        spatial_bounds = True
        if None in spatial_params.values():
            raise HTTPException(status_code=400, detail="Spatial bounds not complete")
        params.update(spatial_params)

    temporal_params = {"from_date": from_datetime,
                       "from_time": from_datetime,
                       "to_date": to_datetime,
                       "to_time": to_datetime}

    if None not in temporal_params.values():
        # Format datetime objects to integers, depending on the type of temporal parameter.
        for key, value in temporal_params.items():
            if key[-4:] == "date":
                temporal_params[key] = int(value.strftime("%Y%m%d"))
            elif key[-4:] == "time":
                temporal_params[key] = int(value.strftime("%H%M%S"))
        temporal_bounds = True
        params.update(temporal_params)

    # From statement added to query, depending on search method (cell or trajectory and temporal/spatial bounds)
    # If no temporal or spatial bounds are provided, we join no tables with spatial or temporal information.
    if temporal_bounds is False and spatial_bounds is False:
        QB.add_sql("from_ship.sql")

    elif search_method.value == "trajectories":
        QB.add_sql("from_trajectory.sql")
        if temporal_bounds or spatial_bounds:
            QB.add_string("WHERE")
        if temporal_bounds and spatial_bounds:
            QB.add_sql("trajectory_temporal.sql")
            QB.add_string(" AND", new_line=False)
            QB.add_sql("trajectory_spatial.sql")
        elif temporal_bounds:
            QB.add_sql("trajectory_temporal.sql")
        elif spatial_bounds:
            QB.add_sql("trajectory_spatial.sql")

    elif "cell" in search_method.value:
        replace = {"{CELL_SIZE}": search_method.value}
        QB.add_sql_with_replace("from_cell.sql", replace)
        if temporal_bounds or spatial_bounds:
            QB.add_string("WHERE")
        if temporal_bounds and spatial_bounds:
            QB.add_sql("cell_temporal.sql")
            QB.add_string(" AND", new_line=False)
            QB.add_sql("cell_spatial.sql")
        elif temporal_bounds:
            QB.add_sql("cell_temporal.sql")
        elif spatial_bounds:
            QB.add_sql("cell_spatial.sql")

    # All parameters for the ship filters
    filter_params_ship = {
        "mmsi_in": mmsi_in,     "mmsi_nin": mmsi_nin,   "mmsi_gt": mmsi_gt,
        "mmsi_gte": mmsi_gte,   "mmsi_lte": mmsi_lte,   "mmsi_lt": mmsi_lt,
        "mid_in": mid_in,       "mid_nin": mid_nin,     "mid_gt": mid_gt,
        "mid_gte": mid_gte,     "mid_lte": mid_lte,     "mid_lt": mid_lt,
        "imo_in": imo_in,       "imo_nin": imo_nin,     "imo_gt": imo_gt,
        "imo_gte": imo_gte,     "imo_lte": imo_lte,     "imo_lt": imo_lt,
        "a_in": a_in,           "a_nin": a_nin,         "a_gt": a_gt,
        "a_gte": a_gte,         "a_lte": a_lte,         "a_lt": a_lt,
        "b_in": b_in,           "b_nin": b_nin,         "b_gt": b_gt,
        "b_gte": b_gte,         "b_lte": b_lte,         "b_lt": b_lt,
        "c_in": c_in,           "c_nin": c_nin,         "c_gt": c_gt,
        "c_gte": c_gte,         "c_lte": c_lte,         "c_lt": c_lt,
        "d_in": d_in,           "d_nin": d_nin,         "d_gt": d_gt,
        "d_gte": d_gte,         "d_lte": d_lte,         "d_lt": d_lt,
        "name_in": name_in,     "name_nin": name_nin,
        "callsign_in": callsign_in, "callsign_nin": callsign_nin,
        "location_system_type_in": location_system_type_in, "location_system_type_nin": location_system_type_nin,
        "flag_region_in": flag_region_in, "flag_region_nin": flag_region_nin,
        "flag_state_in": flag_state_in, "flag_state_nin": flag_state_nin

    }

    # All parameters for ship type filters
    filter_params_ship_type = {
        "mobile_type_in": mobile_type_in, "mobile_type_nin": mobile_type_nin,
        "ship_type_in": ship_type_in, "ship_type_nin": ship_type_nin
    }

    # If there are ship filters, add the appropriate where statement(s) to query
    for key, value in filter_params_ship.items():
        if value:
            param_name = key.rsplit("_", 1)[0]
            operator = get_sql_operator(key)
            QB.add_where("ds." + param_name, operator, value)

    # If there are ship type filters, add the appropriate where statement(s) to query
    for key, value in filter_params_ship_type.items():
        if value:
            param_name = key.split("_")[0]
            operator = get_sql_operator(key)
            QB.add_where("dst." + param_name, operator, value)

    # Group by statement added to query, also introducing the order by, offset and limit statements
    QB.add_sql("group_by_ship.sql")

    final_query = QB.get_query_str()
    print(final_query)
    return response(final_query, dw, params)


@router.get("/{mmsi}")
async def mmsi(
        mmsi: int = Path(..., le=999_999_999),
        dw: Session = Depends(get_dw)
):
    """Get information about a ship by MMSI.

    Args:
        mmsi: The MMSI of the ship
        dw: A session to the data warehouse

    Returns: A list containing information about the ship
    """
    QB = QueryBuilder()
    QB.add_sql("ship_by_mmsi.sql")
    return response(QB.get_query_str(), dw, {"mmsi": mmsi})
