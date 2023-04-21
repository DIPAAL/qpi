"""Router for all trajectory endpoints."""
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, Path
from app.dependencies import get_dw
from sqlalchemy.orm import Session
from app.schemas.mobile_type import MobileType
from app.querybuilder import QueryBuilder
from helper_functions import response, update_params_datetime_min_max_if_none
import json
import os
from app.schemas.content_type import ContentType

router = APIRouter()

SQL_PATH = os.path.join(os.path.dirname(__file__), "SQL")


@router.get("/trajectories/{date_id}/{sub_id}")
async def get_trajectories_by_date_id_and_sub_id(
        date_id: int = Path(description="The date id of the trajectory.", example=20070110),
        sub_id: str = Path(description="The sub id of the trajectory.", example=49396455),
        dw=Depends(get_dw)):
    """Get trajectories for a start date id and its trajectory sub id."""
    params = {"date_id": date_id, "sub_id": sub_id}
    qb = QueryBuilder(SQL_PATH)
    qb.add_sql("select_date_id_and_sub_id.sql")
    final_query = qb.get_query_str()
    query_response = response(final_query, dw, params)
    query_response = _format_mfsjon(query_response, ["trajectory", "rot", "heading", "draught"])

    return query_response  # Returned as a JSON Array by FastAPI, providing conversion to avoiding serialization issues.


@router.get("/trajectories/}")
async def get_trajectories(
        offset: int = Query(default=0),
        limit: int = Query(default=10),
        x_min: float | None = Query(default=None,
                                    description="The minimum longitude of the trajectory."),
        y_min: float | None = Query(default=None,
                                    description="The minimum latitude of the trajectory."),
        x_max: float | None = Query(default=None,
                                    description="The maximum longitude of the trajectory."),
        y_max: float | None = Query(default=None,
                                    description="The maximum latitude of the trajectory."),
        destination: list[str] | None = Query(default=None,
                                              description="The destination of the ship sailing on the trajectory."),
        mmsi: list[int] | None = Query(default=None,
                                       description="The MMSI for the ship sailing on the trajectory."),
        imo: list[int] | None = Query(default=None,
                                      description="The IMO for the ship sailing on the trajectory."),
        name: list[str] | None = Query(default=None,
                                       description="The name for the ship sailing on the trajectory."),
        country: list[str] | None = Query(default=None,
                                          description="The country for the ship sailing on the trajectory."),
        callsign: list[str] | None = Query(default=None,
                                           description="The callsign for the ship sailing on the trajectory."),
        mobile_type: list[MobileType] | None = Query(default=None,
                                                     description="The mobile type for the ship"
                                                                 " sailing on the trajectory."),
        srid: int = Query(default=4326,
                          description="The spatial reference system for the trajectory."),
        from_date: datetime | None = Query(default=None,
                                           description="The start date for the trajectory."),
        to_date: datetime | None = Query(default=None,
                                         description="The end date for the trajectory."),
        stopped: bool | None = Query(default=None,
                                     description="If the trajectory must represents a stopped ship."),
        content_type: ContentType = Query(default=[ContentType.MFJSON],
                                          description="The content type of the response."),
        dw: Session = Depends(get_dw)
):
    """Get trajectories based on the provided parameters."""
    params = {"offset": offset, "limit": limit}
    trajectory_params = {"stopped": stopped}
    ship_params = {
        "mmsi": mmsi, "imo": imo, "name": name,
        "country": country, "callsign": callsign, "mobile_type": mobile_type
    }
    nav_status_params = {"destination": destination}
    temporal_params = {"from_date": from_date, "to_date": to_date}
    # SRID is not required to be complete, and is therefore not part of this dict.
    spatial_params = {"x_min": x_min, "y_min": y_min, "x_max": x_max, "y_max": y_max}

    qb = QueryBuilder(SQL_PATH)

    # Adding SELECT, FROM and JOIN clauses to the query, depending on the requested content type.
    if ContentType.MFJSON:
        qb.add_sql("select_MFJSON.sql")
    elif ContentType.GEOJSON:
        qb.add_sql("select_GeoJSON.sql")
    else:
        raise HTTPException(status_code=400, detail="Invalid content type")

    # If parameters for ships is provided, a JOIN clause between the fact_trajectory and dim_ship is added to the query.
    if any(value is not None for value in ship_params.values()):
        qb.add_string("JOIN dim_ship ds on ft.ship_id = ds.ship_id")

    # If certain parameters are provided, then they are added to the query as a WHERE/AND clause, filtering results.
    _filter_in(qb, params, {"ft": trajectory_params, "ds": ship_params, "dns": nav_status_params})

    # Check if any temporal or spatial parameters are provided and update the parameters accordingly.
    temporal_bounds = _update_params(params, temporal_params)
    update_params_datetime_min_max_if_none(params, temporal_params)
    spatial_bounds = _update_params(params, spatial_params)

    # If spatial bounds are provided, but not complete, raise an error.
    if spatial_bounds and None in spatial_params.values():
        raise HTTPException(status_code=400, detail="Spatial bounds not complete")

    _update_params(params, {"srid": srid}) if spatial_bounds else None

    # If temporal or spatial bounds are provided, a WHERE/AND clause is added to the query, filtering results.
    _filter_temporal_spatial(qb, spatial_bounds, temporal_bounds)

    # Clause for order by, offset and limit is added to the query
    qb.add_string("ORDER BY ft.trajectory_sub_id OFFSET :offset LIMIT :limit;")

    final_query = qb.get_query_str()
    print(final_query)
    query_response = response(final_query, dw, params)
    query_response = _format_mfsjon(query_response, ["trajectory", "rot", "heading", "draught"])
    return query_response  # Returned as a JSON Array by FastAPI, providing conversion to avoiding serialization issues.


