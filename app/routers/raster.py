"""FastAPI router for raster endpoints."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/raster")
def raster():
    """Return a raster."""
    return {"Message": "The create raster endpoint is not yet implemented"}
