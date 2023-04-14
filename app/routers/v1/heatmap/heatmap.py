"""Router for all endpoints related to heatmaps."""
import io

import datetime
import os

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy import text
import pandas as pd
from sqlalchemy.orm import Session

from app.dependencies import get_dw
from pydash.objects import merge

from app.routers.v1.heatmap.heatmap_renders import geo_tiff_to_png, geo_tiffs_to_video
from app.schemas.heatmap_type import HeatmapType
from app.schemas.mobile_type import MobileType
from app.schemas.ship_type import ShipType
from app.schemas.single_output_formats import SingleOutputFormat
from app.schemas.spatial_resolution import SpatialResolution
from app.schemas.temporal_resolution import TemporalResolution
from app.schemas.enc_enum import EncCell
from app.schemas.multi_output_format import MultiOutputFormat
from helper_functions import measure_time

router = APIRouter()
current_file_path = os.path.dirname(os.path.abspath(__file__))

temporal_resolution_names = {
    86400: "daily",
    3600: "hourly",
}


@router.get("")
def metadata(db: Session = Depends(get_dw)):
    """Return the available heatmaps."""
    with open(os.path.join(current_file_path, "sql/available_heatmaps.sql"), "r") as f:
        query = f.read()

    df = pd.read_sql(text(query), db.bind.connect())

    heatmap_types = {}

    for row in df.to_dict(orient="records"):
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
        ship_types: list[ShipType] = Query(default=[ship_type for ship_type in ShipType]),
        output_format: SingleOutputFormat = Query(default=SingleOutputFormat.tiff),
        min_x: int = Query(default=3600000),
        min_y: int = Query(default=3030000),
        max_x: int = Query(default=4395000),
        max_y: int = Query(default=3485000),
        srid: int = Query(default=3034),
        enc_cell: EncCell = Query(default=None),
        start: datetime.datetime = Query(default="2022-01-01T00:00:00Z"),
        end: datetime.datetime = Query(default="2022-02-01T00:00:00Z"),
        heatmap_type: HeatmapType = HeatmapType.count,
        dw=Depends(get_dw)):
    """Return a single heatmap."""
    if srid != 3034:
        raise HTTPException(501, "Only SRID 3034 is supported.")

    with open(os.path.join(current_file_path, "sql/single_heatmap.sql"), "r") as f:
        query = f.read()

    spatial_resolution, min_x, min_y, max_x, max_y, width, height = \
        get_spatial_resolution_and_bounds(dw, spatial_resolution, min_x, min_y, max_x, max_y, enc_cell)

    start_date_id = int(start.strftime("%Y%m%d"))
    end_date_id = int(end.strftime("%Y%m%d"))

    params = {
        'width': width,
        'height': height,
        'min_x': min_x,
        'min_y': min_y,
        'max_x': max_x,
        'max_y': max_y,
        'min_cell_x': int(min_x / 5000),
        'min_cell_y': int(min_y / 5000),
        'max_cell_x': int(max_x / 5000),
        'max_cell_y': int(max_y / 5000),
        'spatial_resolution': int(spatial_resolution),
        'heatmap_type_slug': heatmap_type,
        'mobile_types': mobile_types,
        'ship_types': ship_types,
        'start_date_id': start_date_id,
        'end_date_id': end_date_id,
        'start_timestamp': start,
        'end_timestamp': end,
    }

    result, query_time_taken_sec = measure_time(lambda: dw.execute(text(query), params).fetchone())

    if result is None or result[0] is None:
        raise HTTPException(404, "No heatmap data found given the parameters.")

    if output_format == SingleOutputFormat.png:
        png, image_time_taken_sec = try_get_png_from_geotiff(
            result[0].tobytes(),
            title=f"{heatmap_type.value} {start.strftime('%Y-%m-%d')} - {end.strftime('%Y-%m-%d')}"
        )
        return PlainTextResponse(png, media_type="image/png",
                                 headers={
                                     'Query-Time': str(query_time_taken_sec),
                                     'Image-Time': str(image_time_taken_sec)
                                 })

    return PlainTextResponse(result[0].tobytes(), media_type="image/tiff",
                             headers={'Query-Time': str(query_time_taken_sec)}
                             )


def try_get_png_from_geotiff(geo_tiff_bytes: io.BytesIO, can_be_negative: bool = False, title: str = None):
    """
    Measure time of converting geotiff to png, and reraise the ValueError as HTTPException.

    Keyword arguments:
        geo_tiff_bytes: binary representation of geotiff
        can_be_negative: whether the geotiff can be negative, i.e. whether a colormap should support negative values.
    """
    try:
        png, image_time_taken_sec = \
            measure_time(lambda: geo_tiff_to_png(geo_tiff_bytes, can_be_negative=can_be_negative, title=title).read())
    except ValueError as e:
        if "vmin == vmax" in str(e):
            raise HTTPException(404, "No heatmap data found given the parameters.")
        raise e
    return png, image_time_taken_sec


