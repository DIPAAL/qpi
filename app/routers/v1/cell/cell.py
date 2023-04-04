"""Cell endpoint controller for the DIPAAL api."""
import json
import os
import pandas as pd

from app.dependencies import get_dw
from app.routers.v1.cell.models.cell_fact import FactCell
from app.routers.v1.cell.models.cell_size import CellSize
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()
current_file_path = os.path.dirname(os.path.abspath(__file__))


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
        dw: Session = Depends(get_dw)) -> List[FactCell]:
    """Return cell facts."""
    with open(os.path.join(current_file_path, 'sql/fact_cell_extract.sql')) as file:
        query = file.read().format(CELL_SIZE=cell_size)

    parameters = {
        'xmin': x_min,
        'ymin': y_min,
        'xmax': x_max,
        'ymax': y_max,
        'srid': 4326 if srid is None else srid,
        'stopped': [True, False] if stopped is None else [stopped],
        'upper_timestamp': datetime.max if upper_timestamp is None else upper_timestamp,
        'lower_timestamp': datetime.min if lower_timestamp is None else lower_timestamp,
        'limit': 1000 if limit is None else limit,
        'offset': 0 if offset is None else offset
    }
    df = pd.read_sql(text(query), dw.bind.connect(), params=parameters).fillna("null")

    raw_json = [cell_fact_to_json(row) for _, row in df.iterrows()]
    return JSONResponse(json.dumps(raw_json, indent=2), media_type='application/json')


def cell_fact_to_json(db_row: pd.Series):
    """
    Convert from pandas series representation to return type as json.

    Keyword Arguments:
        db_row: Pandas series containing a single cell fact
    """
    return f""" {{
        "x": {db_row['x']},
        "y": {db_row['y']},
        "trajectory_sub_id": {db_row['trajectory_sub_id']},
        "entry_timestamp": "{db_row['entry_timestamp']}",
        "exit_timestamp": "{db_row['exit_timestamp']}",
        "navigational_status": "{db_row['navigational_status']}",
        "direction": {{
            "begin": "{db_row['begin']}",
            "end": "{db_row['end']}"
        }},
        "sog": {db_row['sog']},
        "delta_cog": {db_row['delta_cog']},
        "delta_heading": {db_row['delta_heading']},
        "draught": {db_row['draught']},
        "stopped": {str(db_row['stopped']).lower()},
        "ship": {{
            "mmsi": {db_row['mmsi']},
            "imo": {db_row['imo']},
            "name": "{db_row['name']}",
            "type": "{db_row['ship_type']}",
            "mobile": "{db_row['mobile_type']}",
            "flag_state": "{db_row['flag_state']}"
        }}
    }}"""
