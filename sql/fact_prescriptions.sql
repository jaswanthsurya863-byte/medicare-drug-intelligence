-- ============================================================
-- fact_prescriptions: Central fact table
-- One row per provider-drug combination
-- Joins to all 3 dimension tables
-- ============================================================
CREATE OR REPLACE TABLE fact_prescriptions AS
SELECT
    -- Keys
    raw.Prscrbr_NPI                AS npi,
    d.drug_key,
    g.geo_key,

    -- Provider info (denormalised for query speed)
    raw.Prscrbr_Type               AS specialty,

    -- Core metrics
    raw.Tot_Clms                   AS total_claims,
    raw.Tot_30day_Fills            AS total_30day_fills,
    raw.Tot_Day_Suply              AS total_day_supply,
    raw.Tot_Drug_Cst               AS total_drug_cost,
    raw.Tot_Benes                  AS total_beneficiaries,

    -- 65+ age group metrics
    raw.GE65_Tot_Clms              AS ge65_claims,
    raw.GE65_Tot_Drug_Cst          AS ge65_drug_cost,
    raw.GE65_Tot_Benes             AS ge65_beneficiaries,

    -- Derived: cost per beneficiary
    CASE
        WHEN raw.Tot_Benes > 0
        THEN ROUND(raw.Tot_Drug_Cst / raw.Tot_Benes, 2)
        ELSE NULL
    END AS cost_per_beneficiary,

    -- Derived: cost per claim
    CASE
        WHEN raw.Tot_Clms > 0
        THEN ROUND(raw.Tot_Drug_Cst / raw.Tot_Clms, 2)
        ELSE NULL
    END AS cost_per_claim

FROM read_csv_auto('data/raw/Medicare_Part_D_Prescribers_by_Provider_and_Drug_2024.csv') raw

LEFT JOIN dim_drug d
    ON raw.Gnrc_Name = d.generic_name
    AND raw.Brnd_Name = d.brand_name

LEFT JOIN dim_geography g
    ON raw.Prscrbr_State_Abrvtn = g.state_abbr

WHERE raw.Tot_Drug_Cst IS NOT NULL
  AND raw.Tot_Clms     IS NOT NULL;
