from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class DimShip(Base):
    __tablename__ = 'dim_ship'

    ship_id = Column(Integer, primary_key=True)
    ship_type_id = Column(Integer, ForeignKey('dim_ship_type.ship_type_id'))
    imo = Column(Integer)
    mmsi = Column(Integer)
    name = Column(String)
    call_sign = Column(String)
    a = Column(Float)
    b = Column(Float)
    c = Column(Float)
    d = Column(Float)
    location_system_type = Column(String)

    dim_ship_type = relationship("DimShipType", back_populates="dim_ship")

class DimShipType(Base):
    __tablename__ = 'dim_ship_type'

    ship_type_id = Column(Integer, primary_key=True)
    mobile_type = Column(String)
    ship_type = Column(String)

    dim_ship = relationship("DimShip", back_populates="dim_ship_type")