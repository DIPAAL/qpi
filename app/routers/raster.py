from fastapi import APIRouter

router = APIRouter()

@router.get("/raster")
def raster():
    return {"Message": "The create raster endpoint is not yet implemented"}