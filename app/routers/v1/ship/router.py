"""
Ship router.

Contains endpoints to retrieve information about a specific ship or a set of ships.
"""
from fastapi import APIRouter, Depends, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.dependencies import get_dw
from app.querybuilder import QueryBuilder
from helper_functions import response, update_params_datetime, update_params_datetime_min_max_if_none, \
    add_filters_to_query_and_param
from app.schemas.search_method_spatial import SearchMethodSpatial
from app.schemas.mobile_type import MobileType
from app.schemas.ship_type import ShipType
from typing import Any, List, Type
from enum import Enum
import datetime
import os

router = APIRouter()

SQL_PATH = os.path.join(os.path.dirname(__file__), "sql")


@router.get("/")
async def ships(
        # Pagination
        offset: int = Query(default=0, description="Skip the first X ships returned by the request"),
        limit: int = Query(default=10, description="Limit the number of ships returned by the request to X"),
        # Filters for ships
        mmsi_in: list[int] | None = Query(default=None,
                                          description="Filter for ships with specified MMSIs"),
        mmsi_nin: list[int] | None = Query(default=None,
                                           description="Filter for ships without specified MMSIs"),
        mmsi_gt: int | None = Query(default=None,
                                    description="Filter for ships with a MMSI greater than the given value"),
        mmsi_gte: int | None = Query(default=None,
                                     description="Filter for ships with a MMSI greater than or equal to the given"
                                                 " value"),
        mmsi_lte: int | None = Query(default=None,
                                     description="Filter for ships with a MMSI less than or equal to the given value"),
        mmsi_lt: int | None = Query(default=None,
                                    description="Filter for ships with a MMSI less than the given value"),
        mid_in: list[int] | None = Query(default=None,
                                         description="Filter for ships with specified MIDs"),
        mid_nin: list[int] | None = Query(default=None,
                                          description="Filter for ships without specified MIDs"),
        mid_gt: int | None = Query(default=None,
                                   description="Filter for ships with a MID greater than the given value"),
        mid_gte: int | None = Query(default=None,
                                    description="Filter for ships with a MID greater than or equal to the given value"),
        mid_lte: int | None = Query(default=None,
                                    description="Filter for ships with a MID less than or equal to the given value"),
        mid_lt: int | None = Query(default=None,
                                   description="Filter for ships with a MID less than the given value"),
        imo_in: list[int] | None = Query(default=None,
                                         description="Filter for ships with specified IMOs"),
        imo_nin: list[int] | None = Query(default=None,
                                          description="Filter for ships without specified IMOs"),
        imo_gt: int | None = Query(default=None,
                                   description="Filter for ships with a IMO greater than the given value"),
        imo_gte: int | None = Query(default=None,
                                    description="Filter for ships with a IMO greater than or equal to the given value"),
        imo_lte: int | None = Query(default=None,
                                    description="Filter for ships with a IMO less than or equal to the given value"),
        imo_lt: int | None = Query(default=None,
                                   description="Filter for ships with a IMO less than the given value"),
        a_in: list[int] | None = Query(default=None,
                                       description="Filter for ships with specified A values"),
        a_nin: list[int] | None = Query(default=None,
                                        description="Filter for ships without specified A values"),
        a_gt: int | None = Query(default=None,
                                 description="Filter for ships with a A greater than the given value"),
        a_gte: int | None = Query(default=None,
                                  description="Filter for ships with a A greater than or equal to the given value"),
        a_lte: int | None = Query(default=None,
                                  description="Filter for ships with a A less than or equal to the given value"),
        a_lt: int | None = Query(default=None,
                                 description="Filter for ships with a A less than the given value"),
        b_in: list[int] | None = Query(default=None,
                                       description="Filter for ships with specified B values"),
        b_nin: list[int] | None = Query(default=None,
                                        description="Filter for ships without specified B values"),
        b_gt: int | None = Query(default=None,
                                 description="Filter for ships with a B greater than the given value"),
        b_gte: int | None = Query(default=None,
                                  description="Filter for ships with a B greater than or equal to the given value"),
        b_lte: int | None = Query(default=None,
                                  description="Filter for ships with a B less than or equal to the given value"),
        b_lt: int | None = Query(default=None,
                                 description="Filter for ships with a B less than the given value"),
        c_in: list[int] | None = Query(default=None,
                                       description="Filter for ships with specified C values"),
        c_nin: list[int] | None = Query(default=None,
                                        description="Filter for ships without specified C values"),
        c_gt: int | None = Query(default=None,
                                 description="Filter for ships with a C greater than the given value"),
        c_gte: int | None = Query(default=None,
                                  description="Filter for ships with a C greater than or equal to the given value"),
        c_lte: int | None = Query(default=None,
                                  description="Filter for ships with a C less than or equal to the given value"),
        c_lt: int | None = Query(default=None,
                                 description="Filter for ships with a C less than the given value"),
        d_in: list[int] | None = Query(default=None,
                                       description="Filter for ships with specified D values"),
        d_nin: list[int] | None = Query(default=None,
                                        description="Filter for ships without specified D values"),
        d_gt: int | None = Query(default=None,
                                 description="Filter for ships with a D greater than the given value"),
        d_gte: int | None = Query(default=None,
                                  description="Filter for ships with a D greater than or equal to the given value"),
        d_lte: int | None = Query(default=None,
                                  description="Filter for ships with a D less than or equal to the given value"),
        d_lt: int | None = Query(default=None,
                                 description="Filter for ships with a D less than the given value"),
        name_in: list[str] | None = Query(default=None,
                                          description="Filter for ships with specified names"),
        name_nin: list[str] | None = Query(default=None,
                                           description="Filter for ships without specified names"),
        callsign_in: list[str] | None = Query(default=None,
                                              description="Filter for ships with specified callsigns"),
        callsign_nin: list[str] | None = Query(default=None,
                                               description="Filter for ships without specified callsigns"),
        location_system_type_in: list[str] | None = Query(default=None,
                                                          description="Filter for ships with specified location "
                                                                      "systems"),
        location_system_type_nin: list[str] | None = Query(default=None,
                                                           description="Filter for ships without specified location "
                                                                       "systems"),
        flag_region_in: list[str] | None = Query(default=None,
                                                 description="Filter for ships with specified flag regions"),
        flag_region_nin: list[str] | None = Query(default=None,
                                                  description="Filter for ships without specified flag regions"),
        flag_state_in: list[str] | None = Query(default=None,
                                                description="Filter for ships with specified flag states"),
        flag_state_nin: list[str] | None = Query(default=None,
                                                 description="Filter for ships without specified flag states"),

        # Filters for ship type
        mobile_type_in: List[MobileType] | None = Query(default=None,
                                                        description="Filter for ships with specified mobile types"),
        mobile_type_nin: List[MobileType] | None = Query(default=None,
                                                         description="Filter for ships without specified mobile types"),
        ship_type_in: List[ShipType] | None = Query(default=None,
                                                    description="Filter for ships with specified ship types"),
        ship_type_nin: List[ShipType] | None = Query(default=None,
                                                     description="Filter for ships without specified ship types"),
        # Search method
        search_method: SearchMethodSpatial = Query(default="cell_1000m",
                                                   description="Determines the search method used to find ships when "
                                                               "using spatial or temporal filters"),
        # Temporal bounds
        from_datetime: datetime.datetime = Query(default=None,
                                                 example="2021-01-01T00:00:00Z",
                                                 description="Filter for ships with a first position after or at the "
                                                             "given datetime"),
        to_datetime: datetime.datetime = Query(default=None,
                                               description="Filter for ships with a last position before or at the "
                                                           "given datetime"),
        # Spatial bounds
        min_x: int = Query(default=None,
                           description="Filter for ships with a first position with a longitude greater than or equal "
                                       "to the given value"),
        min_y: int = Query(default=None,
                           description="Filter for ships with a first position with a latitude greater than or equal "
                                       "to the given value"),
        max_x: int = Query(default=None,
                           description="Filter for ships with a first position with a longitude less than or equal "
                                       "to the given value"),
        max_y: int = Query(default=None,
                           description="Filter for ships with a first position with a latitude less than or equal "
                                       "to the given value"),
        # The data warehouse Session
        dw: Session = Depends(get_dw)
):
    """
    Return a JSON Array containing all ships that match the given filters.

    Note that when using spatial bounds, the SRID for trajectories is 4326 and for cells 3034.
    """
    # Query builder instantiated
    qb = QueryBuilder(SQL_PATH)

    # Parameters to be added to final query.
    params = {
        "offset": offset,
        "limit": limit
    }

    # Placeholders to be added to final query.
    placeholders = {}

    # First, the SELECT clause is added to the query, which is the same for all queries.
    # This statement also determines what the output for the client will be.
    qb.add_sql("select_ship.sql")

    # Setup of spatial bounds if provided
    spatial_params: dict = {"xmin": min_x, "ymin": min_y, "xmax": max_x, "ymax": max_y}
    spatial_bounds = True if any(value is not None for value in spatial_params.values()) else False

    # If spatial bounds are provided, but not complete, raise an error
    if spatial_bounds and None in spatial_params.values():
        raise HTTPException(status_code=400, detail="Spatial bounds not complete")

    params.update(spatial_params)

    # Setup of temporal bounds if provided
    temporal_params: dict = {"from_date": None, "from_time": None, "to_date": None, "to_time": None}

    update_params_datetime(temporal_params, from_datetime, "from")
    update_params_datetime(temporal_params, to_datetime, "to")

    temporal_bounds = True if any(value is not None for value in temporal_params.values()) else False

    # If temporal bounds are provided, but not complete, set the leftover bound to its min or max values
    update_params_datetime_min_max_if_none(temporal_params, temporal_bounds, from_datetime, to_datetime)

    params.update(temporal_params)

    # Add FROM and WHERE clauses to query, depending on the spatial/temporal bounds provided
    if not temporal_bounds and not spatial_bounds:
        qb.add_sql("from_ship.sql")

    elif search_method == SearchMethodSpatial.trajectories:
        add_trajectory_from_where_clause_to_query(qb, spatial_bounds, temporal_bounds)

    elif "cell" in search_method.value:
        add_cell_from_where_clause_to_query(qb, placeholders, search_method, spatial_bounds, temporal_bounds)

    else:
        raise HTTPException(status_code=400, detail="Search method not supported")

    # All filter parameters for the ship dimension.
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

    # All filter parameters for the ship type dimension.
    filter_params_ship_type = {
        "mobile_type_in": get_values_from_enum_list(mobile_type_in, MobileType),
        "mobile_type_nin": get_values_from_enum_list(mobile_type_nin, MobileType),
        "ship_type_in": get_values_from_enum_list(ship_type_in, ShipType),
        "ship_type_nin": get_values_from_enum_list(ship_type_nin, ShipType)
    }

    # Add filters to the query builder query and params dict
    add_filters_to_query_and_param(qb, "ds.", filter_params_ship, params)
    add_filters_to_query_and_param(qb, "dst.", filter_params_ship_type, params)

    # Clause for order by, offset and limit is added to the query
    qb.add_string("ORDER BY ds.ship_id LIMIT :limit OFFSET :offset;")

    # Finally, format all placeholders in the query, then collect the query string and return the response
    qb.format_query(placeholders)
    final_query = qb.get_query_str()
    return JSONResponse(response(final_query, dw, params))


