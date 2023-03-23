"""FastAPI dependencies for dependency injection into routers or the main app."""
import psycopg2.extras

from helper_functions import get_connection


def get_dw_cursor():
    """Return a cursor to the data warehouse database."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return cursor
