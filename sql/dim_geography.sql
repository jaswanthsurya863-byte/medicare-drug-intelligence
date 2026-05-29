-- ============================================================
-- dim_geography: One row per U.S. state
-- Adds full state name and region grouping
-- ============================================================
CREATE OR REPLACE TABLE dim_geography AS
SELECT
    ROW_NUMBER() OVER (ORDER BY state_abbr) AS geo_key,
    state_abbr,
    CASE state_abbr
        WHEN 'AL' THEN 'Alabama'          WHEN 'AK' THEN 'Alaska'
        WHEN 'AZ' THEN 'Arizona'          WHEN 'AR' THEN 'Arkansas'
        WHEN 'CA' THEN 'California'       WHEN 'CO' THEN 'Colorado'
        WHEN 'CT' THEN 'Connecticut'      WHEN 'DE' THEN 'Delaware'
        WHEN 'FL' THEN 'Florida'          WHEN 'GA' THEN 'Georgia'
        WHEN 'HI' THEN 'Hawaii'           WHEN 'ID' THEN 'Idaho'
        WHEN 'IL' THEN 'Illinois'         WHEN 'IN' THEN 'Indiana'
        WHEN 'IA' THEN 'Iowa'             WHEN 'KS' THEN 'Kansas'
        WHEN 'KY' THEN 'Kentucky'         WHEN 'LA' THEN 'Louisiana'
        WHEN 'ME' THEN 'Maine'            WHEN 'MD' THEN 'Maryland'
        WHEN 'MA' THEN 'Massachusetts'    WHEN 'MI' THEN 'Michigan'
        WHEN 'MN' THEN 'Minnesota'        WHEN 'MS' THEN 'Mississippi'
        WHEN 'MO' THEN 'Missouri'         WHEN 'MT' THEN 'Montana'
        WHEN 'NE' THEN 'Nebraska'         WHEN 'NV' THEN 'Nevada'
        WHEN 'NH' THEN 'New Hampshire'    WHEN 'NJ' THEN 'New Jersey'
        WHEN 'NM' THEN 'New Mexico'       WHEN 'NY' THEN 'New York'
        WHEN 'NC' THEN 'North Carolina'   WHEN 'ND' THEN 'North Dakota'
        WHEN 'OH' THEN 'Ohio'             WHEN 'OK' THEN 'Oklahoma'
        WHEN 'OR' THEN 'Oregon'           WHEN 'PA' THEN 'Pennsylvania'
        WHEN 'RI' THEN 'Rhode Island'     WHEN 'SC' THEN 'South Carolina'
        WHEN 'SD' THEN 'South Dakota'     WHEN 'TN' THEN 'Tennessee'
        WHEN 'TX' THEN 'Texas'            WHEN 'UT' THEN 'Utah'
        WHEN 'VT' THEN 'Vermont'          WHEN 'VA' THEN 'Virginia'
        WHEN 'WA' THEN 'Washington'       WHEN 'WV' THEN 'West Virginia'
        WHEN 'WI' THEN 'Wisconsin'        WHEN 'WY' THEN 'Wyoming'
        WHEN 'DC' THEN 'Washington D.C.'
        ELSE 'Other / Territory'
    END AS state_name,
    CASE state_abbr
        WHEN 'CT' THEN 'Northeast' WHEN 'ME' THEN 'Northeast'
        WHEN 'MA' THEN 'Northeast' WHEN 'NH' THEN 'Northeast'
        WHEN 'RI' THEN 'Northeast' WHEN 'VT' THEN 'Northeast'
        WHEN 'NJ' THEN 'Northeast' WHEN 'NY' THEN 'Northeast'
        WHEN 'PA' THEN 'Northeast' WHEN 'DC' THEN 'Northeast'
        WHEN 'IL' THEN 'Midwest'   WHEN 'IN' THEN 'Midwest'
        WHEN 'MI' THEN 'Midwest'   WHEN 'OH' THEN 'Midwest'
        WHEN 'WI' THEN 'Midwest'   WHEN 'IA' THEN 'Midwest'
        WHEN 'KS' THEN 'Midwest'   WHEN 'MN' THEN 'Midwest'
        WHEN 'MO' THEN 'Midwest'   WHEN 'NE' THEN 'Midwest'
        WHEN 'ND' THEN 'Midwest'   WHEN 'SD' THEN 'Midwest'
        WHEN 'DE' THEN 'South'     WHEN 'FL' THEN 'South'
        WHEN 'GA' THEN 'South'     WHEN 'MD' THEN 'South'
        WHEN 'NC' THEN 'South'     WHEN 'SC' THEN 'South'
        WHEN 'VA' THEN 'South'     WHEN 'WV' THEN 'South'
        WHEN 'AL' THEN 'South'     WHEN 'KY' THEN 'South'
        WHEN 'MS' THEN 'South'     WHEN 'TN' THEN 'South'
        WHEN 'AR' THEN 'South'     WHEN 'LA' THEN 'South'
        WHEN 'OK' THEN 'South'     WHEN 'TX' THEN 'South'
        WHEN 'AZ' THEN 'West'      WHEN 'CO' THEN 'West'
        WHEN 'ID' THEN 'West'      WHEN 'MT' THEN 'West'
        WHEN 'NV' THEN 'West'      WHEN 'NM' THEN 'West'
        WHEN 'UT' THEN 'West'      WHEN 'WY' THEN 'West'
        WHEN 'AK' THEN 'West'      WHEN 'CA' THEN 'West'
        WHEN 'HI' THEN 'West'      WHEN 'OR' THEN 'West'
        WHEN 'WA' THEN 'West'
        ELSE 'Other'
    END AS region
FROM (
    SELECT DISTINCT Prscrbr_State_Abrvtn AS state_abbr
    FROM read_csv_auto('data/raw/Medicare_Part_D_Prescribers_by_Provider_and_Drug_2024.csv')
    WHERE Prscrbr_State_Abrvtn IS NOT NULL
);
