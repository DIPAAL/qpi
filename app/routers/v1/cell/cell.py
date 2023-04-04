"""Cell endpoint controller for the DIPAAL api."""
import os
import pandas as pd

from app.dependencies import get_dw
from app.routers.v1.cell.models.cell_fact import FactCell
from app.routers.v1.heatmap.models.spatial_resolution import SpatialResolution
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Dict

router = APIRouter()
current_file_path = os.path.dirname(os.path.abspath(__file__))


@router.get('')
def cell_facts(
        x_min: int = Query(example='3600000'),
        y_min: int = Query(example='3030000'),
        x_max: int = Query(example='4395000'),
        y_max: int = Query(example='3485000'),
        cell_size: SpatialResolution = Query(default=SpatialResolution.five_kilometers),
        srid: int = Query(default=3034),
        upper_timestamp: datetime = Query(default=None, example='2022-01-01T00:00:00Z'),
        lower_timestamp: datetime = Query(default=None, example='2022-01-01T00:00:00Z'),
        stopped: List[bool] = Query(default=[True, False]),
        limit: int = Query(default=1000, ge=0),
        offset: int = Query(default=0, ge=0),
        dw: Session = Depends(get_dw)) -> List[FactCell]:
    """Return cell facts."""
    with open(os.path.join(current_file_path, 'sql/fact_cell_extract.sql')) as file:
        query = file.read().format(CELL_SIZE=int(cell_size))

    parameters = {
        'xmin': x_min,
        'ymin': y_min,
        'xmax': x_max,
        'ymax': y_max,
        'srid': srid,
        'stopped': [True, False] if stopped is None else [stopped],
        'upper_timestamp': datetime.max if upper_timestamp is None else upper_timestamp,
        'lower_timestamp': datetime.min if lower_timestamp is None else lower_timestamp,
        'limit': limit,
        'offset': offset
    }
    df = pd.read_sql(text(query), dw.bind.connect(), params=parameters).fillna("null")

    dicts = [cell_fact_to_dict(row) for _, row in df.iterrows()]
    return JSONResponse(dicts, media_type='application/json')


TIMESTAMP_FORMAT: str = '%Y-%m-%dT%H:%M:%SZ'


def cell_fact_to_dict(db_row: pd.Series) -> Dict:
    """
    Convert from pandas series representation to return type as a dictionary.

    Keyword Arguments:
        db_row: Pandas series containing a single cell fact
    """
    return {
        'x': db_row['x'],
        'y': db_row['y'],
        'trajectory_sub_id': db_row['trajectory_sub_id'],
        'entry_timestamp': db_row['entry_timestamp'].strftime(TIMESTAMP_FORMAT),
        'exit_timestamp': db_row['exit_timestamp'].strftime(TIMESTAMP_FORMAT),
        'navigational_status': db_row['navigational_status'],
        'direction': {
            'begin': db_row['begin'],
            'end': db_row['end']
        },
        'sog': db_row['sog'],
        'delta_cog': db_row['delta_cog'],
        'delta_heading': db_row['delta_heading'],
        'draught': db_row['draught'],
        'stopped': str(db_row['stopped']).lower(),
        'ship': {
            'mmsi': db_row['mmsi'],
            'imo': db_row['imo'],
            'name': db_row['name'],
            'type': db_row['ship_type'],
            'mobile': db_row['mobile_type'],
            'flag_state': db_row['flag_state']
        }
    }
