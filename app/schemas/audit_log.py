"""SQLAlchemy model for audit logs."""

from sqlalchemy import Column, DateTime, Integer, String, ARRAY
from sqlalchemy.dialects.postgresql import JSON

from app.database import Base


class AuditLog(Base):
    """SQLAlchemy model for audit logs."""

    __tablename__ = "audit_log"

    audit_id = Column(Integer, primary_key=True, index=True)
    import_datetime = Column(DateTime(timezone=True))
    file_size = Column(Integer)
    date_id = Column(Integer)
    total_delta_time = Column(Integer)
    statistics = Column(JSON)
    etl_version = Column(String)
    file_name = Column(String)
    requirements = Column(ARRAY(String))
