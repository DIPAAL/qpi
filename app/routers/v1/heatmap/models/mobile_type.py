"""Define the allowed mobile types."""
from enum import Enum


class MobileType (str, Enum):
    """The available filters for mobile type."""

    class_a = "Class A"
    class_b = "Class B"
