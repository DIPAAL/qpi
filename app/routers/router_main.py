"""
API router.

Collects all routers from submodules.
"""
from fastapi import APIRouter
from .v1 import basic_sql, raster

# Routers for different versions of the API can be added here
router_v1 = APIRouter(prefix="/api/v1")
router_v1.include_router(basic_sql.router, prefix="/table", tags=["basic_sql"])
router_v1.include_router(raster.router, prefix="/raster", tags=["raster"])

# Create a router for the main API app
router_main = APIRouter()
router_main.include_router(router_v1)
