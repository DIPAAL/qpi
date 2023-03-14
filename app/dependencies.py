"""FastAPI dependencies for dependency injection into routers or the main app"""
from .constants import CURSOR

def get_dw_cursor():
    """Return a cursor to the data warehouse database."""
    return CURSOR