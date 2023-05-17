"""Model representing a trajectory in the DIPAAL data warehouse."""

from pydantic import BaseModel
from datetime import datetime

# Add example values where appropriate


class MFJSON(BaseModel):
    """Model for Moving Features JSON."""

    type: str = "MovingFloat"
    values: list[int] = [54.2, 221.5]
    datetimes: list[datetime] = datetime(2021, 1, 1, 1, 0, 0), datetime(2021, 1, 1, 8, 0, 0)
    lower_inc: bool = True
    upper_inc: bool = True
    interpolation: str = "Step"


class CRS(BaseModel):
    """Model for Coordinate Reference System."""

    type: str = "name"
    properties: dict[str, str] = {"name": "EPSG:4326"}


class MFJSONTrajectory(BaseModel):
    """Model for Moving Features JSON Trajectory."""

    type: str = "MovingGeomPoint"
    crs: CRS
    coordinates: list[list[float, float]] = [[14.605, 12.504], [24.304, 13.236]]
    datetimes: list[datetime] = [datetime(2021, 1, 1, 1, 0, 0), datetime(2021, 1, 1, 8, 0, 0)]
    lower_inc: bool = True
    upper_inc: bool = True
    interpolation: str = "Linear"


class GeoJSONInnerTrajectory(BaseModel):
    """Model for the inner trajectory of a GeoJSON Trajectory."""

    crs: CRS
    type: str = "LineString"
    datetimes: list[datetime]
    coordinates: list[(float, float)] = [[14.605, 12.504], [24.304, 13.236]]


class GeoJSONTrajectory(BaseModel):
    """Model for GeoJSON Trajectory."""

    trajectory: GeoJSONInnerTrajectory


class BaseTrajectory(BaseModel):
    """Base Trajectory Model."""

    trajectory_sub_id: int
    start_timestamp: datetime = datetime(2021, 1, 1, 1, 0, 0)
    end_timestamp: datetime = datetime(2021, 1, 1, 8, 0, 0)
    eta_timestamp: datetime = datetime(2021, 1, 2, 2, 0, 0)
    trajectory: None
    rot: list[MFJSON] | None
    heading: list[MFJSON] | None
    draught: list[MFJSON] | None
    destination: str = "TERNEUZEN VIA NOK"
    duration: int = 7
    length: int = 44
    stopped: bool = False
    navigational_status: str = "Under way using engine"


class MFJSONTrajectoryResponse(BaseTrajectory):
    """Model for Moving Features JSON Trajectory."""

    trajectory: list[MFJSONTrajectory]


class GeoJSONTrajectoryResponse(BaseTrajectory):
    """Model for GeoJSON Trajectory."""

    trajectory: list[GeoJSONTrajectory]
