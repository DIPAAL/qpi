SELECT ft.trajectory_sub_id,
       ft.start_date_id,
       ft.end_date_id,
       ft.eta_date_id,
       asMFJSON(dt.trajectory)::json as trajectory,
       asMFJSON(dt.rot)::json as rot,
       asMFJSON(dt.heading)::json as heading,
       asMFJSON(dt.draught)::json as draught,
       dt.destination,
       ft.duration,
       ft.length,
       ft.infer_stopped as stopped,
       dns.nav_status as navigational_status
FROM fact_trajectory as ft
JOIN dim_trajectory as dt ON ft.trajectory_sub_id = dt.trajectory_sub_id AND ft.start_date_id = dt.date_id
JOIN dim_nav_status as dns ON ft.nav_status_id = dns.nav_status_id