"""Router for all trajectory endpoints."""
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, Path
from fastapi.responses import JSONResponse
from app.dependencies import get_dw
from sqlalchemy.orm import Session
from app.schemas.mobile_type import MobileType
from app.querybuilder import QueryBuilder
from helper_functions import response_json, get_values_from_enum_list
from typing import Any
import os
from app.schemas.time_series_representation import TimeSeriesRepresentation


router = APIRouter()

SQL_PATH = os.path.join(os.path.dirname(__file__), "sql")


@router.get("/trajectories/{date_id}/{sub_id}")
async def get_trajectories_by_date_id_and_sub_id(
        date_id: int = Path(description="The date id of the trajectory.", example=20070110),
        sub_id: str = Path(description="The sub id of the trajectory.", example=49396455),
        dw=Depends(get_dw)):
    """Get a single trajectory from a start date id and trajectory sub id."""
    params = {"date_id": date_id, "sub_id": sub_id}
    qb = QueryBuilder(SQL_PATH)
    qb.add_sql("select_date_id_and_sub_id.sql")
    final_query = qb.get_query_str()

    # Returned as a JSON Array by FastAPI.
    # FastAPI provides conversion of data types, such as Timestamp to string, or Interval to integer.
    return JSONResponse(response_json(final_query, dw, params))


@router.get("/trajectories/")
async def get_trajectories(
        offset: int = Query(default=0, description="Skip the first X ships returned by the request"),
        limit: int = Query(default=10, description="Limit the number of ships returned by the request to X"),
        x_min: float | None = Query(default=None,
                                    description='Defines the "left side" of the bounding rectangle,'
                                                ' coordinates must match the provided "srid"'),
        y_min: float | None = Query(default=None,
                                    description='Defines the "bottom side" of the bounding rectangle,'
                                                ' coordinates must match the provided "srid"'),
        x_max: float | None = Query(default=None,
                                    description='Defines the "right side" of the bounding rectangle,'
                                                ' coordinates must match the provided "srid"'),
        y_max: float | None = Query(default=None,
                                    description='Defines the "top side" of the bounding rectangle,'
                                                ' coordinates must match the provided "srid"'),
        destination: list[str] | None = Query(default=None,
                                              description="The destination of the ship generating the trajectory."),
        mmsi: list[int] | None = Query(default=None,
                                       description="The MMSI for the ship generating the trajectory."),
        imo: list[int] | None = Query(default=None,
                                      description="The IMO for the ship generating the trajectory."),
        name: list[str] | None = Query(default=None,
                                       description="The name for the ship generating the trajectory."),
        country: list[str] | None = Query(default=None,
                                          description="The country for the ship generating the trajectory."),
        callsign: list[str] | None = Query(default=None,
                                           description="The callsign for the ship generating the trajectory."),
        mobile_type: list[MobileType] | None = Query(default=None,
                                                     description="The mobile type for the ship"
                                                                 " sailing on the trajectory."),
        srid: int = Query(default=4326,
                          description="The spatial reference system for the trajectory."),
        from_date: datetime | None = Query(default=None,
                                           example="2021-01-01T00:00:00Z",
                                           description="The start date for the trajectory."),
        to_date: datetime | None = Query(default=None,
                                         example="2021-01-01T00:00:00Z",
                                         description="The end date for the trajectory."),
        stopped: bool | None = Query(default=None,
                                     description="If the trajectory must represents a stopped ship."
                                                 "\nIf not provided, both stopped and non-stopped ships are returned."),
        time_series_representation_type: TimeSeriesRepresentation =
        Query(default=TimeSeriesRepresentation.MFJSON,
              description="The time series representation of the trajectory data in the response."),
        dw: Session = Depends(get_dw)
):
    """Get trajectories based on the provided parameters."""
    params = {"offset": offset, "limit": limit}
    trajectory_params = {"infer_stopped": stopped}
    ship_params = {"mmsi": mmsi, "imo": imo, "name": name, "country": country, "callsign": callsign}
    ship_type_params = {"mobile_type": get_values_from_enum_list(mobile_type, MobileType) if mobile_type else None}
    nav_status_params = {"destination": destination}
    temporal_params = {"from_datetime": from_date, "to_datetime": to_date}
    # SRID is not required to be complete, and is therefore not part of this dict.
    spatial_params = {"xmin": x_min, "ymin": y_min, "xmax": x_max, "ymax": y_max}

    qb = QueryBuilder(SQL_PATH)

    # Adding SELECT, FROM and JOIN clauses to the query, depending on the requested content type.
    if time_series_representation_type.MFJSON:
        qb.add_sql("select_MFJSON.sql")
    elif time_series_representation_type.GEOJSON:
        qb.add_sql("select_GeoJSON.sql")

    # If parameters for ships is provided, a JOIN clause between the fact_trajectory and dim_ship is added to the query.
    _add_joins_ship_relations(qb, ship_params, ship_type_params)

    # If certain parameters are provided, then they are added to the query as a WHERE/AND clause, filtering results.
    _filter_operator(qb, params, {"ds": ship_params, "dst": ship_type_params, "dns": nav_status_params}, "IN")
    _filter_operator(qb, params, {"ft": trajectory_params}, "=")

    # Check if any temporal or spatial parameters are provided and update the parameters accordingly.
    temporal_bounds = _update_params_temporal(params, temporal_params)
    spatial_bounds = _update_params(params, spatial_params)

    # If spatial bounds are provided, but not complete, raise an error.
    if spatial_bounds and None in spatial_params.values():
        raise HTTPException(status_code=400, detail="Spatial bounds not complete")

    _update_params(params, {"srid": srid}) if spatial_bounds else None

    # If temporal or spatial bounds are provided, WHERE clauses are added to the query.
    _filter_temporal_spatial(qb, spatial_bounds, temporal_bounds)

    # Clause for order by, offset and limit is added to the query
    qb.add_string("ORDER BY ft.trajectory_sub_id OFFSET :offset LIMIT :limit;")

    final_query = qb.get_query_str()

    return JSONResponse(response_json(final_query, dw, params))


