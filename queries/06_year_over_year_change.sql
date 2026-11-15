-- q6: how much did permit volume change each year comapred with the year before (2019-2025)

WITH yearly AS (
    SELECT
        strftime('%Y', p.submitted_date) AS year,
        COUNT(*) AS permits,
        SUM(CASE WHEN rt.sector = 'Commercial'  THEN 1 ELSE 0 END) AS commercial,
        SUM(CASE WHEN rt.sector = 'Residential' THEN 1 ELSE 0 END) AS residential
    FROM permits AS p
    JOIN record_types AS rt
        ON p.record_type_id = rt.record_type_id
    WHERE p.submitted_date BETWEEN '2019-01-01' AND '2025-12-31'
    GROUP BY year
)
SELECT
    year,
    permits,
    ROUND(100.0 * (permits - LAG(permits) OVER w) / LAG(permits) OVER w, 1)             AS pct_change,
    commercial,
    ROUND(100.0 * (commercial - LAG(commercial) OVER w) / LAG(commercial) OVER w, 1)    AS commercial_pct_change,
    residential,
    ROUND(100.0 * (residential - LAG(residential) OVER w) / LAG(residential) OVER w, 1) AS residential_pct_change
FROM yearly
WINDOW w AS (ORDER BY year)
ORDER BY year;
