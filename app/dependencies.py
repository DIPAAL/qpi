"""FastAPI dependencies for dependency injection into routers or the main app."""
from app.database import SessionLocal


def get_dw():
    """Use the globally scoped sessionmaker to create a db session scoped to the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
