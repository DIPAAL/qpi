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
from app.schemas.trajectory import GeoJSONTrajectoryResponse, MFJSONTrajectoryResponse

router = APIRouter()

SQL_PATH = os.path.join(os.path.dirname(__file__), "sql")


@router.get("/trajectories/{date_id}/{sub_id}", response_model=MFJSONTrajectoryResponse)
async def get_trajectories_by_date_id_and_sub_id(
        date_id: int = Path(description="The start date id of the trajectory, in format: YYYYMMDD.",
                            example=20070110),
        sub_id: str = Path(description="The sub id of the trajectory.",
                           example=49396455),
        dw=Depends(get_dw)):
    """
    Get a single trajectory from a start date id and trajectory sub id.

    The trajectory is returned as a MFJSON object.
    """
    params = {"date_id": date_id, "sub_id": sub_id}
    qb = QueryBuilder(SQL_PATH)
    qb.add_sql("select_date_id_and_sub_id.sql")
    final_query = qb.get_query_str()

    # Returned as a JSON Array by FastAPI.
    # FastAPI provides conversion of data types, such as Timestamp to string, or Interval to integer.
    return JSONResponse(response_json(final_query, dw, params))


@router.get("/trajectories/", response_model=list[GeoJSONTrajectoryResponse] | list[MFJSONTrajectoryResponse])
async def get_trajectories(
        offset: int = Query(default=0, description="Specifies the offset of the first result to return."),
        limit: int = Query(default=10, description="Limits the number of results returned."),
        x_min: float | None = Query(default=None,
                                    description='Defines the "left side" of the bounding rectangle,'
                                                ' coordinates must match the provided "srid".'),
        y_min: float | None = Query(default=None,
                                    description='Defines the "bottom side" of the bounding rectangle,'
                                                ' coordinates must match the provided "srid".'),
        x_max: float | None = Query(default=None,
                                    description='Defines the "right side" of the bounding rectangle,'
                                                ' coordinates must match the provided "srid".'),
        y_max: float | None = Query(default=None,
                                    description='Defines the "top side" of the bounding rectangle,'
                                                ' coordinates must match the provided "srid".'),
        destination: list[str] | None = Query(default=None,
                                              description="Limits the destinations the ships must be going to."),
        mmsi: list[int] | None = Query(default=None,
                                       description="Limits what MMSI the ships must sails under."),
        imo: list[int] | None = Query(default=None,
                                      description="Limits what IMO  the ships must sails under."),
        name: list[str] | None = Query(default=None,
                                       description="Limits what name the ships must sails under."),
        country: list[str] | None = Query(default=None,
                                          description="Limits what country the ships must hail from."),
        callsign: list[str] | None = Query(default=None,
                                           description="Limits what callsign the ships must sails under."),
        mobile_type: list[MobileType] | None = Query(default=None,
                                                     description="Limits what mobile type the ships must belong to."
                                                                 "\nIf not provided, all mobile types are included."),
        srid: int = Query(default=4326,
                          description="The spatial reference system for the trajectory."),
        start_timestamp: datetime | None = Query(default=None,
                                                 example="2022-01-01T00:00:00Z",
                                                 description="The inclusive timestamp that defines "
                                                             "the start of the temporal bound. "
                                                             "If not provided, the earliest date is used."),
        end_timestamp: datetime | None = Query(default=None,
                                               example="2022-01-01T00:00:00Z",
                                               description="The inclusive timestamp that defines "
                                                           "the end of the the temporal bound. "
                                                           "If not provided, the latest date is used."),
        stopped: bool | None = Query(default=None,
                                     description="If the result must represents stopped ships."
                                                 "\nIf not provided, both stopped and "
                                                 "non-stopped ships are represented."),
        crop: bool = Query(default=False,
                           description="Whether to crop spatio-temporal and temporal data in the result "
                                       "to the spatio-temporal bounds. "
                                       "If not provided, the result is not cropped."),
        time_series_representation_type: TimeSeriesRepresentation =
        Query(default=TimeSeriesRepresentation.MFJSON,
              description="The time series representation of the trajectory data in the result."),
        dw: Session = Depends(get_dw)
):
    """Get trajectories based on the provided parameters."""
    params = {"offset": offset, "limit": limit}
    trajectory_params = {"infer_stopped": stopped}
    ship_params = {"mmsi": mmsi, "imo": imo, "name": name, "country": country, "callsign": callsign}
    ship_type_params = {"mobile_type": get_values_from_enum_list(mobile_type, MobileType) if mobile_type else None}
    nav_status_params = {"destination": destination}
    temporal_params = {"start_timestamp": start_timestamp, "end_timestamp": end_timestamp}
    # SRID is not required to be complete, and is therefore not part of this dict.
    spatial_params = {"xmin": x_min, "ymin": y_min, "xmax": x_max, "ymax": y_max}

    qb = QueryBuilder(SQL_PATH)

    # Check if cropped trajectories is requested, and set the parameters accordingly.
    _validate_temporal_bounds(temporal_params)
    _set_cropped_param(temporal_params, params, crop)

    # Adding SELECT, FROM and JOIN clauses to the query, depending on the requested content type.
    _add_trajectory_query(crop, qb, time_series_representation_type)

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


