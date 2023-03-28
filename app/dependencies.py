"""FastAPI dependencies for dependency injection into routers or the main app."""
from app.database import SessionLocal

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()