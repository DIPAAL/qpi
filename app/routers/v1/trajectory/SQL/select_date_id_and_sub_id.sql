SELECT ft.trajectory_sub_id,
       ft.start_date_id,
       ft.end_date_id,
       ft.eta_date_id,
       asMFJSON(dt.trajectory) as trajectory,
       asMFJSON(dt.rot) as rot,
       asMFJSON(dt.heading) as heading,
       asMFJSON(dt.draught) as draught,
       dt.destination,
       ft.duration,
       ft.length,
       ft.infer_stopped,
       dns.nav_status
FROM fact_trajectory as ft
JOIN dim_trajectory as dt ON ft.trajectory_sub_id = dt.trajectory_sub_id
JOIN dim_nav_status as dns ON ft.nav_status_id = dns.nav_status_id
WHERE ft.start_date_id = :date_id
AND ft.trajectory_sub_id = :sub_id;