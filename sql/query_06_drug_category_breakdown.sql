-- ============================================================
-- Query 6: Spend by Drug Category
-- How much goes to each therapeutic area?
-- ============================================================
SELECT
    d.drug_category,
    ROUND(SUM(f.total_drug_cost) / 1e9, 2)      AS total_spend_billions,
    ROUND(SUM(f.total_drug_cost) * 100.0
          / SUM(SUM(f.total_drug_cost)) OVER (), 1)
                                                 AS pct_of_total_spend,
    SUM(f.total_claims)                          AS total_claims,
    COUNT(DISTINCT d.drug_key)                   AS unique_drugs,
    ROUND(SUM(f.total_drug_cost)
          / SUM(f.total_beneficiaries), 0)       AS avg_cost_per_patient
FROM fact_prescriptions f
JOIN dim_drug d ON f.drug_key = d.drug_key
GROUP BY d.drug_category
ORDER BY SUM(f.total_drug_cost) DESC;
