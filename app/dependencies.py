"""FastAPI dependencies for dependency injection into routers or the main app."""
from app.datawarehouse import SessionLocal


def get_dw():
    """Use the globally scoped sessionmaker to create a db session scoped to the request."""
    dw = SessionLocal()
    try:
        yield dw
    finally:
        dw.close()
