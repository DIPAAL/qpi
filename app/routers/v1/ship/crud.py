from sqlalchemy.orm import Session

from app.routers.v1.ship import models
from app.routers.v1.ship.sql.sqlrunner import get_sql_file_contents



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
    return dw.query(models.FactTrajectory).join(models.DimShip).filter(
        models.FactTrajectory.start_date_id >= from_date,
        models.FactTrajectory.end_date_id <= to_date).all()

def get_ships_by_temporal_bounds_as_df(dw: Session, from_date, to_date):
    return dw.execute(get_sql_file_contents("spatial_bounds.sql"), {"from_date": from_date, "to_date": to_date})
