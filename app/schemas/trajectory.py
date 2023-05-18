"""Model representing a trajectory in the DIPAAL data warehouse."""

from pydantic import BaseModel, Field
from datetime import datetime

# Add example values where appropriate


class MFJSON(BaseModel):
    """Model for Moving Features JSON."""

    type: str = Field(description="The type of data.")
    values: list[int] = Field(description="The values for the type of data.")
    datetimes: list[datetime] = Field(description="The datetimes for the type of data.")
    lower_inc: bool = Field(description="Whether the lower bound is inclusive or not.")
    upper_inc: bool = Field(description="Whether the upper bound is inclusive or not.")
    interpolation: str = Field(description="The interpolation method used.")


class CRS(BaseModel):
    """Model for Coordinate Reference System."""

    type: str = Field(description="The type of Coordinate Reference System.")
    properties: dict[str, str] = Field(description="The properties for that type of Coordinate Reference System.")


class MFJSONTrajectory(BaseModel):
    """Model for Moving Features JSON Trajectory."""

    type: str = Field(description="The type of data.")
    crs: CRS = Field(description="The Coordinate Reference System of the trajectory.")
    coordinates: list[list[float, float]] = Field(description="The coordinates of the trajectory.")
    datetimes: list[datetime] = Field(description="The datetimes of the trajectory.")
    lower_inc: bool = Field(description="Whether the lower bound is inclusive or not.")
    upper_inc: bool = Field(description="Whether the upper bound is inclusive or not.")
    interpolation: str = Field(description="The interpolation method used.")


class GeoJSONInnerTrajectory(BaseModel):
    """Model for the inner trajectory of a GeoJSON Trajectory."""

    crs: CRS = Field(description="The Coordinate Reference System of the trajectory.")
    type: str = Field(description="The type of trajectory.")
    datetimes: list[datetime] = Field(description="The datetimes of the trajectory.")
    coordinates: list[(float, float)] = Field(description="The coordinates of the trajectory.")


class GeoJSONTrajectory(BaseModel):
    """Model for GeoJSON Trajectory."""

    trajectory: GeoJSONInnerTrajectory


class BaseTrajectory(BaseModel):
    """Base Trajectory Model."""

    trajectory_sub_id: int = Field(description="The sub id of the trajectory.")
    start_timestamp: datetime = Field(description="The start timestamp of the trajectory.")
    end_timestamp: datetime = Field(description="The end timestamp of the trajectory.")
    eta_timestamp: datetime = Field(description="The estimated time of arrival of the trajectory.")
    trajectory: None
    rot: list[MFJSON] | None = Field(description="The rate of turn of the trajectory as Moving Features JSON.")
    heading: list[MFJSON] | None = Field(description="The heading of the trajectory as Moving Features JSON.")
    draught: list[MFJSON] | None = Field(description="The draught of the trajectory as Moving Features JSON.")
    destination: str | None = Field(description="The destination of the trajectory.")
    duration: int = Field(description="The duration of the trajectory.")
    length: int = Field(description="The length of the trajectory.")
    stopped: bool = Field(description="Whether the trajectory represents a stopped ship or not.")
    navigational_status: str = Field(description="The navigational status of the trajectory.")


class MFJSONTrajectoryResponse(BaseTrajectory):
    """Model for Moving Features JSON Trajectory."""

    trajectory: list[MFJSONTrajectory] = Field(description="The trajectory as Moving Features JSON.")


class GeoJSONTrajectoryResponse(BaseTrajectory):
    """Model for GeoJSON Trajectory."""

    trajectory: list[GeoJSONTrajectory] = Field(description="The trajectory as GeoJSON.")
