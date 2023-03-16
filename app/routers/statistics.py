"""FastAPI router for statistical endpoints."""
from fastapi import APIRouter, Depends
from ..dependencies import get_dw_cursor
from helper_functions import readfile

router = APIRouter()


# Currently produces error: "Cannot calculate the size because relation 'dim_raster' is not distributed"
@router.get("/api/vi/misc/table_size")
def table_size(dw_cursor=Depends(get_dw_cursor)):
    """Return the size of all distributed tables."""
    query = readfile("app/routers/sql/distributed_table_size.sql")
    dw_cursor.execute(query)
    return dw_cursor.fetchall()
