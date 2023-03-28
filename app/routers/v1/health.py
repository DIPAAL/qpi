"""FastAPI router for health check query."""

from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies import get_db

router = APIRouter()


@router.get("")
def health(response: Response, db: Session=Depends(get_db)):
    """Check the health of the API, for now just checks if database is reachable."""
    status = db.execute(text("SELECT 1")).fetchone()[0] == 1
    response.status_code = 200 if status else 500
    return {"status": "pass"} if status else {"status": "fail"}
