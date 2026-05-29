-- ============================================================
-- dim_drug: One row per unique drug
-- Adds a drug_category so we can group by therapeutic area
-- ============================================================
CREATE OR REPLACE TABLE dim_drug AS
SELECT
    ROW_NUMBER() OVER (ORDER BY Gnrc_Name, Brnd_Name) AS drug_key,
    Gnrc_Name                                          AS generic_name,
    Brnd_Name                                          AS brand_name,

    -- Classify drugs into therapeutic categories
    CASE
        WHEN Gnrc_Name ILIKE '%semaglutide%'
          OR Gnrc_Name ILIKE '%tirzepatide%'
          OR Gnrc_Name ILIKE '%dulaglutide%'
          OR Gnrc_Name ILIKE '%liraglutide%'
          OR Gnrc_Name ILIKE '%exenatide%'
            THEN 'GLP-1 / Weight Loss'

        WHEN Gnrc_Name ILIKE '%apixaban%'
          OR Gnrc_Name ILIKE '%rivaroxaban%'
          OR Gnrc_Name ILIKE '%warfarin%'
          OR Gnrc_Name ILIKE '%dabigatran%'
            THEN 'Blood Thinners'

        WHEN Gnrc_Name ILIKE '%empagliflozin%'
          OR Gnrc_Name ILIKE '%dapagliflozin%'
          OR Gnrc_Name ILIKE '%canagliflozin%'
          OR Gnrc_Name ILIKE '%sitagliptin%'
          OR Gnrc_Name ILIKE '%metformin%'
          OR Gnrc_Name ILIKE '%insulin%'
          OR Gnrc_Name ILIKE '%glipizide%'
          OR Gnrc_Name ILIKE '%glimepiride%'
            THEN 'Diabetes'

        WHEN Gnrc_Name ILIKE '%lenalidomide%'
          OR Gnrc_Name ILIKE '%enzalutamide%'
          OR Gnrc_Name ILIKE '%ibrutinib%'
          OR Gnrc_Name ILIKE '%abiraterone%'
          OR Gnrc_Name ILIKE '%bictegrav%'
          OR Gnrc_Name ILIKE '%palbociclib%'
          OR Gnrc_Name ILIKE '%pembrolizumab%'
            THEN 'Oncology / Specialty'

        WHEN Gnrc_Name ILIKE '%sacubitril%'
          OR Gnrc_Name ILIKE '%carvedilol%'
          OR Gnrc_Name ILIKE '%metoprolol%'
          OR Gnrc_Name ILIKE '%lisinopril%'
          OR Gnrc_Name ILIKE '%amlodipine%'
          OR Gnrc_Name ILIKE '%atorvastatin%'
          OR Gnrc_Name ILIKE '%rosuvastatin%'
            THEN 'Cardiology'

        WHEN Gnrc_Name ILIKE '%fluticasone%'
          OR Gnrc_Name ILIKE '%umeclidineum%'
          OR Gnrc_Name ILIKE '%tiotropium%'
          OR Gnrc_Name ILIKE '%budesonide%'
          OR Gnrc_Name ILIKE '%albuterol%'
            THEN 'Respiratory'

        WHEN Gnrc_Name ILIKE '%adalimumab%'
          OR Gnrc_Name ILIKE '%etanercept%'
          OR Gnrc_Name ILIKE '%ustekinumab%'
          OR Gnrc_Name ILIKE '%tofacitinib%'
            THEN 'Immunology / Biologics'

        WHEN Gnrc_Name ILIKE '%gabapentin%'
          OR Gnrc_Name ILIKE '%pregabalin%'
          OR Gnrc_Name ILIKE '%duloxetine%'
          OR Gnrc_Name ILIKE '%sertraline%'
          OR Gnrc_Name ILIKE '%escitalopram%'
          OR Gnrc_Name ILIKE '%tafamidis%'
            THEN 'Neurology / Mental Health'

        ELSE 'Other'
    END AS drug_category

FROM (
    SELECT DISTINCT Gnrc_Name, Brnd_Name
    FROM read_csv_auto('data/raw/Medicare_Part_D_Prescribers_by_Provider_and_Drug_2024.csv')
    WHERE Gnrc_Name IS NOT NULL
);
