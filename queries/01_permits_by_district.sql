-- Question 1: how many permits has each supervisor district had and what share of the county total is that

SELECT
    d.district_name,
    COUNT(*) AS permits,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM permits), 1) AS pct_of_county
FROM permits AS p
JOIN districts AS d
    ON p.district_id = d.district_id
GROUP BY d.district_name
ORDER BY permits DESC;