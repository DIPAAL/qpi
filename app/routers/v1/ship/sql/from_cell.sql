FROM fact_{CELL_SIZE} fc
    JOIN dim_ship ds ON fc.ship_id = ds.ship_id
    JOIN dim_ship_type dst ON ds.ship_type_id = dst.ship_type_id