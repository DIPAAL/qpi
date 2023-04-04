SELECT *
FROM fact_trajectory ft
    JOIN dim_ship ds on ft.ship_id = ds.ship_id
    JOIN dim_trajectory dt on ft.trajectory_sub_id = dt.trajectory_sub_id
WHERE
    ft.start_date_id >= :from_date AND ft.end_date_id <= :to_date;