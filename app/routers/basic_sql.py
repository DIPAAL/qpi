from fastapi import APIRouter
from app.dependencies import CURSOR, DWTable
# from pydantic import BaseModel


router = APIRouter()


@router.get("/count_row_table/{table}")
def count_row_table(table: DWTable):
    CURSOR.execute(f"SELECT COUNT(*) FROM {table}")
    return CURSOR.fetchall()

@router.get("/get_coloumn_names/")
def get_column_names(table: DWTable):
    CURSOR.execute(f"SELECT * FROM {table} LIMIT 0")
    return [desc[0] for desc in CURSOR.description]






