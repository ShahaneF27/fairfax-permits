-- Q2: how has permit volume changed year to year and how does the commercial activity compare with residentials

SELECT
    strftime('%Y', p.submitted_date) AS year,
    COUNT(*) AS total_permits,
    SUM(CASE WHEN rt.sector = 'Commercial' THEN 1 ELSE 0 END) AS commercial,
    SUM(CASE WHEN rt.sector = 'Residential' THEN 1 ELSE 0 END) AS residential
FROM permits AS p
JOIN record_types AS rt
    ON p.record_type_id = rt.record_type_id
WHERE p.submitted_date IS NOT NULL
GROUP BY year
ORDER BY year;