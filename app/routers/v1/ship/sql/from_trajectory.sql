FROM fact_trajectory ft
    JOIN dim_ship ds ON ft.ship_id = ds.ship_id
    JOIN dim_ship_type dst ON ds.ship_type_id = dst.ship_type_id
    JOIN dim_trajectory dt ON ft.trajectory_sub_id = dt.trajectory_sub_id