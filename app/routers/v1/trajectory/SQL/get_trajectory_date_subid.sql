SELECT * FROM fact_trajectory WHERE start_date_id = :date_id AND trajectory_sub_id = :sub_id LIMIT 1;