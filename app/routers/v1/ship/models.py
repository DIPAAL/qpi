"""Database models for ship."""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Interval
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

    # Relations that have a foreign key from this table
    dim_ship_type = relationship("DimShipType", back_populates="dim_ship")
    # Relations that have a foreign key to this table
    fact_trajectory = relationship("FactTrajectory", back_populates="dim_ship")

class DimShipType(Base):
    """Ship type dimension table"""
    __tablename__ = "dim_ship_type"

    ship_type_id = Column(Integer, primary_key=True, index=True)
    mobile_type = Column(String)
    ship_type = Column(String)

    dim_ship = relationship("DimShip", back_populates="dim_ship_type")

class FactTrajectory(Base):
    """Trajectory fact table"""
    __tablename__ = "fact_trajectory"

    duration = Column(Interval)
    ship_id = Column(Integer, ForeignKey("dim_ship.ship_id"), primary_key=True)
    start_date_id = Column(Integer, ForeignKey("dim_date.date_id"), primary_key=True)
    end_date_id = Column(Integer, ForeignKey("dim_date.date_id"), primary_key=True)
    eta_date_id = Column(Integer, ForeignKey("dim_date.date_id"), primary_key=True)
    end_time_id = Column(Integer, ForeignKey("dim_time.time_id"), primary_key=True)
    start_time_id = Column(Integer, ForeignKey("dim_time.time_id"), primary_key=True)
    eta_time_id = Column(Integer, ForeignKey("dim_time.time_id"), primary_key=True)
    trajectory_sub_id = Column(Integer, ForeignKey("dim_trajectory.trajectory_sub_id"), primary_key=True)
    nav_status_id = Column(Integer, ForeignKey("dim_nav_status.nav_status_id"), primary_key=True)
    length = Column(Integer)
    infer_stopped = Column(Boolean)

    # Relations that have a foreign key from this table
    # Relations that are not yet implemented as models, are commented out
    # dim_trajectory = relationship("DimTrajectory", back_populates="fact_trajectory")
    # dim_nav_status = relationship("DimNavStatus", back_populates="fact_trajectory")
    dim_date = relationship("DimDate")
    dim_time = relationship("DimTime")
    dim_ship = relationship("DimShip", back_populates="fact_trajectory")

# DimTrajectory can't be implemented as a model, because it contains MobilityDB types (TFloat, TGeomPoint)
# Those types are not supported by SQLAlchemy, and mobilitydb-sqlalchemy is too outdated to be of any use.

class DimDate(Base):
    """Date dimension table"""
    __tablename__ = "dim_date"

    date_id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    month_of_year = Column(Integer)
    quarter_of_year = Column(Integer)
    week_of_year = Column(Integer)
    day_of_year = Column(Integer)
    day_of_month = Column(Integer)
    day_of_week = Column(Integer)
    day_name = Column(String)
    month_name = Column(String)
    weekday = Column(String)
    season = Column(String)
    holiday = Column(String)

    # Relations that have a foreign key to this table
    fact_trajectory = relationship("FactTrajectory", back_populates="dim_date")

class DimTime(Base):
    __tablename__ = "dim_time"

    time_id = Column(Integer, primary_key=True, index=True)
    hour = Column(Integer)
    minute = Column(Integer)
    second = Column(Integer)

    # Relations that have a foreign key to this table
    fact_trajectory = relationship("FactTrajectory", back_populates="dim_time")