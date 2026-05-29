-- ============================================================
-- Query 3: GLP-1 / Weight Loss Drug Deep Dive
-- Ozempic, Mounjaro, Trulicity — the $18B question
-- ============================================================

-- Part A: Total GLP-1 spend and scale
SELECT
    d.brand_name,
    d.generic_name,
    ROUND(SUM(f.total_drug_cost) / 1e6, 1)     AS total_cost_millions,
    SUM(f.total_claims)                         AS total_claims,
    SUM(f.total_beneficiaries)                  AS total_patients,
    COUNT(DISTINCT f.npi)                       AS prescribers,
    ROUND(SUM(f.total_drug_cost)
          / SUM(f.total_beneficiaries), 0)      AS annual_cost_per_patient
FROM fact_prescriptions f
JOIN dim_drug d ON f.drug_key = d.drug_key
WHERE d.drug_category = 'GLP-1 / Weight Loss'
GROUP BY d.brand_name, d.generic_name
ORDER BY SUM(f.total_drug_cost) DESC;
