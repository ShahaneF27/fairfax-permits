-- Q3: how long does a decision typically take for each permit type (2019-2025)
-- Median is used instead of average because a few very long cases skew the average

WITH timed AS (
    SELECT
        rt.record_type,
        p.days_to_decision,
        ROW_NUMBER() OVER (PARTITION BY rt.record_type ORDER BY p.days_to_decision) AS rn,
        COUNT(*)     OVER (PARTITION BY rt.record_type)                             AS n
    FROM permits AS p
    JOIN record_types AS rt
        ON p.record_type_id = rt.record_type_id
    WHERE p.submitted_date BETWEEN '2019-01-01' AND '2025-12-31'
      AND p.days_to_decision IS NOT NULL
)
SELECT
    record_type,
    MAX(n) AS permits_timed,
    ROUND(AVG(CASE WHEN rn IN ((n + 1) / 2, (n + 2) / 2) THEN days_to_decision END), 1) AS median_days,
    ROUND(AVG(days_to_decision), 1) AS avg_days,
    ROUND(100.0 * SUM(CASE WHEN days_to_decision = 0  THEN 1 ELSE 0 END) / MAX(n), 1) AS pct_same_day,
    ROUND(100.0 * SUM(CASE WHEN days_to_decision > 90 THEN 1 ELSE 0 END) / MAX(n), 1) AS pct_over_90_days
FROM timed
GROUP BY record_type
ORDER BY median_days DESC;