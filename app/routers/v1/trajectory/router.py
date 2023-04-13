"""Router for all trajectory endpoints."""
import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from app.dependencies import get_dw
from sqlalchemy.orm import Session
from app.schemas.mobile_type import MobileType

router = APIRouter()

@router.get("/trajectories/{date_id}/{sub_id}")
async def get_trajectories_by_date_id_and_sub_id(
        date_id: datetime.datetime,
        sub_id: str,
        dw=Depends(get_dw)):

    params = {
        "date_id": date_id,
        "sub_id": sub_id,
    }

    # TODO: Setup query from file, then run it and return the result

    pass
    """Get trajectories for a start date id and its trajectory sub id."""


@router.get("/trajectories/}")
async def get_trajectories(
        offset: int = Query(default=0),
        limit: int = Query(default=10),
        x_min: float = Query(default=None,
                             description="The minimum longitude of the trajectory."),
        y_min: float = Query(default=None,
                             description="The minimum latitude of the trajectory."),
        x_max: float = Query(default=None,
                             description="The maximum longitude of the trajectory."),
        y_max: float = Query(default=None,
                             description="The maximum latitude of the trajectory."),
        destination: list[str] = Query(default=None,
                                       description="The destination of the ship sailing on the trajectory."),
        mmsi: list[str] = Query(default=None,
                                description="The MMSI for the ship sailing on the trajectory."),
        imo: list[str] = Query(default=None,
                               description="The IMO for the ship sailing on the trajectory."),
        name: list[str] = Query(default=None,
                                description="The name for the ship sailing on the trajectory."),
        country: list[str] = Query(default=None,
                                   description="The country for the ship sailing on the trajectory."),
        callsign: list[str] = Query(default=None,
                                    description="The callsign for the ship sailing on the trajectory."),
        mobile_type: list[MobileType] = Query(default=None,
                                       description="The mobile type for the ship sailing on the trajectory."),
        srid: int = Query(default=4326,
                          description="The spatial reference system for the trajectory."),
        from_date: datetime.datetime = Query(default=None),
        to_date: datetime.datetime = Query(default=None),
        stopped: bool = Query(default=None,
                              description="If the trajectory must represents a stopped ship."),
        dw: Session = Depends(get_dw)
):
    params = {
        "offset": offset,
        "limit": limit,
    }
    trajectory_params = {
        srid: srid,
        stopped: stopped,
    }
    ship_params = {
        destination: destination,
        mmsi: mmsi,
        imo: imo,
        name: name,
        country: country,
        callsign: callsign,
        mobile_type: mobile_type
    }
    temporal_params = {
        "from_date": from_date,
        "to_date": to_date,
    }
    spatial_params = {
        "x_min": x_min,
        "y_min": y_min,
        "x_max": x_max,
        "y_max": y_max,
    }
    """Get trajectories based on the provided parameters."""

    # Add SELECT statement to query

    # Add FROM statement to query

    if ship_params:
        # add JOIN ship to query
        pass

    # Add WHERE/AND statement(s) to query based on the provided parameters
    pass

