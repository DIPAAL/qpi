SELECT
    fc.cell_x AS x,
    fc.cell_y AS y,
    fc.trajectory_sub_id,
    timestamp_from_date_time_id(fc.entry_date_id, fc.entry_time_id) AS entry_timestamp,
    timestamp_from_date_time_id(fc.exit_date_id, fc.exit_time_id) AS exit_timestamp,
    fc.nav_status_id AS navigational_status,
    dd."from" AS begin,
    dd."to" AS end,
    fc.sog,
    fc.delta_cog,
    fc.delta_heading,
    fc.draught,
    fc.infer_stopped AS stopped,
    ds.mmsi,
    ds.imo,
    ds.name,
    dst.ship_type,
    dst.mobile_type,
    ds.flag_state
FROM fact_cell_5000m fc
INNER JOIN dim_cell_5000m dc ON fc.cell_x = dc.x AND fc.cell_y = dc.y AND fc.partition_id = dc.partition_id
INNER JOIN dim_ship ds on fc.ship_id = ds.ship_id
INNER JOIN dim_direction dd on fc.direction_id = dd.direction_id
INNER JOIN dim_ship_type dst on ds.ship_type_id = dst.ship_type_id
WHERE ST_Intersects(dc.geom, st_makeenvelope(:xmin, :ymin, :xmax, :ymax, :srid))
  AND fc.infer_stopped = ANY(:stopped)
  AND timestamp_from_date_time_id(fc.entry_date_id, fc.entry_time_id) < :upper_timestamp
  AND timestamp_from_date_time_id(fc.entry_date_id, fc.entry_time_id) > :lower_timestamp
LIMIT :limit
OFFSET :offset
;