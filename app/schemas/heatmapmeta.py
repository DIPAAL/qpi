"""Model for portraying the metadata of a heatmap."""
from pydantic import BaseModel, Field
from datetime import datetime


class TemporalDomain(BaseModel):
    """Model for portraying the temporal domain of a heatmap."""

    start: datetime = Field(description='The start of the temporal domain')
    end: datetime = Field(description='The end of the temporal domain')


class TemporalResolution(BaseModel):
    """Model for portraying the resolution of a heatmap."""

    resolution: int = Field(description='The temporal resolution of the heatmap.')
    units: str = Field(description='The units of the temporal resolution.')
    temporal_domain: TemporalDomain = Field(description='The temporal domain of the heatmap.')


class CellSize(BaseModel):
    """Model for portraying the cell size of a heatmap."""

    resolution: int = Field(description='The size of the cell.')
    units: str = Field(description='The units of the cell size.')
    temporal_resolutions: dict[str, TemporalResolution] = Field(description='The temporal resolutions of the cell.')


class HeatmapMetadata(BaseModel):
    """Model for portraying the metadata of a heatmap."""

    name: str = Field(description='Name for the type of heatmap.')
    description: str = Field(description='Description of the heatmap type.')
    spatial_resolutions: dict[str, CellSize] = Field(description='The spatial resolutions of the heatmap, '
                                                                 'each containing additional information.')
