FROM dim_ship ds
    JOIN dim_ship_type dst ON ds.ship_type_id = dst.ship_type_id