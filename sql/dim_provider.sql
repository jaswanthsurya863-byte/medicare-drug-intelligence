-- ============================================================
-- dim_provider: One row per unique prescriber (NPI)
-- ============================================================
CREATE OR REPLACE TABLE dim_provider AS
SELECT DISTINCT
    Prscrbr_NPI                                    AS npi,
    Prscrbr_Last_Org_Name                          AS last_name,
    Prscrbr_First_Name                             AS first_name,
    Prscrbr_City                                   AS city,
    Prscrbr_State_Abrvtn                           AS state,
    Prscrbr_Type                                   AS specialty,

    -- Group specialties into broader categories
    CASE
        WHEN Prscrbr_Type ILIKE '%oncolog%'
          OR Prscrbr_Type ILIKE '%hematol%'
            THEN 'Oncology'
        WHEN Prscrbr_Type ILIKE '%cardiol%'
            THEN 'Cardiology'
        WHEN Prscrbr_Type ILIKE '%family%'
          OR Prscrbr_Type ILIKE '%internal medicine%'
          OR Prscrbr_Type ILIKE '%general practice%'
            THEN 'Primary Care'
        WHEN Prscrbr_Type ILIKE '%nurse practitioner%'
          OR Prscrbr_Type ILIKE '%physician assistant%'
            THEN 'Advanced Practice'
        WHEN Prscrbr_Type ILIKE '%endocrin%'
            THEN 'Endocrinology'
        WHEN Prscrbr_Type ILIKE '%neurol%'
          OR Prscrbr_Type ILIKE '%psychiatr%'
            THEN 'Neurology / Psychiatry'
        WHEN Prscrbr_Type ILIKE '%pulmon%'
          OR Prscrbr_Type ILIKE '%respirat%'
            THEN 'Pulmonology'
        WHEN Prscrbr_Type ILIKE '%rheumatol%'
            THEN 'Rheumatology'
        ELSE 'Other Specialty'
    END AS specialty_group

FROM read_csv_auto('data/raw/Medicare_Part_D_Prescribers_by_Provider_and_Drug_2024.csv')
WHERE Prscrbr_NPI IS NOT NULL;
