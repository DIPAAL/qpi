"""
Ship router.

Contains endpoints to retrieve information about a specific ship or a set of ships.
"""
from fastapi import APIRouter, Depends, Path, HTTPException, Query
from sqlalchemy.orm import Session
from app.dependencies import get_dw
from app.querybuilder import QueryBuilder
from helper_functions import response
from app.schemas.search_method_spatial import SearchMethodSpatial
from app.schemas.mobile_type import MobileType
from app.schemas.ship_type import ShipType
import datetime
import os

router = APIRouter()

SQL_PATH = os.path.join(os.path.dirname(__file__), "sql")


@router.get("/")
async def ships(  # noqa: C901
        # Pagination
        skip: int = Query(default=0, description="Skip the first X ships returned by the request"),
        limit: int = Query(default=100, description="Limit the number of ships returned by the request to X"),
        # Filter for a specific ship
        ship_id: int | None = Query(default=None,
                                    description="Filter for a specific ship by its ID in the fact_ship relation"),
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
        mobile_type_in: list[MobileType] | None = Query(default=None,
                                                        description="Filter for ships with specified mobile types"),
        mobile_type_nin: list[MobileType] | None = Query(default=None,
                                                         description="Filter for ships without specified mobile types"),
        ship_type_in: list[ShipType] | None = Query(default=None,
                                                    description="Filter for ships with specified ship types"),
        ship_type_nin: list[ShipType] | None = Query(default=None,
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
    """Return a dictionary containing information ships, filtered by the given parameters."""
    # Query builder instantiated and ship select statement added to query
    qb = QueryBuilder(SQL_PATH)

    # Parameters to be added to final query.
    params = {
        "offset": skip,
        "limit": limit
    }
    # Placeholders to be replaced in the final query.
    placeholders = {}

    # First, the select statement is added to the query, which is the same for all queries.
    # This part of the query also determines what the output for the client will be.
    qb.add_sql("select_ship.sql", new_line=False)

    # If ship_id is provided, only one ship can be found, done by a simple query.
    if ship_id:
        qb.add_sql("ship_by_id.sql")
        return response(qb.get_query_str(), dw, {"id": ship_id})

    # Setup of spatial bounds if provided
    spatial_params = {"xmin": min_x, "ymin": min_y, "xmax": max_x, "ymax": max_y}
    spatial_bounds = True if any(value is not None for value in spatial_params.values()) else False

    if spatial_bounds and None in spatial_params.values():
        raise HTTPException(status_code=400, detail="Spatial bounds not complete")
    params.update(spatial_params)

    # Setup of temporal bounds if provided
    temporal_params = {}

    if from_datetime:
        temporal_params.update({
            "from_date": int(from_datetime.strftime("%Y%m%d")),
            "from_time": int(from_datetime.strftime("%H%M%S"))
        })
    if to_datetime:
        temporal_params.update({
            "to_date": int(to_datetime.strftime("%Y%m%d")),
            "to_time": int(to_datetime.strftime("%H%M%S")),
        })

    params.update(temporal_params)
    temporal_bounds = True if any(temporal_params) else False

    # From and where statements added to query, depending on search method and temporal/spatial bounds
    # If no temporal or spatial bounds are provided, we join no tables with spatial or temporal information.
    if not temporal_bounds and not spatial_bounds:
        qb.add_sql("from_ship.sql")

    elif search_method == SearchMethodSpatial.trajectories:
        qb.add_sql("from_trajectory.sql")
        if spatial_bounds:
            qb.add_string("JOIN dim_trajectory dt ON ft.trajectory_sub_id = dt.trajectory_sub_id")
            qb.add_where_from_string("st_intersects(ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, 4326), "
                                     "dt.trajectory::geometry)")
        if temporal_bounds:
            temporal_attribute = "ft.start_date_id"
            add_temporal_filter(qb, temporal_attribute, temporal_params)

    elif "cell" in search_method.value:
        qb.add_sql("from_cell.sql")
        placeholders.update({"CELL_SIZE": search_method.value})
        if temporal_bounds and spatial_bounds:
            qb.add_where_from_file("stbox_spatialtemporal.sql")
            placeholders.update({"RELATION_STBOX": "fc"})
        elif temporal_bounds:
            temporal_attribute = "fc.entry_date_id"
            add_temporal_filter(qb, temporal_attribute, temporal_params)
        elif spatial_bounds:
            qb.add_where_from_string("ST_CONTAINS(ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, 3034), dc.geom)")
    else:
        raise HTTPException(status_code=400, detail="Search method not supported")

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
        "mobile_type_in": get_values_from_enum_list(mobile_type_in, MobileType),
        "mobile_type_nin": get_values_from_enum_list(mobile_type_nin, MobileType),
        "ship_type_in": get_values_from_enum_list(ship_type_in, ShipType),
        "ship_type_nin": get_values_from_enum_list(ship_type_nin, ShipType)
    }

    # If there are ship filters, add the appropriate where statement(s) to query
    for key, value in filter_params_ship.items():
        if value:
            param_name = key.rsplit("_", 1)[0]
            qb.add_where("ds." + param_name, qb.get_sql_operator(key), value, params)

    # If there are ship type filters, add the appropriate where statement(s) to query
    for key, value in filter_params_ship_type.items():
        if value:
            param_name = key.rsplit("_", 1)[0]
            qb.add_where("dst." + param_name, qb.get_sql_operator(key), value, params)

    # Statements for order by, offset and limit is added to the query
    qb.add_string("ORDER BY ds.ship_id LIMIT :limit OFFSET :offset;")

    # Finally, format all placeholders in the query, then collect the query string and return the response
    qb.format_query(placeholders)
    final_query = qb.get_query_str()
    return response(final_query, dw, params)


def add_temporal_filter(qb: QueryBuilder, temporal_attribute: str, temporal_params: dict):
    """Add a temporal filter to the query builder."""
    if temporal_params["from_date"] and temporal_params["from_time"]:
        qb.add_where(temporal_attribute, ">=", temporal_params["from_date"])\
            .add_where(temporal_attribute, ">=", temporal_params["from_time"])
    if temporal_params["to_date"] and temporal_params["to_time"]:
        qb.add_where(temporal_attribute, "<=", temporal_params["to_date"])\
            .add_where(temporal_attribute, "<=", temporal_params["to_time"])
    return qb


def get_values_from_enum_list(enum_list, enum_type):
    """Return a list of values from an enum list."""
    if enum_list:
        return [enum_type(value).value for value in enum_list]


@router.get("/{mmsi}")
async def mmsi(
        mmsi: int = Path(..., le=999_999_999, description="The mmsi number of a ship"),
        dw: Session = Depends(get_dw)
):
    """
    Get information about a ship by MMSI.

    Although MMSI is supposed to be a unique identifier, there are some cases where ships share the same MMSI.
    In such cases a set of ships is returned.
    """
    qb = QueryBuilder()
    qb.add_sql("ship_by_mmsi.sql")
    return response(qb.get_query_str(), dw, {"mmsi": mmsi})
