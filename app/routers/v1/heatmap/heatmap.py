"""Router for all endpoints related to heatmaps."""
import datetime
import os

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import PlainTextResponse

from app.dependencies import get_dw_cursor
from pydash.objects import merge

from app.routers.v1.heatmap.heatmap_renders import geo_tiff_to_png
from app.routers.v1.heatmap.models.heatmap_type import HeatmapType
from app.routers.v1.heatmap.models.mobile_type import MobileType
from app.routers.v1.heatmap.models.ship_type import ShipType
from app.routers.v1.heatmap.models.single_output_formats import SingleOutputFormat
from app.routers.v1.heatmap.models.spatial_resolution import SpatialResolution
from app.routers.v1.heatmap.models.temporal_resolution import TemporalResolution

router = APIRouter()
current_file_path = os.path.dirname(os.path.abspath(__file__))

temporal_resolution_names = {
    86400: "daily",
    3600: "hourly",
}


@router.get("")
def metadata(dw_cursor=Depends(get_dw_cursor)):
    """Return the available heatmaps."""
    with open(os.path.join(current_file_path, "sql/available_heatmaps.sql"), "r") as f:
        query = f.read()

    dw_cursor.execute(query)

    result = dw_cursor.fetchall()

    heatmap_types = {}

    for row in result:
        row_object = {
            row['slug']: {
                "name": row['name'],
                "description": row['description'],
                "spatial_resolutions": {
                    f"{row['spatial_resolution']}m": {
                        "resolution": row['spatial_resolution'],
                        "units": "meters",
                        "temporal_resolutions": {
                            temporal_resolution_names.get(
                                row['temporal_resolution_sec'],
                                f"{row['temporal_resolution_sec']}s"
                            ): {
                                "resolution": row['temporal_resolution_sec'],
                                "units": "seconds",
                                "temporal_domain": {
                                    "start": row['min_date'],
                                    "end": row['max_date']
                                }
                            }
                        }
                    }
                }
            }
        }
        # merge the object into the heatmap_types dict using pydash
        heatmap_types = merge(heatmap_types, row_object)

    return heatmap_types


@router.get("/single/{heatmap_type}/{spatial_resolution}", response_class=PlainTextResponse)
def single_heatmap(
        spatial_resolution: SpatialResolution,
        mobile_types: list[MobileType] = Query(default=[MobileType.class_a, MobileType.class_b]),
        ship_types: list[ShipType] = Query(default=[ShipType.cargo, ShipType.passenger]),
        output_format: SingleOutputFormat = Query(default=SingleOutputFormat.tiff),
        min_x: int = Query(default=3600000),
        min_y: int = Query(default=3030000),
        max_x: int = Query(default=4395000),
        max_y: int = Query(default=3485000),
        srid: int = Query(default=3034),
        start: datetime.datetime = Query(default="2022-01-01T00:00:00Z"),
        end: datetime.datetime = Query(default="2022-02-01T00:00:00Z"),
        heatmap_type: HeatmapType = HeatmapType.count,
        dw_cursor=Depends(get_dw_cursor)):
    """Return a single heatmap."""
    if srid != 3034:
        raise HTTPException("Only SRID 3034 is supported.")

    with open(os.path.join(current_file_path, "sql/single_heatmap.sql"), "r") as f:
        query = f.read()

    spatial_resolution = int(spatial_resolution)

    # extend spatial bounds to fit the spatial resolution
    min_x = min_x - (min_x % spatial_resolution)
    min_y = min_y - (min_y % spatial_resolution)
    max_x = max_x + (spatial_resolution - (max_x % spatial_resolution))
    max_y = max_y + (spatial_resolution - (max_y % spatial_resolution))

    # get size of the output raster
    width = int((max_x - min_x) / int(spatial_resolution))
    height = int((max_y - min_y) / int(spatial_resolution))

    start_date_id = int(start.strftime("%Y%m%d"))
    end_date_id = int(end.strftime("%Y%m%d"))

    dw_cursor.execute(query, {
        'width': width,
        'height': height,
        'min_x': min_x,
        'min_y': min_y,
        'max_x': max_x,
        'max_y': max_y,
        'spatial_resolution': int(spatial_resolution),
        'heatmap_type_slug': heatmap_type,
        'mobile_types': mobile_types,
        'ship_types': ship_types,
        'start_date_id': start_date_id,
        'end_date_id': end_date_id,
        'start_timestamp': start,
        'end_timestamp': end,
    })

    result = dw_cursor.fetchone()

    if result is None:
        raise HTTPException(status_code=404, detail="No heatmap data found given the parameters")

    # print the type of raster.tobytes() to see if it is bytes or str
    print(type(result['raster'].tobytes()))

    if output_format == SingleOutputFormat.png:
        return PlainTextResponse(geo_tiff_to_png(result['raster'].tobytes()).read(), media_type="image/png")

    return PlainTextResponse(result['raster'].tobytes(), media_type="image/tiff")


@router.post("mapalgebra/{type}/{spatial_resolution}/{temporal_resolution}")
def mapalgebra_heatmap(
        heatmap_type: HeatmapType,
        spatial_resolution: SpatialResolution,
        temporal_resolution: TemporalResolution,
        # dw_cursor=Depends(get_dw_cursor)
):
    """Return a single mapalgebra heatmap."""
    raise NotImplementedError(f"Mapalgebra heatmap for {heatmap_type} is not implemented yet. "
                              f"(spatial_resolution={spatial_resolution}, temporal_resolution={temporal_resolution})")


@router.post("multi/{type}/{spatial_resolution}/{temporal_resolution}")
def multi_heatmap(
        heatmap_type: HeatmapType,
        spatial_resolution: SpatialResolution,
        temporal_resolution: TemporalResolution,
        # dw_cursor=Depends(get_dw_cursor)
):
    """Return a multi heatmap."""
    raise NotImplementedError(f"Multi heatmap for {heatmap_type} is not implemented yet."
                              f" (spatial_resolution={spatial_resolution}, temporal_resolution={temporal_resolution})")
