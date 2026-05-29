-- ============================================================
-- Query 1: Overall Medicare Drug Spend Summary
-- ============================================================
SELECT
    ROUND(SUM(total_drug_cost) / 1e9, 2)       AS total_spend_billions,
    SUM(total_claims)                           AS total_claims,
    SUM(total_beneficiaries)                    AS total_beneficiaries,
    COUNT(DISTINCT npi)                         AS unique_prescribers,
    COUNT(DISTINCT drug_key)                    AS unique_drugs,
    ROUND(AVG(cost_per_beneficiary), 2)         AS avg_cost_per_beneficiary,
    ROUND(AVG(cost_per_claim), 2)               AS avg_cost_per_claim
FROM fact_prescriptions;
