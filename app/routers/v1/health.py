"""FastAPI router for health check query."""

from fastapi import APIRouter
from app.dependencies import get_dw_cursor

router = APIRouter()


@router.get("")
def health():
    """Check the health of the API, for now just checks if database is reachable."""
    query = "SELECT 1"
    dw_cursor = get_dw_cursor()

    dw_cursor.execute(query)
    return {"status": "ok" if dw_cursor.fetchone()[0] == 1 else "fail"}