def _add_joins_ship_relations(qb: QueryBuilder, ship_params: dict[str, list[str | int]],
                              ship_type_params: dict[str, list[str]]) -> None:
    """
    Add JOIN clauses for attributes related to ships and ship types to the query builder, if applicable.

    Args:
        qb: The query builder to add the JOIN clauses to.
        ship_params: The parameters for the ship.
        ship_type_params: The parameters for the ship type.
    """
    ship_sql_str = "JOIN dim_ship ds on ft.ship_id = ds.ship_id"
    ship_type_sql_str = "JOIN dim_ship_type dst on ds.ship_type_id = dst.ship_type_id"
    ship_join_added = False
    if any(value is not None for value in ship_params.values()):
        qb.add_string(ship_sql_str)
        ship_join_added = True
    if ship_type_params["mobile_type"] is not None:
        if ship_join_added:
            qb.add_string(ship_type_sql_str)
        else:
            qb.add_string(ship_sql_str).add_string(ship_type_sql_str)


def _update_params_temporal(params: dict[str, Any], temporal_dict: dict[str, datetime]) -> bool:
    """
    Update the params dict with the values from temporal_dict.

    If only one of the values is provided, the other is set to the min or max value.

    Args:
        params: The params dict to add the values to.
        temporal_dict: The dict containing the temporal values to add.
    """
    if temporal_dict["from_datetime"] is None and temporal_dict["to_datetime"] is None:
        return False
    temporal_dict["from_datetime"] = temporal_dict["from_datetime"] if temporal_dict["from_datetime"] else datetime.min
    temporal_dict["to_datetime"] = temporal_dict["to_datetime"] if temporal_dict["to_datetime"] else datetime.max
    _update_params(params,
                   {"from_date": temporal_dict["from_datetime"].strftime("%Y%m%d"),
                    "from_time": temporal_dict["from_datetime"].strftime("%H%M%S"),
                    "to_date": temporal_dict["to_datetime"].strftime("%Y%m%d"),
                    "to_time": temporal_dict["to_datetime"].strftime("%H%M%S")})
    return True


def _update_params(params: dict[str, Any], param_dict: dict[str, Any]) -> bool:
    """
    Update the params dict with the values from param_dict if the value is not None.

    Args:
        params: The params dict to add the values to.
        param_dict: The dict containing the potential values to add.

    Returns:
        bool: True if any value was added to the params dict, False otherwise.
    """
    update = False
    for key, value in param_dict.items():
        if value is not None:
            params[key] = value
            update = True
    return update


def _filter_operator(qb: QueryBuilder, params: dict[str, Any], filter_dict: dict[str, Any], operator: str) -> None:
    """
    Add WHERE clauses to the query builder, depending on the provided parameters.

     Args:
         qb: The QueryBuilder object to add the WHERE clauses to.
         params: The params dict to add the values to.
         filter_dict: The dict containing the values to filter on.
         operator: The operator to use in the WHERE clause.
    """
    for relation, param_dict in filter_dict.items():
        for key, value in param_dict.items():
            if value is not None:
                qb.add_where(relation + "." + key, operator, value, params)


def _filter_temporal_spatial(qb: QueryBuilder, spatial_bounds: bool, temporal_bounds: bool) -> None:
    """
    Add temporal and spatial filters to the query if bounds are provided.

    Args:
        qb: The QueryBuilder object to add the WHERE/AND clause to.
        spatial_bounds: True if spatial bounds are provided, False otherwise.
        temporal_bounds: True if temporal bounds are provided, False otherwise.
    """
    bound_placeholder = ""
    if temporal_bounds or spatial_bounds:
        qb.add_where_from_string("STBOX({BOUNDS}) && dt.trajectory")
        # Adding spatial filters to the query if provided
        if spatial_bounds:
            bound_placeholder = "ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, :srid)"
        # Adding temporal filters to the query if provided
        if temporal_bounds:
            if bound_placeholder != "":
                bound_placeholder += ", "
            bound_placeholder += "span(timestamp_from_date_time_id(:from_date, :from_time), " \
                                 "timestamp_from_date_time_id(:to_date, :to_time), True, True)"
    qb.format_query({"BOUNDS": bound_placeholder}) if bound_placeholder != "" else None