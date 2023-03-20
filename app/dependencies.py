"""FastAPI dependencies for dependency injection into routers or the main app."""
from helper_functions import get_connection


def get_dw_cursor():
    """Return a cursor to the data warehouse database."""
    conn = get_connection()
    cursor = conn.cursor()
    return cursor
