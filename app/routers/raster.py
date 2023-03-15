"""FastAPI router for raster endpoints."""
from fastapi import APIRouter, Depends
from ..dependencies import get_dw_cursor

router = APIRouter()


@router.get("/raster")
def raster(dw_cursor=Depends(get_dw_cursor)):
    """Return a raster."""
    return {"Message": "The create raster endpoint is not yet implemented"}
