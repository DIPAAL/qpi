"""Endpoint controller for querying audit logs."""

from fastapi import APIRouter, Depends

from app.dependencies import get_dw
from app.schemas.audit_log import AuditLog

router = APIRouter()


@router.get("")
async def get_audit_logs(limit: int = 100, offset: int = 0, dw=Depends(get_dw)):
    """Get all audit logs."""
    return dw.query(AuditLog).limit(limit).offset(offset).all()


@router.get("/{date_id}")
async def get_audit_logs_by_date_id(date_id: int, dw=Depends(get_dw)):
    """Get audit logs for a given date."""
    return dw.query(AuditLog).filter(AuditLog.date_id == date_id).all()
