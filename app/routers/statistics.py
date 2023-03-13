from fastapi import APIRouter
from ..dependencies import CURSOR, readfile
from enum import Enum

router = APIRouter()


@router.get("/distributed_table_size")  # Currently produces error: "Cannot calculate the size because relation 'dim_raster' is not distributed"
def distributed_table_size():
    query = readfile("app/routers/sql/distributed_table_size.sql")
    CURSOR.execute(query)
    return CURSOR.fetchall()

