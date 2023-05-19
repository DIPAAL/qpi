"""FastAPI router for health check query."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.schemas.message import Message
from app.dependencies import get_dw

router = APIRouter()


@router.get("", response_model=Message,
            responses={
                503: {"model": Message}
            })
async def health(db: Session = Depends(get_dw)):
    """Check the health of the API, verifying that the data warehouse is accessible."""
    try:
        db.execute(text("SELECT 1")).fetchone()[0] == 1
    except Exception:
        return JSONResponse(status_code=503, content={"message": "Data warehouse is not accessible."})
    return Message(message="Data warehouse is accessible.")
