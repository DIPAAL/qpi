"""
API router.

Collects all routers from submodules into a single router for easier import in api_main.
"""
from fastapi import APIRouter
from app.routers.v1 import basic_sql, health
from app.routers.v1.audit_log import audit_log
from app.routers.v1.heatmap import heatmap
from app.routers.v1.cell import cell

# Routers for different versions of the API can be added here
# Remember to add the proper prefix and tags to the router
router_v1 = APIRouter(prefix="/api/v1")
router_v1.include_router(basic_sql.router, prefix="/table", tags=["basic_sql"])
router_v1.include_router(health.router, prefix="/health", tags=["health"])
router_v1.include_router(heatmap.router, prefix="/heatmap", tags=["heatmap"])
router_v1.include_router(cell.router, prefix='/cells', tags=['cell'])
router_v1.include_router(audit_log.router, prefix="/audit_log", tags=["audit_log"])

# The main router for the API app. This router is imported in api_main
router_main = APIRouter()
router_main.include_router(router_v1)
