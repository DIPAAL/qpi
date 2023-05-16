"""Endpoint controller for querying audit logs."""

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_dw
from app.schemas.audit_log import AuditLog, AuditLogResponse

router = APIRouter()


@router.get("", response_model=list[AuditLogResponse])
async def get_audit_logs(
        limit: int = Query(default=100, description="Limits the number of results returned in the collection to N."),
        offset: int = Query(default=0, description="Exclude the first N results of the collection."),
        dw=Depends(get_dw)):
    """Get all audit logs."""
    return dw.query(AuditLog).limit(limit).offset(offset).all()


@router.get("/{date_id}", response_model=list[AuditLogResponse])
async def get_audit_logs_by_date_id(date_id: int, dw=Depends(get_dw)):
    """Get audit logs for a given date id."""
    return dw.query(AuditLog).filter(AuditLog.date_id == date_id).all()
