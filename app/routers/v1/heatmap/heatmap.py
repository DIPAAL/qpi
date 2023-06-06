"""Router for all endpoints related to heatmaps."""
import io

import datetime
import os

from fastapi import APIRouter, Depends, Query, HTTPException, Path
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
from app.schemas.heatmapmeta import HeatmapMetadata
from helper_functions import measure_time


router = APIRouter()
current_file_path = os.path.dirname(os.path.abspath(__file__))

temporal_resolution_names = {
    86400: "daily",
    3600: "hourly",
}


@router.get("", response_model=dict[str, HeatmapMetadata])
def metadata(db: Session = Depends(get_dw)):
    """Return all heatmaps that are available in the DW."""
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
        # Path parameters
        spatial_resolution: SpatialResolution = Path(description="The spatial resolution of the heatmap.",
                                                     example=SpatialResolution.five_kilometers),
        heatmap_type: HeatmapType = Path(description="The type of the heatmap.",
                                         example=HeatmapType.count),
        # Query parameters
        mobile_types: list[MobileType] = Query(default=[MobileType.class_a, MobileType.class_b],
                                               description="Limits what mobile type the ships must belong to."),
        ship_types: list[ShipType] = Query(default=[ship_type for ship_type in ShipType],
                                           description="Limits what ship type the ships must belong to."),
        output_format: SingleOutputFormat = Query(default=SingleOutputFormat.tiff,
                                                  description="The output format of the heatmap."),
        x_min: int = Query(default=3600000, description='Defines the "left side" of the bounding rectangle, '
                                                        'coordinates must match the provided "srid" parameter.'),
        y_min: int = Query(default=3030000, description='Defines the "bottom side" of the bounding rectangle, '
                                                        'coordinates must match the provided "srid" parameter.'),
        x_max: int = Query(default=4395000, description='Defines the "right side" of the bounding rectangle, '
                                                        'coordinates must match the provided "srid" parameter.'),
        y_max: int = Query(default=3485000, description='Defines the "top side" of the bounding rectangle, '
                                                        'coordinates must match the provided "srid" parameter.'),
        srid: int = Query(default=3034, description='The spatial reference system for the heatmap. '
                                                    'Currently only EPSG:3034 is supported.'),
        enc_cell: EncCell = Query(default=None,
                                  description='Limits the heatmaps spatial extent to the provided ENC cell. '
                                              'If provided, this parameter overrides any other spatial constraints.'),
        start: datetime.datetime = Query(default="2022-01-01T00:00:00Z",
                                         description='The inclusive start time, '
                                                     'defines the start of the temporal bound.'),
        end: datetime.datetime = Query(default="2022-02-01T00:00:00Z",
                                       description='The exclusive end time, '
                                                   'defines the end of the temporal bound.'),
        dw=Depends(get_dw)):
    """Return a single heatmap, based on the parameters provided."""
    if srid != 3034:
        raise HTTPException(501, "Only SRID 3034 is supported.")

    with open(os.path.join(current_file_path, "sql/single_heatmap.sql"), "r") as f:
        query = f.read()

    spatial_resolution, x_min, y_min, x_max, y_max, width, height = \
        get_spatial_resolution_and_bounds(dw, spatial_resolution, x_min, y_min, x_max, y_max, enc_cell)

    start_date_id = int(start.strftime("%Y%m%d"))
    end_date_id = int(end.strftime("%Y%m%d"))

    params = {
        'width': width,
        'height': height,
        'min_x': x_min,
        'min_y': y_min,
        'max_x': x_max,
        'max_y': y_max,
        'min_cell_x': int(x_min / 5000),
        'min_cell_y': int(y_min / 5000),
        'max_cell_x': int(x_max / 5000),
        'max_cell_y': int(y_max / 5000),
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


def try_get_png_from_geotiff(geo_tiff_bytes: io.BytesIO, can_be_negative: bool = False, title: str = None)\
        -> (io.BytesIO, float):
    """
    Measure time of converting geotiff to png, and reraise the ValueError as HTTPException.

    Keyword arguments:
        geo_tiff_bytes: binary representation of geotiff
        can_be_negative: whether the geotiff can be negative, i.e. whether a colormap should support negative values.
        title: title of the heatmap to be rendered
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

    # commit the transaction, as citus will tend to not create new connections to workers if not committed.
    db.commit()

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


@router.get("/mapalgebra/{heatmap_type}/{spatial_resolution}", response_class=PlainTextResponse)
def mapalgebra_heatmap(
        # Path parameters
        heatmap_type: HeatmapType = Path(description='The type of the heatmap.',
                                         example=HeatmapType.count),
        spatial_resolution: SpatialResolution = Path(description='The spatial resolution of the heatmap.',
                                                     example=SpatialResolution.five_kilometers),
        # Query parameters
        output_format: SingleOutputFormat = Query(default=SingleOutputFormat.tiff,
                                                  description='Output format of the heatmap.'),
        map_algebra_expr: str = Query(default="[rast1.val]-[rast2.val]",
                                      description='A PostgreSQL algebraic expression involving two rasters and '
                                                  'functions/operators that defines the pixel value when pixels '
                                                  'intersect.'),
        map_algebra_no_data_1_expr: str = Query(default="[rast2.val]",
                                                description='A PostgreSQL algebraic expression only involving the '
                                                            'second raster, that defines what to return when the first '
                                                            'raster has no data.'),
        map_algebra_no_data_2_expr: str = Query(default="-[rast1.val]",
                                                description='A PostgreSQL algebraic expression only involving the '
                                                            'first raster, that defines what to return when the second '
                                                            'raster has no data.'),
        x_min: int = Query(default=3600000,
                           description='Defines the "left side" of the bounding rectangle, '
                                       'coordinates must match the provided "srid" parameter.'),
        y_min: int = Query(default=3030000,
                           description='Defines the "bottom side" of the bounding rectangle, '
                                       'coordinates must match the provided "srid" parameter.'),
        x_max: int = Query(default=4395000,
                           description='Defines the "right side" of the bounding rectangle, '
                                       'coordinates must match the provided "srid" parameter.'),
        y_max: int = Query(default=3485000,
                           description='Defines the "top side" of the bounding rectangle, '
                                       'coordinates must match the provided "srid" parameter.'),
        srid: int = Query(default=3034,
                          description='The spatial reference system for the heatmap. '
                                      'Currently only EPSG:3034 is supported.'),
        enc_cell: EncCell = Query(default=None,
                                  description='Limits the heatmaps spatial extent to the provided ENC cell. '
                                              'If provided, this parameter overrides any other spatial constraints.'),
        first_mobile_types: list[MobileType] = Query(default=[MobileType.class_a, MobileType.class_b],
                                                     description='The mobile types to include in the first raster.'),
        first_ship_types: list[ShipType] = Query(default=[ShipType.cargo, ShipType.passenger],
                                                 description='The ship types to include in the first raster.'),
        first_start: datetime.datetime = Query(default="2021-01-01T00:00:00Z",
                                               description='The inclusive start of the temporal bound for the '
                                                           'first raster.'),
        first_end: datetime.datetime = Query(default="2021-02-01T00:00:00Z",
                                             description='The exclusive end of the temporal bound for the '
                                                         'first raster.'),
        second_mobile_types: list[MobileType] = Query(default=[MobileType.class_a, MobileType.class_b],
                                                      description='The mobile types to include in the second raster.'),
        second_ship_types: list[ShipType] = Query(default=[ShipType.cargo, ShipType.passenger],
                                                  description='The ship types to include in the second raster.'),
        second_start: datetime.datetime = Query(default="2021-07-01T00:00:00Z",
                                                description='The inclusive start of the temporal bound for the '
                                                            'second raster.'),
        second_end: datetime.datetime = Query(default="2021-08-01T00:00:00Z",
                                              description='The exclusive end of the temporal bound for the '
                                                          'second raster.'),
        dw=Depends(get_dw)
):
    """Return a single mapalgebra heatmap, based on the parameters provided."""
    if srid != 3034:
        raise HTTPException(501, "Only SRID 3034 is supported.")

    with open(os.path.join(current_file_path, "sql/mapalgebra_single_heatmap.sql"), "r") as f:
        query = f.read()

    spatial_resolution, x_min, y_min, x_max, y_max, width, height = \
        get_spatial_resolution_and_bounds(dw, spatial_resolution, x_min, y_min, x_max, y_max, enc_cell)

    first_start_date_id = int(first_start.strftime("%Y%m%d"))
    first_end_date_id = int(first_end.strftime("%Y%m%d"))
    second_start_date_id = int(second_start.strftime("%Y%m%d"))
    second_end_date_id = int(second_end.strftime("%Y%m%d"))

    params = {
        'width': width,
        'height': height,
        'min_x': x_min,
        'min_y': y_min,
        'max_x': x_max,
        'max_y': y_max,
        'min_cell_x': int(x_min / 5000),
        'min_cell_y': int(y_min / 5000),
        'max_cell_x': int(x_max / 5000),
        'max_cell_y': int(y_max / 5000),
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


@router.get("/multi/{heatmap_type}/{spatial_resolution}/{temporal_resolution}", response_class=PlainTextResponse)
def multi_heatmap(
        heatmap_type: HeatmapType = Path(description='The type of the heatmap.',
                                         example=HeatmapType.count),
        spatial_resolution: SpatialResolution = Path(description='The spatial resolution of the heatmap.',
                                                     example=SpatialResolution.five_kilometers),
        temporal_resolution: TemporalResolution = Path(description='The temporal resolution of the heatmap.',
                                                       example=TemporalResolution.daily),
        output_format: MultiOutputFormat = Query(default=MultiOutputFormat.mp4,
                                                 description='The output format of result.'),
        fps: int = Query(default=10,
                         description='The frames per second of the result. Only applicable for mp4 output format.'),
        x_min: int = Query(default=3600000,
                           description='Defines the "left side" of the bounding rectangle, '
                                       'coordinates must match the provided "srid" parameter.'),
        y_min: int = Query(default=3030000,
                           description='Defines the "bottom side" of the bounding rectangle, '
                                       'coordinates must match the provided "srid" parameter.'),
        x_max: int = Query(default=4395000,
                           description='Defines the "right side" of the bounding rectangle, '
                                       'coordinates must match the provided "srid" parameter.'),
        y_max: int = Query(default=3485000,
                           description='Defines the "top side" of the bounding rectangle, '
                                       'coordinates must match the provided "srid" parameter.'),
        srid: int = Query(default=3034,
                          description='The spatial reference system for the heatmap. '
                                      'Currently only EPSG:3034 is supported.'),
        enc_cell: EncCell = Query(default=None,
                                  description='Limits the heatmaps spatial extent to the provided ENC cell. '
                                              'If provided, this parameter overrides any other spatial constraints.'),
        mobile_types: list[MobileType] = Query(default=[MobileType.class_a, MobileType.class_b],
                                               description='Limits what mobile type the ships must belong to.'),
        ship_types: list[ShipType] = Query(default=[ShipType.cargo, ShipType.passenger],
                                           description='Limits what ship type the ships must belong to.'),
        start: datetime.datetime = Query(default="2021-01-01T00:00:00Z",
                                         description='The inclusive start time, '
                                                     'defines the start of the temporal bound.'),
        end: datetime.datetime = Query(default="2021-02-01T00:00:00Z",
                                       description='The exclusive end time, '
                                                   'defines the end of the temporal bound.'),
        dw=Depends(get_dw)
):
    """Return a multi heatmap, based on the parameters provided."""
    if srid != 3034:
        raise HTTPException(501, "Only SRID 3034 is supported.")

    with open(os.path.join(current_file_path, f"sql/multi_heatmaps/{temporal_resolution.value}.sql"), "r") as f:
        query = f.read()

    spatial_resolution, x_min, y_min, x_max, y_max, width, height = \
        get_spatial_resolution_and_bounds(dw, spatial_resolution, x_min, y_min, x_max, y_max, enc_cell)

    start_date_id = int(start.strftime("%Y%m%d"))
    end_date_id = int(end.strftime("%Y%m%d"))

    params = {
        'width': width,
        'height': height,
        'min_x': x_min,
        'min_y': y_min,
        'max_x': x_max,
        'max_y': y_max,
        'min_cell_x': int(x_min / 5000),
        'min_cell_y': int(y_min / 5000),
        'max_cell_x': int(x_max / 5000),
        'max_cell_y': int(y_max / 5000),
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

    if result is None or len(result) == 0:
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
