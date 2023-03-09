from fastapi import APIRouter
from app.dependencies import CURSOR

router = APIRouter()


@router.get("/rawsql")
def insert_(sql: str):
    CURSOR.execute(sql)
    return CURSOR.fetchall()


@router.get("/select")
def select(select: str, table: str):
    CURSOR.execute(f"SELECT {select} FROM {table}")
    return CURSOR.fetchall()



