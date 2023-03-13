"""FastAPI router for statistics endpoints."""
from fastapi import APIRouter
from ..dependencies import CURSOR, readfile

router = APIRouter()


# Currently produces error: "Cannot calculate the size because relation 'dim_raster' is not distributed"
@router.get("/distributed_table_size")
def distributed_table_size():
    """Return the size of all distributed tables."""
    query = readfile("app/routers/sql/distributed_table_size.sql")
    CURSOR.execute(query)
    return CURSOR.fetchall()
