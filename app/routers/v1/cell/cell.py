"""Cell endpoint controller for the DIPAAL api."""
import os
import pandas as pd
import numpy as np

from app.dependencies import get_dw
from app.schemas.fact_cell import FactCell
from app.schemas.spatial_resolution import SpatialResolution
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Path
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()
current_file_path = os.path.dirname(os.path.abspath(__file__))


@router.get('/{cell_size}', response_model=List[FactCell])
def cell_facts(
        x_min: int = Query(example='3600000',
                           description='Defines the "left side" of the bounding rectangle,'
                           ' coordinates must match the provided "srid".'),
        y_min: int = Query(example='3030000',
                           description='Defines the "bottom side" of the bounding rectangle,'
                           ' coordinates must match the provided "srid".'),
        x_max: int = Query(example='4395000',
                           description='Defines the "right side" of the bounding rectangle,'
                           ' coordinates must match the provided "srid".'),
        y_max: int = Query(example='3485000',
                           description='Defines the "top side" of the bounding rectangle,'
                           ' coordinates must match the provided "srid".'),
        cell_size: SpatialResolution = Path(description='Defines the spatial resolution of the resulting cell facts.'),
        srid: int = Query(default=3034,
                          description='The srid projection used for the defined bounding rectangle.'),
        end_timestamp: datetime = Query(default=datetime.max,
                                        example='2022-01-01T00:00:00Z',
                                        description='The inclusive timestamp that defines'
                                        ' the end temporal bound of the result.'),
        start_timestamp: datetime = Query(default=datetime.min,
                                          example='2022-01-01T00:00:00Z',
                                          description='The inclusive timestamp that defines'
                                          ' the start temporal bound of the result.'),
        stopped: List[bool] = Query(default=[True, False], description='Looking at stopped and/or moving ships'),
        limit: int = Query(default=1000, ge=0, description='Limits the number of results returned.'),
        offset: int = Query(default=0, ge=0, description='Specifies the offset of the first result to return.'),
        dw: Session = Depends(get_dw)):
    """Get cell facts based on the given parameters."""
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


def convert_db_row_to_cell_fact(db_row: pd.Series) -> FactCell:
    """
    Convert from pandas series representation to an object based on FactCell schema.

    Keyword Arguments:
        db_row: Pandas series containing a single cell fact
    """
    timestamp_format: str = '%Y-%m-%dT%H:%M:%SZ'

    return FactCell.parse_obj({
        'x': db_row['x'],
        'y': db_row['y'],
        'trajectory_sub_id': db_row['trajectory_sub_id'],
        'entry_timestamp': db_row['entry_timestamp'].strftime(timestamp_format),
        'exit_timestamp': db_row['exit_timestamp'].strftime(timestamp_format),
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
            'ship_id': db_row['ship_id'],
            'mmsi': db_row['mmsi'],
            'imo': db_row['imo'],
            'name': db_row['name'],
            'callsign': db_row['callsign'],
            'ship_type': db_row['ship_type'],
            'mobile_type': db_row['mobile_type'],
            'flag_region': db_row['flag_region'],
            'flag_state': db_row['flag_state'],
            'location_system_type': db_row['location_system_type'],
            'a': db_row['a'],
            'b': db_row['b'],
            'c': db_row['c'],
            'd': db_row['d'],
            'length': db_row['length'],
            'width': db_row['width'],
        }
    })
