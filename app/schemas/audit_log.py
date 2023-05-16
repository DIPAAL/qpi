"""Models for audit logs."""

from sqlalchemy import Column, DateTime, Integer, String, ARRAY
from sqlalchemy.dialects.postgresql import JSON

from app.datawarehouse import Base
from pydantic import BaseModel
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

    file_size: int = 139919
    total_delta_time: int = 27
    etl_version: str = "9001"
    requirements: list[str] = [
        "psycopg2-binary==2.9.5",
        "pytest==7.2.2",
        "pytest-cov==4.0.0",
        "pytest-dotenv==0.5.2",
        "dask==2023.3.1",
        "dask-geopandas==0.3.0",
        "geopandas==0.12.2",
        "fiona==1.9.1",
        "pandas==2.0.0",
        "Rtree==1.0.1",
        "Shapely==2.0.1",
        "SQLAlchemy==2.0.6",
        "git+https://github.com/DIPAAL/MobilityDB-python.git#1.3",
        "requests==2.28.2",
        "beautifulsoup4==4.11.2",
        "clint==0.5.1",
        "wget==3.2",
        "patool==1.12",
        "flake8==6.0.0",
        "flake8-docstrings==1.7.0",
        "tqdm==4.65.0"
    ]
    audit_id: int = 1
    import_datetime: datetime = datetime(2023, 5, 12, 13, 51, 6, 656838)
    date_id: int = 20220101
    statistics: dict = {
        "rows": {
            "file": 1000,
            "dim_ship": 2,
            "spatial_join": 26,
            "dim_ship_type": 2,
            "traj_split_5k": 2,
            "dim_nav_status": 1,
            "dim_trajectory": 2,
            "fact_trajectory": 2,
            "points_after_clean": 26,
            "trajectories_built": 2,
            "dim_cell_5000m_lazy": 2,
            "fact_cell_5000m_rollup": 2,
            "heatmap_time_5000m_aggregation": 2,
            "heatmap_count_5000m_aggregation": 2,
            "heatmap_delta_cog_5000m_aggregation": 2,
            "heatmap_max_draught_5000m_aggregation": 2,
            "heatmap_delta_heading_5000m_aggregation": 2
        },
        "timings": {
            "cleaning": 5.42077953700209,
            "trajectory": 2.824563745991327,
            "bulk_insert": 10.929611864994513,
            "spatial_join": 0.03560235499753617,
            "traj_split_5k": 1.0057452890032437,
            "cell_construct": 7.836577715992462,
            "dim_cell_5000m_lazy": 0.42491554700245615,
            "bulk_inserter_dim_ship": 0.04015656400588341,
            "fact_cell_5000m_rollup": 2.7678619299986167,
            "bulk_inserter_dim_ship_type": 0.041111760001513176,
            "bulk_inserter_dim_nav_status": 0.016528349995496683,
            "bulk_inserter_dim_trajectory": 0.011915631010197103,
            "bulk_inserter_fact_trajectory": 0.010036808002041653,
            "heatmap_time_5000m_aggregation": 0.318993214998045,
            "heatmap_count_5000m_aggregation": 1.3425339999957941,
            "heatmap_delta_cog_5000m_aggregation": 0.32054712501121685,
            "heatmap_max_draught_5000m_aggregation": 0.33882967999670655,
            "heatmap_delta_heading_5000m_aggregation": 0.3752087320026476
        }
    }
    file_name: str = "aisdk-sampleSmall-2022.csv"

    class Config:
        """Pydantic model configuration."""

        orm_mode = True