def get_enc_cell_min_max(db: Session, enc_cell: EncCell, min_x, min_y, max_x, max_y) -> tuple[int, int, int, int]:
    """Replace min and maxes with enc values if enc_cell is not None."""
    if enc_cell is None:
        return min_x, min_y, max_x, max_y
    # replace min_x, min_y, max_x, max_y with the values from the enc_cell
    enc_cell_result = db.execute(text("""
            SELECT
                ST_XMin(geom) AS min_x,
                ST_YMin(geom) AS min_y,
                ST_XMax(geom) AS max_x,
                ST_YMax(geom) AS max_y
            FROM reference_geometries WHERE name = :name AND type = 'enc';
        """), {"name": enc_cell.value}).fetchone()
    return enc_cell_result.min_x, enc_cell_result.min_y, enc_cell_result.max_x, enc_cell_result.max_y


def get_spatial_resolution_and_bounds(dw, spatial_resolution, min_x, min_y, max_x, max_y, enc_cell)\
        -> tuple[int, int, int, int, int, int, int]:
    """
    Based on query inputs, find bounds and spatial resolution of the output raster.

    Keyword arguments:
        dw: database connection
        spatial_resolution: spatial resolution of the output raster
        min_x: minimum x coordinate of the output raster
        min_y: minimum y coordinate of the output raster
        max_x: maximum x coordinate of the output raster
        max_y: maximum y coordinate of the output raster
        enc_cell: ENC cell name (optional)
    """
    spatial_resolution = int(spatial_resolution)

    min_x, min_y, max_x, max_y = get_enc_cell_min_max(dw, enc_cell, min_x, min_y, max_x, max_y)

    # extend spatial bounds to fit the spatial resolution
    min_x = int(min_x - (min_x % spatial_resolution))
    min_y = int(min_y - (min_y % spatial_resolution))
    max_x = int(max_x + (spatial_resolution - (max_x % spatial_resolution)))
    max_y = int(max_y + (spatial_resolution - (max_y % spatial_resolution)))

    # get size of the output raster
    width = int((max_x - min_x) / int(spatial_resolution))
    height = int((max_y - min_y) / int(spatial_resolution))

    # if more than 2 megapixels, ask the user to adjust resolution or bounds
    if width * height > 2000000:
        raise HTTPException(400, "The requested raster contains more than 2 megapixels."
                                 " Please adjust the resolution or bounds.")

    return spatial_resolution, min_x, min_y, max_x, max_y, width, height


@router.get("/mapalgebra/{heatmap_type}/{spatial_resolution}")
def mapalgebra_heatmap(
        heatmap_type: HeatmapType = HeatmapType.count,
        spatial_resolution: SpatialResolution = SpatialResolution.five_kilometers,
        output_format: SingleOutputFormat = Query(default=SingleOutputFormat.tiff),
        map_algebra_expr: str = Query(default="[rast1.val]-[rast2.val]"),
        map_algebra_no_data_1_expr: str = Query(default="[rast2.val]"),
        map_algebra_no_data_2_expr: str = Query(default="-[rast1.val]"),
        min_x: int = Query(default=3600000),
        min_y: int = Query(default=3030000),
        max_x: int = Query(default=4395000),
        max_y: int = Query(default=3485000),
        srid: int = Query(default=3034),
        enc_cell: EncCell = Query(default=None),
        first_mobile_types: list[MobileType] = Query(default=[MobileType.class_a, MobileType.class_b]),
        first_ship_types: list[ShipType] = Query(default=[ShipType.cargo, ShipType.passenger]),
        first_start: datetime.datetime = Query(default="2021-01-01T00:00:00Z"),
        first_end: datetime.datetime = Query(default="2021-02-01T00:00:00Z"),
        second_mobile_types: list[MobileType] = Query(default=[MobileType.class_a, MobileType.class_b]),
        second_ship_types: list[ShipType] = Query(default=[ShipType.cargo, ShipType.passenger]),
        second_start: datetime.datetime = Query(default="2021-07-01T00:00:00Z"),
        second_end: datetime.datetime = Query(default="2021-08-01T00:00:00Z"),
        dw=Depends(get_dw)
):
    """Return a single mapalgebra heatmap."""
    if srid != 3034:
        raise HTTPException(501, "Only SRID 3034 is supported.")

    with open(os.path.join(current_file_path, "sql/mapalgebra_single_heatmap.sql"), "r") as f:
        query = f.read()

    spatial_resolution, min_x, min_y, max_x, max_y, width, height = \
        get_spatial_resolution_and_bounds(dw, spatial_resolution, min_x, min_y, max_x, max_y, enc_cell)

    first_start_date_id = int(first_start.strftime("%Y%m%d"))
    first_end_date_id = int(first_end.strftime("%Y%m%d"))
    second_start_date_id = int(second_start.strftime("%Y%m%d"))
    second_end_date_id = int(second_end.strftime("%Y%m%d"))

    params = {
        'width': width,
        'height': height,
        'min_x': min_x,
        'min_y': min_y,
        'max_x': max_x,
        'max_y': max_y,
        'min_cell_x': int(min_x / 5000),
        'min_cell_y': int(min_y / 5000),
        'max_cell_x': int(max_x / 5000),
        'max_cell_y': int(max_y / 5000),
        'spatial_resolution': int(spatial_resolution),
        'heatmap_type_slug': heatmap_type,
        'map_algebra_expr': map_algebra_expr,
        'map_algebra_no_data_1_expr': map_algebra_no_data_1_expr,
        'map_algebra_no_data_2_expr': map_algebra_no_data_2_expr,
        'first_mobile_types': first_mobile_types,
        'first_ship_types': first_ship_types,
        'first_start_date_id': first_start_date_id,
        'first_end_date_id': first_end_date_id,
        'first_start_timestamp': first_start,
        'first_end_timestamp': first_end,
        'second_mobile_types': second_mobile_types,
        'second_ship_types': second_ship_types,
        'second_start_date_id': second_start_date_id,
        'second_end_date_id': second_end_date_id,
        'second_start_timestamp': second_start,
        'second_end_timestamp': second_end,
    }

    result, query_time_taken_sec = measure_time(lambda: dw.execute(text(query), params).fetchone())

    if result is None or result[0] is None:
        raise HTTPException(404, "No heatmap data found given the parameters.")

    if output_format == SingleOutputFormat.png:
        png, image_time_taken_sec = try_get_png_from_geotiff(
            result[0].tobytes(),
            can_be_negative=True,
            title=f"{heatmap_type.value} - custom map algebra"
        )
        return PlainTextResponse(png, media_type="image/png",
                                 headers={
                                     'Query-Time': str(query_time_taken_sec),
                                     'Image-Time': str(image_time_taken_sec)
                                 })

    return PlainTextResponse(result[0].tobytes(), media_type="image/tiff",
                             headers={'Query-Time': str(query_time_taken_sec)}
                             )


