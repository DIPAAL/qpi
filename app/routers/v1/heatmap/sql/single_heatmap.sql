WITH reference (rast, geom) AS (
    SELECT ST_AddBand(
        ST_MakeEmptyRaster (%(width)s, %(height)s, %(min_x)s, %(min_y)s, %(spatial_resolution)s, %(spatial_resolution)s, 0, 0, 3034),
        '32BUI'::text,
        1,
        0
    ) AS rast,
    ST_MakeEnvelope(%(min_x)s, %(min_y)s, %(max_x)s, %(max_y)s, 3034) AS geom
)
 SELECT
    ST_AsGDALRaster(
        ST_MapAlgebra(ST_Union(q1.rast), reference.rast, '[rast1.val]+[rast2.val]', extenttype:='UNION'),
        'GTiff'
    ) AS raster
FROM reference, (
    SELECT
        ST_Union(fch.rast) AS rast
    FROM reference, fact_cell_heatmap fch
    JOIN dim_ship_type dst on fch.ship_type_id = dst.ship_type_id
    JOIN dim_cell_5000m dc on fch.cell_x = dc.x AND fch.cell_y = dc.y AND fch.partition_id = dc.partition_id
    WHERE fch.spatial_resolution = %(spatial_resolution)s
        AND fch.heatmap_type_id = (SELECT heatmap_type_id FROM dim_heatmap_type WHERE slug = %(heatmap_type_slug)s)
        AND timestamp_from_date_time_id(fch.date_id, fch.time_id) <= %(end_timestamp)s
        AND timestamp_from_date_time_id(fch.date_id, fch.time_id) >= %(start_timestamp)s
        AND dst.ship_type = ANY(%(ship_types)s)
        AND dst.mobile_type = ANY(%(mobile_types)s)
        AND dc.geom && reference.geom
    GROUP BY fch.partition_id
    ) q1
GROUP BY reference.rast