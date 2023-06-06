SELECT ft.trajectory_sub_id,
       timestamp_from_date_time_id(ft.start_date_id, ft.start_time_id) as start_timestamp,
       timestamp_from_date_time_id(ft.end_date_id, ft.end_time_id) as end_timestamp,
       (
        CASE WHEN ft.eta_date_id = -1 THEN NULL
            ELSE timestamp_from_date_time_id(ft.eta_date_id, ft.eta_time_id)
        END
       ) as eta_timestamp,
       asMFJSON(atstbox(dt.trajectory, stbox({BOUNDS})))::json as trajectory,
       asMFJSON(attime(dt.rot, tstzspan :crop_span))::json as rot,
       asMFJSON(attime(dt.heading, tstzspan :crop_span))::json as heading,
       asMFJSON(attime(dt.draught, tstzspan :crop_span))::json as draught,
       dt.destination,
       ft.duration,
       ft.length,
       ft.infer_stopped as stopped,
       dns.nav_status as navigational_status,
       JSON_BUILD_OBJECT(
           'ship_id', ds.ship_id,
           'name', ds.name,
           'callsign', ds.callsign,
           'mmsi', ds.mmsi,
           'imo', ds.imo,
           'flag_region', ds.flag_region,
           'flag_state', ds.flag_state,
           'mobile_type', dst.mobile_type,
           'ship_type', dst.ship_type,
           'location_system_type', ds.location_system_type,
           'a', ds.a,
           'b', ds.b,
           'c', ds.c,
           'd', ds.d,
           'length', ds.length,
           'width', ds.width
       ) as ship
FROM fact_trajectory as ft
JOIN dim_trajectory as dt ON ft.trajectory_sub_id = dt.trajectory_sub_id AND ft.start_date_id = dt.date_id
JOIN dim_nav_status as dns ON ft.nav_status_id = dns.nav_status_id
JOIN dim_ship as ds ON ft.ship_id = ds.ship_id
JOIN dim_ship_type as dst ON ds.ship_type_id = dst.ship_type_id