@router.get("/multi/{heatmap_type}/{spatial_resolution}/{temporal_resolution}")
def multi_heatmap(
        heatmap_type: HeatmapType = HeatmapType.count,
        spatial_resolution: SpatialResolution = SpatialResolution.five_kilometers,
        temporal_resolution: TemporalResolution = TemporalResolution.daily,
        output_format: MultiOutputFormat = Query(default=MultiOutputFormat.mp4),
        fps: int = Query(default=10),
        min_x: int = Query(default=3600000),
        min_y: int = Query(default=3030000),
        max_x: int = Query(default=4395000),
        max_y: int = Query(default=3485000),
        srid: int = Query(default=3034),
        enc_cell: EncCell = Query(default=None),
        mobile_types: list[MobileType] = Query(default=[MobileType.class_a, MobileType.class_b]),
        ship_types: list[ShipType] = Query(default=[ShipType.cargo, ShipType.passenger]),
        start: datetime.datetime = Query(default="2021-01-01T00:00:00Z"),
        end: datetime.datetime = Query(default="2021-02-01T00:00:00Z"),
        dw=Depends(get_dw)
):
    """Return a multi heatmap."""
    if srid != 3034:
        raise HTTPException(501, "Only SRID 3034 is supported.")

    with open(os.path.join(current_file_path, f"sql/multi_heatmaps/{temporal_resolution.value}.sql"), "r") as f:
        query = f.read()

    spatial_resolution, min_x, min_y, max_x, max_y, width, height = \
        get_spatial_resolution_and_bounds(dw, spatial_resolution, min_x, min_y, max_x, max_y, enc_cell)

    start_date_id = int(start.strftime("%Y%m%d"))
    end_date_id = int(end.strftime("%Y%m%d"))

    params = {
        'width': width,
        'height': height,
        'min_x': min_x,
        'min_y': min_y,
        'max_x': max_x,
        'max_y': max_y,
        'min_cell_x': int(min_x / 5000),
        'min_cell_y': int(min_y / 5000),
        'max_cell_x': int(max_x / 5000),
        'max_cell_y': int(max_y / 5000),
        'spatial_resolution': int(spatial_resolution),
        'heatmap_type_slug': heatmap_type,
        'mobile_types': mobile_types,
        'ship_types': ship_types,
        'start_date_id': start_date_id,
        'end_date_id': end_date_id,
        'start_timestamp': start,
        'end_timestamp': end,
    }

    result, query_time_taken_sec = measure_time(lambda: dw.execute(text(query), params).fetchall())

    if result is None:
        raise HTTPException(404, "No heatmap data found given the parameters.")

    max_value = max([r[2] for r in result])

    result = [(r[0], r[1].tobytes()) for r in result]

    video, image_time_taken_sec = measure_time(
        lambda: geo_tiffs_to_video(result, fps, output_format.value, heatmap_type.value, max_value)
    )

    media_type = f"video/{output_format.value}"
    if output_format == MultiOutputFormat.gif:
        media_type = f"image/{output_format.value}"

    return PlainTextResponse(video.read(), media_type=media_type,
                             headers={
                                 'Query-Time': str(query_time_taken_sec),
                                 'Image-Time': str(image_time_taken_sec)
                             })
