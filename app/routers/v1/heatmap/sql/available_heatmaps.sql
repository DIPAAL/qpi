SELECT
    dht.slug,
    dht.name,
    dht.description,
    spatial_resolution,
    temporal_resolution_sec,
    TO_TIMESTAMP(min(date_id)::text, 'YYYYMMDD') as min_date,
    TO_TIMESTAMP(max(date_id)::text, 'YYYYMMDD') + INTERVAL '1 day' as max_date
FROM dim_heatmap_type dht
JOIN fact_cell_heatmap fch on dht.heatmap_type_id = fch.heatmap_type_id
GROUP BY dht.slug, dht.name, dht.description, spatial_resolution, temporal_resolution_sec