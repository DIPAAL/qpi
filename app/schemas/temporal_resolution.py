"""Define the allowed temporal resolutions."""
from enum import Enum


class TemporalResolution(str, Enum):
    """Enum of available temporal resolutions."""

    monthly = "monthly"
    hourly = "hourly"
    daily = "daily"
    quarterly = "quarterly"
    yearly = "yearly"
