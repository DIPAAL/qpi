from sqlalchemy.orm import Session

from app.routers.v1.ship import models, schemas


def get_ship(dw: Session, ship_id: int):
    return dw.query(models.DimShip).filter(models.DimShip.ship_id == ship_id).first()
def get_ship_by_mmsi(dw: Session, mmsi: int):
    return dw.query(models.DimShip).filter(models.DimShip.mmsi == mmsi).first()

def get_ships(dw: Session, skip: int = 0, limit: int = 100):
    return dw.query(models.DimShip).offset(skip).limit(limit).all()

def get_ship_types(dw: Session, skip: int = 0, limit: int = 100):
    return dw.query(models.DimShipType).offset(skip).limit(limit).all()

