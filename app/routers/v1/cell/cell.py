from fastapi import APIRouter, Depends, Query
from app.dependencies import get_dw
from app.routers.v1.cell.models.cell_fact import CellFact
from app.routers.v1.cell.models.cell_size import CellSize
from datetime import datetime

router = APIRouter()

@router.get('')
def cell_facts(
        x_min: int = Query(example='3600000'),
        y_min: int = Query(example='3030000'),
        x_max: int = Query(example='4395000'),
        y_max: int = Query(example='3485000'),
        cell_size: CellSize = Query(default=CellSize.meter_5000),
        srid: int = Query(default=4326),
        upper_timestamp: datetime = Query(default=None, example='2022-01-01T00:00:00Z'),
        lower_timestamp: datetime = Query(default=None, example='2022-01-01T00:00:00Z'),
        stopped: bool = Query(default=None),
        limit: int = Query(default=None),
        offset: int = Query(default=None),
        dw = Depends(get_dw)) -> CellFact:
    return True