WITH RECURSIVE pg_inherit(inhrelid, inhparent) AS
    (select inhrelid, inhparent
    FROM pg_inherits
    UNION
    SELECT child.inhrelid, parent.inhparent
    FROM pg_inherit child, pg_inherits parent
    WHERE child.inhparent = parent.inhrelid),
    pg_inherit_short AS (SELECT * FROM pg_inherit WHERE inhparent NOT IN (SELECT inhrelid FROM pg_inherit))
    SELECT TABLE_NAME,
	   relation_size AS CITUS_RELATION_SIZE,
	   table_size AS CITUS_TABLE_SIZE,
	   total_relation_size AS CITUS_TOTAL_RELATION_SIZE
    FROM (
        SELECT *
    FROM (
         SELECT c.oid,
				relname AS TABLE_NAME,
				SUM(citus_relation_size(c.oid)) OVER (partition BY parent) as relation_size,
				SUM(citus_table_size(c.oid)) OVER (partition BY parent) AS table_size,
				SUM(citus_total_relation_size(c.oid)) OVER (partition BY parent) AS total_relation_size,
				parent
          FROM (
                SELECT pg_class.oid,
			           reltuples,
			  		   relname,
			  		   relnamespace,
			  		   pg_class.reltoastrelid,
			           COALESCE(inhparent, pg_class.oid) parent
                FROM pg_class
                    LEFT JOIN pg_inherit_short ON inhrelid = oid
                WHERE relkind IN ('r', 'p') AND (relname LIKE ('fact_%') OR relname LIKE ('dim_%') OR relname = 'danish_waters')
             ) c
             LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
    ) a
    WHERE oid = parent
    ) b
    ORDER BY CITUS_TOTAL_RELATION_SIZE DESC;