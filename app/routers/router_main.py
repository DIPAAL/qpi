"""
API router.

Collects all routers from submodules into a single router for easier import in api_main.
"""
from fastapi import APIRouter
from app.routers.v1 import basic_sql, raster
import app.routers.v1.ship.router as ship

# Routers for different versions of the API can be added here
# Remember to add the proper prefix and tags to the router
router_v1 = APIRouter(prefix="/api/v1")
router_v1.include_router(basic_sql.router, prefix="/table", tags=["basic_sql"])
router_v1.include_router(raster.router, prefix="/raster", tags=["raster"])
router_v1.include_router(ship.router, prefix="/ships", tags=["ship"])

# The main router for the API app. This router is imported in api_main
router_main = APIRouter()
router_main.include_router(router_v1)
