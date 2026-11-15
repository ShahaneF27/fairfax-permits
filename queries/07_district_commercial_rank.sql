-- Q7: which districts led commercial activity each year (2019-2025)
-- show the top 3 districts per year

WITH district_year AS (
    SELECT
        strftime('%Y', p.submitted_date) AS YEAR,
        d.district_name,
        COUNT(*) AS commercial_permits
    FROM permits AS p
    JOIN record_types AS rt
        ON p.record_type_id = rt.record_type_id
    JOIN districts AS d
        ON p.district_id = d.district_id
    WHERE p.submitted_date BETWEEN '2019-01-01' AND '2025-12-31'
      AND rt.sector = 'Commercial'
    GROUP BY year, district_name
),
ranked AS (
    SELECT
        year,
        district_name,
        commercial_permits,
        RANK() OVER (PARTITION BY year ORDER BY commercial_permits DESC) AS rank_in_year
    FROM district_year
)
SELECT year, rank_in_year, district_name, commercial_permits
FROM ranked
WHERE rank_in_year <= 3
ORDER BY year, rank_in_year;