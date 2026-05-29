-- ============================================================
-- Query 4: Drug Spend by State and Region
-- ============================================================
SELECT
    g.state_abbr,
    g.state_name,
    g.region,
    ROUND(SUM(f.total_drug_cost) / 1e6, 1)      AS total_cost_millions,
    SUM(f.total_claims)                          AS total_claims,
    COUNT(DISTINCT f.npi)                        AS unique_prescribers,
    ROUND(SUM(f.total_drug_cost)
          / COUNT(DISTINCT f.npi), 0)            AS spend_per_prescriber
FROM fact_prescriptions f
JOIN dim_geography g ON f.geo_key = g.geo_key
WHERE g.state_abbr NOT IN ('XX', 'ZZ')         -- exclude unknown/territories
GROUP BY g.state_abbr, g.state_name, g.region
ORDER BY SUM(f.total_drug_cost) DESC;
