--Q4: how did the median processing time for construction permits change
--quarter by quarter from 2019 to 2025
--Did it jump after the )ct 2022 switch to PLUS

WITH timed AS (
    SELECT
        strftime('%Y', p.submitted_date) || '-Q' ||
            ((CAST(strftime('%m', p.submitted_date) AS INTEGER) + 2) / 3) AS quarter,
        p.days_to_decision
    FROM permits AS p
    JOIN record_types AS rt
        ON p.record_type_id = rt.record_type_id
    WHERE p.submitted_date BETWEEN '2019-01-01' AND '2025-12-31'
      AND rt.category = 'Construction'
      AND p.days_to_decision IS NOT NULL
),
ranked AS (
    SELECT
        quarter,
        days_to_decision,
        ROW_NUMBER() OVER (PARTITION BY quarter ORDER BY days_to_decision) AS rn,
        COUNT(*)     OVER (PARTITION BY quarter)                           AS n
    FROM timed
)
SELECT
    quarter,
    MAX(n) AS permits,
    ROUND(AVG(CASE WHEN rn IN ((n + 1) / 2, (n + 2) / 2) THEN days_to_decision END), 1) AS median_days
FROM ranked
GROUP BY quarter
ORDER BY quarter;