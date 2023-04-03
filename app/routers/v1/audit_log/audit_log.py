"""Endpoint controller for querying audit logs."""

from fastapi import APIRouter, Depends

from app.dependencies import get_dw
from app.routers.v1.audit_log.model.audit_log import AuditLog

router = APIRouter()


@router.get("/{date_id}")
async def get_audit_logs(date_id: int, dw=Depends(get_dw)):
    """Get audit logs for a given date."""
    return dw.query(AuditLog).filter(AuditLog.date_id == date_id).all()
