SELECT ds.ship_id,
       ds.name,
       ds.callsign,
       ds.mmsi,
       ds.imo,
       ds.mid,
       ds.flag_region,
       ds.flag_state,
       dst.mobile_type,
       dst.ship_type,
       ds.location_system_type,
       ds.a,
       ds.b,
       ds.c,
       ds.d
FROM fact_{CELL_SIZE} fc
    JOIN dim_ship ds ON fc.ship_id = ds.ship_id
    JOIN dim_ship_type dst ON ds.ship_type_id = dst.ship_type_id
    JOIN dim_{CELL_SIZE} dc ON fc.partition_id = dc.partition_id
WHERE
    fc.entry_date_id >= :from_date AND
    fc.exit_date_id <= :to_date  AND
    ST_CONTAINS(ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, 3034), dc.geom)
GROUP BY ds.ship_id, dst.mobile_type, dst.ship_type ORDER BY ds.ship_id LIMIT :limit OFFSET :offset;