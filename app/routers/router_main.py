"""
API router.

Collects all routers from submodules into a single router for easier import in api_main.
"""
from fastapi import APIRouter
from app.routers.v1 import basic_sql, health
from app.routers.v1.audit_log import audit_log
from app.routers.v1.heatmap import heatmap
from app.routers.v1.cell import cell
from app.routers.v1.trajectory import router as trajectory
from app.routers.v1.ship import router as ship

# Routers for different versions of the API can be added here
# Remember to add the proper prefix and tags to the router
router_v1 = APIRouter(prefix="/api/v1")
router_v1.include_router(heatmap.router, prefix="/heatmap", tags=["Heatmap"])
router_v1.include_router(trajectory.router, prefix="/trajectory", tags=["Trajectory"])
router_v1.include_router(ship.router, prefix="/ships", tags=["Ships"])
router_v1.include_router(cell.router, prefix='/cells', tags=['Cell'])
router_v1.include_router(health.router, prefix="/health", tags=["Miscellaneous"])
router_v1.include_router(basic_sql.router, prefix="/table", tags=["Miscellaneous"])
router_v1.include_router(audit_log.router, prefix="/audit_log", tags=["Miscellaneous"])

# The main router for the API app. This router is imported in api_main
router_main = APIRouter()
router_main.include_router(router_v1)
