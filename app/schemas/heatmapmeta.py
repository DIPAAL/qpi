"""Model for portraying the metadata of a heatmap."""
from pydantic import BaseModel
from datetime import datetime


class TemporalDomain(BaseModel):
    """Model for portraying the temporal domain of a heatmap."""

    start: datetime
    end: datetime


class TemporalResolution(BaseModel):
    """Model for portraying the resolution of a heatmap."""

    resolution: int
    units: str
    temporal_domain: TemporalDomain


class CellSize(BaseModel):
    """Model for portraying the cell size of a heatmap."""

    resolution: int
    units: str
    temporal_resolutions: dict[str, TemporalResolution]


class HeatmapMetadata(BaseModel):
    """Model for portraying the metadata of a heatmap."""

    name: str
    description: str
    spatial_resolutions: dict[str, CellSize]
