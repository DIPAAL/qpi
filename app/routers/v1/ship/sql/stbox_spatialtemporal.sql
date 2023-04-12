STBOX(ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, 3034),
      span(timestamp_from_date_time_id(:from_date, :from_time),
      timestamp_from_date_time_id(:to_date, :to_time), True, True))
          && {RELATION_STBOX}.st_bounding_box