--q5: which of the county's planned growth centers attract the most commercial activity (2019-2025)?
-- commercial = new commercial buildings, commercial alterations, and business occupancy approvals

SELECT
    COALESCE(gc.growth_center_name, '(Outside growth centers)' ) AS growth_center,
    COUNT(*) AS commercial_permits,
    SUM(CASE WHEN rt.record_type = 'Commercial New' THEN 1 ELSE 0 END) AS new_buildings,
    SUM(CASE WHEN rt.category = 'Business Occupancy' THEN 1 ELSE 0 END) AS business_occupancy,
    ROUND(100.0 * COUNT(*) /SUM(COUNT(*)) OVER (), 1) AS pct_of_commercial
FROM permits AS p
JOIN record_types AS rt
    ON p.record_type_id = rt.record_type_id
LEFT JOIN growth_centers AS gc
    ON p.growth_center_id = gc.growth_center_id
WHERE p.submitted_date BETWEEN '2019-01-01' AND '2025-12-31'
  AND rt.sector = 'Commercial'
GROUP BY growth_center
ORDER BY commercial_permits DESC
LIMIT 15;