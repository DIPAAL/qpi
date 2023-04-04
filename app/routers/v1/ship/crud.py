from sqlalchemy.orm import Session

from app.routers.v1.ship import models
from helper_functions import get_file_contents_as_text
import os

# Path to sql files
sql_path = os.path.join(os.path.dirname(__file__), "sql")

def get_ship(dw: Session, ship_id: int):
    return dw.query(models.DimShip).filter(models.DimShip.ship_id == ship_id).first()
def get_ship_by_mmsi(dw: Session, mmsi: int):
    return dw.query(models.DimShip).filter(models.DimShip.mmsi == mmsi).first()

def get_ships(dw: Session, skip: int = 0, limit: int = 100):
    return dw.query(models.DimShip).offset(skip).limit(limit).all()

def get_ship_types(dw: Session, skip: int = 0, limit: int = 100):
    return dw.query(models.DimShipType).offset(skip).limit(limit).all()

def get_ships_by_spatial_bounds(dw: Session, min_x, min_y, max_x, max_y):
    pass


def get_ships_by_temporal_bounds(dw: Session, from_date, to_date):
    path = os.path.join(sql_path, "temporal_bounds.sql")
    return dw.execute(get_file_contents_as_text(path), {"from_date": from_date, "to_date": to_date})