def add_trajectory_from_where_clause_to_query(qb: QueryBuilder, spatial_bounds: bool, temporal_bounds: bool) -> None:
    """
    Add the FROM and WHERE clauses for the trajectory search method to the query builder.

    Args:
        qb (QueryBuilder): The query builder to add the clauses to.
        spatial_bounds (bool): If true, the spatial bounds are added to the WHERE clause.
        temporal_bounds (bool): If true, the temporal bounds are added to the WHERE clause.
    """
    qb.add_sql("from_trajectory.sql")
    if temporal_bounds and spatial_bounds:
        qb.add_where_from_string("STBOX(ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, 4326), "
                                 "span(timestamp_from_date_time_id(:from_date, :from_time), "
                                 "timestamp_from_date_time_id(:to_date, :to_time), True, True)) && dt.trajectory")
    elif spatial_bounds:
        qb.add_where_from_string("WHERE STBOX(ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, 4326)) && dt.trajectory")

    elif temporal_bounds:
        qb.add_where_from_string("STBOX(span(timestamp_from_date_time_id(:from_date, :from_time), "
                                 "timestamp_from_date_time_id(:to_date, :to_time), True, True)) && dt.trajectory")


def add_cell_from_where_clause_to_query(qb: QueryBuilder, placeholders: dict, search_method: SearchMethodSpatial,
                                        spatial_bounds: bool, temporal_bounds: bool) -> None:
    """
    Add the FROM and WHERE clauses for the cell search method to the query builder and update the placeholders.

    Args:
        qb (QueryBuilder): The query builder to add the clauses to.
        placeholders (dict): The placeholders to update.
        search_method (SearchMethodSpatial): The search method to use. Determines the cell size.
        spatial_bounds (bool): If true, the spatial bounds are added to the WHERE clause.
        temporal_bounds (bool): If true, the temporal bounds are added to the WHERE clause.
    """
    qb.add_sql("from_cell.sql")
    placeholders.update({"CELL_SIZE": search_method.value})
    if temporal_bounds and spatial_bounds:
        qb.add_where_from_string("STBOX(ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, 3034), "
                                 "span(timestamp_from_date_time_id(:from_date, :from_time), "
                                 "timestamp_from_date_time_id(:to_date, :to_time), True, True)) && fc.st_bounding_box")
    elif temporal_bounds:
        qb.add_where_from_string("STBOX(span(timestamp_from_date_time_id(:from_date, :from_time), "
                                 "timestamp_from_date_time_id(:to_date, :to_time), True, True)) && fc.st_bounding_box")
    elif spatial_bounds:
        qb.add_where_from_string("STBOX(ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, 3034)) && fc.st_bounding_box")


def get_values_from_enum_list(enum_list: List[Type[Enum]] | None, enum_type: Type[Enum]) -> list[Any]:
    """
    Get the values from an enum list.

    Args:
        enum_list: A list of enums.
        enum_type: The type of the enums in the list.

    Returns: A list of values from an enum list.
    """
    if enum_list:
        return [enum_type(value).value for value in enum_list]


@router.get("/{ship_id}")
async def ship_by_id(
        ship_id: int = Path(description="The ship ID for a ship in the data warehouse"),
        dw: Session = Depends(get_dw)
):
    """Get information about a ship by its ID."""
    qb = QueryBuilder(SQL_PATH)
    qb.add_sql("ship_by_id.sql")
    final_query = qb.get_query_str()
    return JSONResponse(response(final_query, dw, {"id": ship_id}))