def _update_params(params: dict, param_dict: dict):
    """
    Update the params dict with the values from param_dict if the value is not None.

    Returns:
        bool: True if any value was updated, False otherwise.
    """
    update = False
    for key, value in param_dict.items():
        if value is not None:
            params[key] = value
            update = True
    return update


def _filter_in(qb: QueryBuilder, params: dict, filter_dict: dict):
    """
    Add a WHERE/AND clause with and IN operator to the query for each value in the filter_dict that is not None.

     Args:
         qb (QueryBuilder): The QueryBuilder object to add the WHERE/AND clause to.
         params (dict): The params dict to add the values to.
         filter_dict (dict):
    """
    for relation, param_dict in filter_dict.items():
        for key, value in param_dict.items():
            if value is not None:
                qb.add_where(relation + "." + key, "IN", value, params)


def _filter_temporal_spatial(qb: QueryBuilder, spatial_bounds: bool, temporal_bounds: bool):
    """Add temporal and spatial filters to the query if bounds are provided."""
    bound_placeholder = None
    if temporal_bounds or spatial_bounds:
        qb.add_string("STBOX({BOUNDS}) && dt.trajectory))")
        # Adding spatial filters to the query if provided
        if spatial_bounds:
            bound_placeholder = "ST_MakeEnvelope(:xmin,:ymin,: xmax,:ymax, :srid)"
        # Adding temporal filters to the query if provided
        if temporal_bounds:
            if bound_placeholder is not None:
                bound_placeholder += ", "
            bound_placeholder += "span(timestamp_from_date_time_id(:from_date, :from_time), " \
                                 "timestamp_from_date_time_id(:to_date, :to_time), True, True)"
    qb.format_query({"BOUNDS": bound_placeholder}) if bound_placeholder is not None else None


def _format_mfsjon(response_result: list[dict], attributes: list[str]) -> list[dict]:
    """
    Convert the MFSJON strings to a python dictionary, so FastAPI can convert it to JSON for the response.

    Args:
        response_result (list[dict]): The response from the data warehouse
        attributes (list[str]): The attributes that are MFSJON strings

    Returns:
        list[dict]: The response with the MFSJON strings converted to python dictionaries
    """
    for key in response_result:
        for attribute in attributes:
            if key[attribute] is not None:
                key[attribute] = json.loads(key[attribute])
    return response_result
