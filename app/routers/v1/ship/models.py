"""Database models for ship."""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.datawarehouse import Base

class DimShip(Base):
    """Ship dimension table."""
    __tablename__ = "dim_ship"

    ship_id = Column(Integer, primary_key=True, index=True)
    ship_type_id = Column(Integer, ForeignKey("dim_ship_type.ship_type_id"))
    imo = Column(Integer)
    mmsi = Column(Integer)
    name = Column(String)
    callsign = Column(String)
    a = Column(Float)
    b = Column(Float)
    c = Column(Float)
    d = Column(Float)
    location_system_type = Column(String)
    mid = Column(Integer)
    flag_region = Column(String)
    flag_state = Column(String)

    dim_ship_type = relationship("DimShipType", back_populates="dim_ship")

class DimShipType(Base):
    """Ship type dimension table"""
    __tablename__ = "dim_ship_type"

    ship_type_id = Column(Integer, primary_key=True, index=True)
    mobile_type = Column(String)
    ship_type = Column(String)

    dim_ship = relationship("DimShip", back_populates="dim_ship_type")