def _add_trajectory_query(crop: bool, qb: QueryBuilder,
                          time_series_representation_type: TimeSeriesRepresentation) -> None:
    """
    Add SELECT, FROM and JOIN clauses to the query, depending on the requested content type.

    Args:
        crop: If the result must be cropped to the temporal bound.
        qb: The query builder to add the clauses to.
        time_series_representation_type: The time series representation of the trajectory data in the result.
    """
    try:
        if crop:
            qb.add_sql(f"select_{time_series_representation_type.value}_cropped.sql")
        else:
            qb.add_sql(f"select_{time_series_representation_type.value}.sql")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid time series representation type") from e


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
    if temporal_dict["start_timestamp"] is None and temporal_dict["end_timestamp"] is None:
        return False
    temporal_dict["start_timestamp"] = temporal_dict["start_timestamp"] \
        if temporal_dict["start_timestamp"] else datetime.min
    temporal_dict["end_timestamp"] = temporal_dict["end_timestamp"] \
        if temporal_dict["end_timestamp"] else datetime.max
    _update_params(params,
                   {"start_date": temporal_dict["start_timestamp"].strftime("%Y%m%d"),
                    "start_time": temporal_dict["start_timestamp"].strftime("%H%M%S"),
                    "end_date": temporal_dict["end_timestamp"].strftime("%Y%m%d"),
                    "end_time": temporal_dict["end_timestamp"].strftime("%H%M%S")})
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
            bound_placeholder = "ST_Transform(ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, :srid), 4326)"
        # Adding temporal filters to the query if provided
        if temporal_bounds:
            # Add partition elimination
            qb.add_where_from_string("dt.date_id BETWEEN :start_date AND :end_date")
            qb.add_where_from_string("ft.start_date_id BETWEEN :start_date AND :end_date")

            if bound_placeholder != "":
                bound_placeholder += ", "
            bound_placeholder += "span(timestamp_from_date_time_id(:start_date, :start_time), " \
                                 "timestamp_from_date_time_id(:end_date, :end_time), True, True)"
    qb.format_query({"BOUNDS": bound_placeholder}) if bound_placeholder != "" else None


def _set_cropped_param(temporal_params: dict[str, datetime], params: dict[str, Any], cropped: bool) -> None:
    """
    Set the cropped parameter in the params dict if the trajectory must be cropped.

    Args:
        temporal_params: The temporal parameters.
        params: The params dict to add the values to.
        cropped: True if the trajectory must be cropped, False otherwise.
    """
    if not cropped:
        return None
    else:
        from_datetime = temporal_params["from_datetime"]
        to_datetime = temporal_params["to_datetime"]

        # Creates a string representation of a time span in a MobilityDB compatible format
        tstzspan_string = "[" + from_datetime.strftime("%Y-%m-%d %H:%M:%S") + ", "\
                              + to_datetime.strftime("%Y-%m-%d %H:%M:%S") + "]"

        _update_params(params, {"crop_span": tstzspan_string})


def _validate_temporal_bounds(temporal_params: dict[str, datetime]) -> None:
    """Raise an HTTPException if the temporal bounds are the same."""
    start_time = temporal_params["from_datetime"]
    end_time = temporal_params["to_datetime"]

    if start_time is None or end_time is None:
        return None

    if start_time == end_time:
        raise HTTPException(status_code=400, detail="The temporal bounds must not be the same.")
