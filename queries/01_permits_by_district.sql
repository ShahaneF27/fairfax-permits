-- Question 1: how many permits has each supervisor district had and what share of the county total is that

SELECT
    d.district_name,
    COUNT(*) AS permits,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_county
FROM permits AS p
JOIN districts AS d
    ON p.district_id = d.district_id
WHERE p.submitted_date BETWEEN '2019-01-01' AND '2025-12-31'
GROUP BY d.district_name
ORDER BY permits DESC;