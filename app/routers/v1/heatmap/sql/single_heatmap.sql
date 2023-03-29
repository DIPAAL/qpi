WITH reference (rast, geom) AS (
    SELECT ST_AddBand(
        ST_MakeEmptyRaster (:width, :height, :min_x, :min_y, :spatial_resolution, :spatial_resolution, 0, 0, 3034),
        '32BUI'::text,
        1,
        0
    ) AS rast,
    ST_MakeEnvelope(:min_x, :min_y, :max_x, :max_y, 3034) AS geom
)
 SELECT
    ST_AsGDALRaster(
        ST_MapAlgebra(ST_Union(q1.rast, 'SUM'), reference.rast, '[rast1.val]+[rast2.val]', extenttype:='UNION'),
        'GTiff'
    ) AS raster
FROM reference, (
    SELECT
        ST_Union(fch.rast, 'SUM') AS rast
    FROM reference, fact_cell_heatmap fch
    JOIN dim_ship_type dst on fch.ship_type_id = dst.ship_type_id
    WHERE fch.spatial_resolution = :spatial_resolution
        AND fch.heatmap_type_id = (SELECT heatmap_type_id FROM dim_heatmap_type WHERE slug = :heatmap_type_slug)
        AND timestamp_from_date_time_id(fch.date_id, fch.time_id) <= :end_timestamp
        AND timestamp_from_date_time_id(fch.date_id, fch.time_id) >= :start_timestamp
        AND dst.ship_type = ANY(:ship_types)
        AND dst.mobile_type = ANY(:mobile_types)
        AND fch.cell_x >= :min_cell_x
        AND fch.cell_x <= :max_cell_x
        AND fch.cell_y >= :min_cell_y
        AND fch.cell_y <= :max_cell_y
        AND fch.date_id BETWEEN :start_date_id AND :end_date_id
    GROUP BY fch.partition_id
    ) q1
GROUP BY reference.rast