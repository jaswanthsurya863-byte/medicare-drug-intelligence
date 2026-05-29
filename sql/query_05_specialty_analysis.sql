-- ============================================================
-- Query 5: Prescriber Specialty Analysis
-- Which specialties drive the most cost?
-- ============================================================
SELECT
    p.specialty_group,
    ROUND(SUM(f.total_drug_cost) / 1e6, 1)      AS total_cost_millions,
    SUM(f.total_claims)                          AS total_claims,
    COUNT(DISTINCT f.npi)                        AS unique_prescribers,
    ROUND(SUM(f.total_drug_cost)
          / COUNT(DISTINCT f.npi), 0)            AS avg_spend_per_prescriber,
    ROUND(SUM(f.total_drug_cost)
          / SUM(f.total_beneficiaries), 0)       AS avg_cost_per_patient
FROM fact_prescriptions f
JOIN dim_provider p ON f.npi = p.npi
GROUP BY p.specialty_group
ORDER BY SUM(f.total_drug_cost) DESC;
