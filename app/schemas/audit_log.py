"""Models for audit logs."""

from sqlalchemy import Column, DateTime, Integer, String, ARRAY
from sqlalchemy.dialects.postgresql import JSON

from app.datawarehouse import Base
from pydantic import BaseModel, Field
from datetime import datetime


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


class AuditLogResponse(BaseModel):
    """Pydantic model for portraying the audit log output."""

    file_size: int = Field(description='The size of the file in bytes.')
    total_delta_time: int = Field(description='The total time it took to process the file in seconds.')
    etl_version: str = Field(description='The version of the ETL script used to process the file.')
    requirements: list[str] = Field(description='The external libraries used to process the file.')
    audit_id: int = Field(description='The id of the audit log.')
    import_datetime: datetime = Field(description='The timestamp of when the file was processed.')
    date_id: int = Field(description='The date id of the file.')
    statistics: dict[str, int | float] = Field(description='The statistics for the ETL process.')
    file_name: str = Field(description='The name of the file.')

    class Config:
        """Pydantic model configuration."""

        orm_mode = True
