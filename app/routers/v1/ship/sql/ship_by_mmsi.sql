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
FROM dim_ship ds
    JOIN dim_ship_type dst ON ds.ship_type_id = dst.ship_type_id
WHERE ds.mmsi = :mmsi;
