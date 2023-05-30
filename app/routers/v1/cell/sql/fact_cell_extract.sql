SELECT
    fc.cell_x AS x,
    fc.cell_y AS y,
    fc.trajectory_sub_id,
    timestamp_from_date_time_id(fc.entry_date_id, fc.entry_time_id) AS entry_timestamp,
    timestamp_from_date_time_id(fc.exit_date_id, fc.exit_time_id) AS exit_timestamp,
    dns.nav_status AS navigational_status,
    dd."from" AS begin,
    dd."to" AS end,
    fc.sog,
    fc.delta_cog,
    fc.delta_heading,
    fc.draught,
    fc.infer_stopped AS stopped,
    ds.*,
    dst.ship_type,
    dst.mobile_type
FROM fact_cell_{CELL_SIZE}m fc
INNER JOIN dim_cell_{CELL_SIZE}m dc ON fc.cell_x = dc.x AND fc.cell_y = dc.y AND fc.partition_id = dc.partition_id
INNER JOIN dim_ship ds ON fc.ship_id = ds.ship_id
INNER JOIN dim_direction dd ON fc.direction_id = dd.direction_id
INNER JOIN dim_ship_type dst ON ds.ship_type_id = dst.ship_type_id
INNER JOIN dim_nav_status dns ON fc.nav_status_id = dns.nav_status_id
WHERE ST_Intersects(dc.geom, ST_Transform(st_makeenvelope(:xmin, :ymin, :xmax, :ymax, :srid), 3034))
  AND fc.infer_stopped = ANY(:stopped)
  AND fc.entry_date_id BETWEN :start_date_id AND :end_date_id
  AND timestamp_from_date_time_id(fc.entry_date_id, fc.entry_time_id) <= :end_timestamp
  AND timestamp_from_date_time_id(fc.entry_date_id, fc.entry_time_id) >= :start_timestamp
LIMIT :limit
OFFSET :offset
;