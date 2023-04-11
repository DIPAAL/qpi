"""Cell endpoint controller for the DIPAAL api."""
import os
import pandas as pd
import numpy as np

from app.dependencies import get_dw
from app.schemas.cell_fact import FactCell
from app.schemas.spatial_resolution import SpatialResolution
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()
current_file_path = os.path.dirname(os.path.abspath(__file__))


@router.get('', response_model=List[FactCell])
def cell_facts(
        x_min: int = Query(example='3600000', description='Defines the "left side" of the bounding rectangle, coordinates must match the provided "srid"'),  # noqa: E501
        y_min: int = Query(example='3030000', description='Defines the "bottom side" of the bounding rectangle, coordinates must match the provided "srid"'),  # noqa: E501
        x_max: int = Query(example='4395000', description='Defines the "right side" of the bounding rectangle, coordinates must match the provided "srid"'),  # noqa: E501
        y_max: int = Query(example='3485000', description='Defines the "top side" of the bounding rectangle, coordinates must match the provided "srid"'),  # noqa: E501
        cell_size: SpatialResolution = Query(default=SpatialResolution.five_kilometers, description='Defines the spatial resolution of the resulting cell facts'),  # noqa: E501
        srid: int = Query(default=3034, description='The srid projection used for the defined bounding rectangle'),
        end_timestamp: datetime = Query(default=datetime.max, example='2022-01-01T00:00:00Z', description='The inclusive timestamp that defines the end temporal bound of the result'),  # noqa: E501
        start_timestamp: datetime = Query(default=datetime.min, example='2022-01-01T00:00:00Z', description='The inclusive timestamp that defines the start temporal bound of the result'),  # noqa: E501
        stopped: List[bool] = Query(default=[True, False], description='Looking at stopped and/or moving ships'),
        limit: int = Query(default=1000, ge=0, description='How many results returned (pagination)'),
        offset: int = Query(default=0, ge=0, description='The result offset (pagination)'),
        dw: Session = Depends(get_dw)):
    """Return cell facts."""
    with open(os.path.join(current_file_path, 'sql/fact_cell_extract.sql')) as file:
        query = file.read().format(CELL_SIZE=int(cell_size))

    parameters = {
        'xmin': x_min,
        'ymin': y_min,
        'xmax': x_max,
        'ymax': y_max,
        'srid': srid,
        'stopped': stopped,
        'end_timestamp': end_timestamp,
        'start_timestamp': start_timestamp,
        'limit': limit,
        'offset': offset
    }
    df = pd.read_sql(text(query), dw.bind.connect(), params=parameters).replace(np.nan, None)

    dicts = [convert_db_row_to_cell_fact(row) for _, row in df.iterrows()]
    return JSONResponse(content=jsonable_encoder(dicts))


TIMESTAMP_FORMAT: str = '%Y-%m-%dT%H:%M:%SZ'


def convert_db_row_to_cell_fact(db_row: pd.Series) -> FactCell:
    """
    Convert from pandas series representation to an object based on FactCell schema.

    Keyword Arguments:
        db_row: Pandas series containing a single cell fact
    """
    return FactCell.parse_obj({
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
    })
