"""FastAPI dependencies for dependency injection into routers or the main app."""
from helper_functions import get_connection
from app.datawarehouse import SessionLocal


def get_dw_cursor():
    """Return a cursor to the data warehouse database."""
    conn = get_connection()
    cursor = conn.cursor()
    return cursor


def get_dw():
    """Use the globally scoped sessionmaker to create a db session scoped to the request."""
    dw = SessionLocal()
    try:
        yield dw
    finally:
        dw.close()
