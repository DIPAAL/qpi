"""FastAPI dependencies for dependency injection into routers or the main app"""
# from .api_constants import CURSOR
from helper_functions import get_connection

def get_dw_cursor():
    """Return a cursor to the data warehouse database."""
    conn = get_connection()
    return conn.cursor