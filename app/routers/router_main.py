"""
API router.

Collects all routers from submodules into a single router for easier import in api_main.
"""
from fastapi import APIRouter
<<<<<<< HEAD
from app.routers.v1 import basic_sql, raster
from app.routers.v1.ship.router import router as ship_router

=======
from app.routers.v1 import basic_sql, health
from app.routers.v1.heatmap import heatmap
>>>>>>> 380a392dc83593c6bbb612a251be6bdb609a5b73

# Routers for different versions of the API can be added here
# Remember to add the proper prefix and tags to the router
router_v1 = APIRouter(prefix="/api/v1")
router_v1.include_router(basic_sql.router, prefix="/table", tags=["basic_sql"])
<<<<<<< HEAD
router_v1.include_router(raster.router, prefix="/raster", tags=["raster"])
router_v1.include_router(ship_router, prefix="/ships", tags=["ships"])
=======
router_v1.include_router(health.router, prefix="/health", tags=["health"])
router_v1.include_router(heatmap.router, prefix="/heatmap", tags=["heatmap"])
>>>>>>> 380a392dc83593c6bbb612a251be6bdb609a5b73

# The main router for the API app. This router is imported in api_main
router_main = APIRouter()
router_main.include_router(router_v1)
