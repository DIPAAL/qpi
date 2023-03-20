"""FastAPI router for health check query."""

from fastapi import APIRouter, Depends, Response

from app.dependencies import get_dw_cursor

router = APIRouter()


@router.get("")
def health(response: Response, dw_cursor=Depends(get_dw_cursor)):
    """Check the health of the API, for now just checks if database is reachable."""
    query = "SELECT 1"

    dw_cursor.execute(query)

    health = dw_cursor.fetchone()[0] == 1
    response.status_code = 200 if health else 500
    return {"status": "pass"} if health else {"status": "fail"}
