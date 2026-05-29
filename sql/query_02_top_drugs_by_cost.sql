-- ============================================================
-- Query 2: Top 20 Drugs by Total Medicare Spend
-- Shows drug category, cost, claims, cost per claim
-- ============================================================
SELECT
    d.generic_name,
    d.brand_name,
    d.drug_category,
    ROUND(SUM(f.total_drug_cost) / 1e6, 1)          AS total_cost_millions,
    SUM(f.total_claims)                              AS total_claims,
    SUM(f.total_beneficiaries)                       AS total_beneficiaries,
    COUNT(DISTINCT f.npi)                            AS unique_prescribers,
    ROUND(SUM(f.total_drug_cost) / SUM(f.total_beneficiaries), 0)
                                                     AS cost_per_patient
FROM fact_prescriptions f
JOIN dim_drug d ON f.drug_key = d.drug_key
GROUP BY d.generic_name, d.brand_name, d.drug_category
ORDER BY SUM(f.total_drug_cost) DESC
LIMIT 20;
