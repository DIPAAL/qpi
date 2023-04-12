"""Define the allowed temporal resolutions."""
from enum import Enum


class TemporalResolution(str, Enum):
    """Enum of available temporal resolutions."""

    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    yearly = "yearly"
