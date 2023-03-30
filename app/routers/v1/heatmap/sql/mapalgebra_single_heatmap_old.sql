WITH reference (rast, geom) AS (
    SELECT ST_AddBand(
        ST_MakeEmptyRaster (:width, :height, :min_x, :min_y, :spatial_resolution, :spatial_resolution, 0, 0, 3034),
        '32BSI'::text,
        1,
        0
    ) AS rast,
    ST_MakeEnvelope(:min_x, :min_y, :max_x, :max_y, 3034) AS geom
)
SELECT
    CASE WHEN q3.rast IS NULL THEN NULL ELSE
        ST_AsGDALRaster(q3.rast,'GTiff')
    END AS raster
FROM (
    SELECT ST_MapAlgebra(q2.rast, reference.rast, '[rast1.val]+[rast2.val]', extenttype := 'SECOND') AS rast
    FROM reference, (
        SELECT ST_Union(r1.rast) AS rast FROM (
            SELECT ST_MapAlgebra(ST_MakeEmptyRaster(ST_Union(q1.second)), ST_Union(q1.second), :map_algebra_expr, pixeltype := '32BSI', nodata1expr := '0', nodata2expr := '0', nodatanodataval := '0') AS rast
            FROM (
                SELECT fch.partition_id,
                    ST_Union(
                        (SELECT fch.rast WHERE
                            timestamp_from_date_time_id(fch.date_id, fch.time_id) <= :first_end_timestamp
                            AND timestamp_from_date_time_id(fch.date_id, fch.time_id) >= :first_start_timestamp
                            AND dst.ship_type = ANY (:first_ship_types)
                            AND dst.mobile_type = ANY (:first_mobile_types)
                            AND fch.date_id BETWEEN :first_start_date_id AND :first_end_date_id
                        ),
                        'SUM'
                    ) AS first,
                    ST_Union(
                        (SELECT fch.rast WHERE
                            timestamp_from_date_time_id(fch.date_id, fch.time_id) <= :second_end_timestamp
                            AND timestamp_from_date_time_id(fch.date_id, fch.time_id) >= :second_start_timestamp
                            AND dst.ship_type = ANY (:second_ship_types)
                            AND dst.mobile_type = ANY (:second_mobile_types)
                            AND fch.date_id BETWEEN :second_start_date_id AND :second_end_date_id
                        ),
                        'SUM'
                    ) AS second
                FROM fact_cell_heatmap fch
                JOIN dim_ship_type dst on fch.ship_type_id = dst.ship_type_id
                WHERE fch.spatial_resolution = :spatial_resolution
                AND fch.heatmap_type_id = (SELECT heatmap_type_id FROM dim_heatmap_type WHERE slug = :heatmap_type_slug)
                AND fch.cell_x >= :min_cell_x
                AND fch.cell_x < :max_cell_x
                AND fch.cell_y >= :min_cell_y
                AND fch.cell_y < :max_cell_y
                GROUP BY fch.partition_id
            ) q1
            GROUP BY q1.partition_id
        ) r1
    ) q2
)q3