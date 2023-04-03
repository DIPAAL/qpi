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
    -- Create a title from the date by parsing it into a date object and then formatting it. Month of year and day of month should be zero padded.
    to_char(to_timestamp(q3.year::text   || '-' || lpad(q3.month_of_year::text, 2, '0') || '-' || lpad(q3.day_of_month::text, 2, '0'), 'YYYY-MM-DD'), 'DD/MM/YYYY') AS title,
    CASE WHEN q3.rast IS NULL THEN NULL ELSE
        ST_AsGDALRaster(q3.rast,'GTiff')
    END AS raster,
    (ST_SummaryStats(q3.rast)).max AS max
FROM (
    SELECT
        q2.year,
        q2.month_of_year,
        q2.day_of_month,
        ST_MapAlgebra(q2.rast, reference.rast, '[rast1.val]+[rast2.val]', extenttype := 'SECOND') AS rast
    FROM reference, (
        SELECT
            q1.year,
            q1.month_of_year,
            q1.day_of_month,
            ST_Union(q1.rast) AS rast
        FROM (
            SELECT
                dd.year,
                dd.month_of_year,
                dd.day_of_month,
                ST_Union(fch.rast, 'SUM') AS rast
            FROM fact_cell_heatmap fch
            JOIN dim_ship_type dst on fch.ship_type_id = dst.ship_type_id
            JOIN dim_date dd on fch.date_id = dd.date_id
            WHERE fch.spatial_resolution = :spatial_resolution
            AND fch.heatmap_type_id = (SELECT heatmap_type_id FROM dim_heatmap_type WHERE slug = :heatmap_type_slug)
            AND timestamp_from_date_time_id(fch.date_id, fch.time_id) <= :end_timestamp
            AND timestamp_from_date_time_id(fch.date_id, fch.time_id) >= :start_timestamp
            AND dst.ship_type = ANY (:ship_types)
            AND dst.mobile_type = ANY (:mobile_types)
            AND fch.cell_x >= :min_cell_x
            AND fch.cell_x < :max_cell_x
            AND fch.cell_y >= :min_cell_y
            AND fch.cell_y < :max_cell_y
            AND fch.date_id BETWEEN :start_date_id AND :end_date_id
            GROUP BY fch.partition_id, dd.year, dd.month_of_year, dd.day_of_month
        ) q1
        GROUP BY q1.year, q1.month_of_year, q1.day_of_month
    ) q2
)q3
ORDER BY q3.year, q3.month_of_year, q3.day_of_month ASC;