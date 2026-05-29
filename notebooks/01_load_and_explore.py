# ============================================================
# Medicare Drug Intelligence — Step 1: Load & Explore
# ============================================================
# What this script does:
#   1. Connects to DuckDB
#   2. Reads 4GB CSV directly (no pandas memory crash)
#   3. Counts rows and columns
#   4. Checks for nulls in key columns
#   5. Shows top drugs by cost — first look at the data

import duckdb
import pandas as pd

print("✅ Packages loaded")

# ── 1. Connect to DuckDB ─────────────────────────────────────
con = duckdb.connect("medicare.duckdb")
print("✅ DuckDB connected")

# ── 2. Point DuckDB at the raw CSV ───────────────────────────
RAW_FILE = "data/raw/Medicare_Part_D_Prescribers_by_Provider_and_Drug_2024.csv"

# ── 3. Row & Column Count ────────────────────────────────────
print("\n📊 Counting rows (this may take 30 seconds on 4GB file)...")

row_count = con.execute(f"""
    SELECT COUNT(*) AS total_rows
    FROM read_csv_auto('{RAW_FILE}')
""").fetchone()[0]

col_count = con.execute(f"""
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_name = 'read_csv_auto'
""")

print(f"✅ Total rows: {row_count:,}")

# ── 4. Preview Columns ───────────────────────────────────────
print("\n📋 Columns in dataset:")
cols = con.execute(f"""
    DESCRIBE SELECT * FROM read_csv_auto('{RAW_FILE}') LIMIT 1
""").df()
print(cols[['column_name', 'column_type']].to_string(index=False))

# ── 5. Null Check on Key Columns ─────────────────────────────
print("\n🔍 Null check on key columns...")
null_check = con.execute(f"""
    SELECT
        COUNT(*) AS total_rows,
        SUM(CASE WHEN Prscrbr_NPI IS NULL THEN 1 ELSE 0 END) AS null_npi,
        SUM(CASE WHEN Gnrc_Name IS NULL THEN 1 ELSE 0 END) AS null_drug,
        SUM(CASE WHEN Tot_Drug_Cst IS NULL THEN 1 ELSE 0 END) AS null_cost,
        SUM(CASE WHEN Prscrbr_State_Abrvtn IS NULL THEN 1 ELSE 0 END) AS null_state,
        SUM(CASE WHEN Prscrbr_Type IS NULL THEN 1 ELSE 0 END) AS null_specialty
    FROM read_csv_auto('{RAW_FILE}')
""").df()
print(null_check.to_string(index=False))

# ── 6. Total Medicare Drug Spend ─────────────────────────────
print("\n💰 Total Medicare drug spend in dataset:")
total_spend = con.execute(f"""
    SELECT
        ROUND(SUM(Tot_Drug_Cst) / 1e9, 2) AS total_spend_billions,
        ROUND(AVG(Tot_Drug_Cst), 2) AS avg_cost_per_record,
        SUM(Tot_Clms) AS total_claims
    FROM read_csv_auto('{RAW_FILE}')
    WHERE Tot_Drug_Cst IS NOT NULL
""").df()
print(total_spend.to_string(index=False))

# ── 7. Top 15 Drugs by Total Cost ────────────────────────────
print("\n🏆 Top 15 drugs by total Medicare spend:")
top_drugs = con.execute(f"""
    SELECT
        Gnrc_Name AS drug_name,
        Brnd_Name AS brand_name,
        ROUND(SUM(Tot_Drug_Cst) / 1e6, 1) AS total_cost_millions,
        SUM(Tot_Clms) AS total_claims,
        COUNT(DISTINCT Prscrbr_NPI) AS unique_prescribers
    FROM read_csv_auto('{RAW_FILE}')
    WHERE Tot_Drug_Cst IS NOT NULL
    GROUP BY Gnrc_Name, Brnd_Name
    ORDER BY SUM(Tot_Drug_Cst) DESC
    LIMIT 15
""").df()
print(top_drugs.to_string(index=False))

# ── 8. Top 10 States by Total Spend ──────────────────────────
print("\n🗺️  Top 10 states by Medicare drug spend:")
top_states = con.execute(f"""
    SELECT
        Prscrbr_State_Abrvtn AS state,
        ROUND(SUM(Tot_Drug_Cst) / 1e6, 1) AS total_cost_millions,
        SUM(Tot_Clms) AS total_claims,
        COUNT(DISTINCT Prscrbr_NPI) AS unique_prescribers
    FROM read_csv_auto('{RAW_FILE}')
    WHERE Prscrbr_State_Abrvtn IS NOT NULL
      AND Tot_Drug_Cst IS NOT NULL
    GROUP BY Prscrbr_State_Abrvtn
    ORDER BY SUM(Tot_Drug_Cst) DESC
    LIMIT 10
""").df()
print(top_states.to_string(index=False))

# ── 9. Top 10 Provider Specialties by Spend ──────────────────
print("\n👨‍⚕️  Top 10 provider specialties by total drug spend:")
top_specialties = con.execute(f"""
    SELECT
        Prscrbr_Type AS specialty,
        ROUND(SUM(Tot_Drug_Cst) / 1e6, 1) AS total_cost_millions,
        SUM(Tot_Clms) AS total_claims,
        COUNT(DISTINCT Prscrbr_NPI) AS unique_prescribers
    FROM read_csv_auto('{RAW_FILE}')
    WHERE Prscrbr_Type IS NOT NULL
      AND Tot_Drug_Cst IS NOT NULL
    GROUP BY Prscrbr_Type
    ORDER BY SUM(Tot_Drug_Cst) DESC
    LIMIT 10
""").df()
print(top_specialties.to_string(index=False))

con.close()
print("\n✅ Step 1 complete — data is real, loaded, and ready for star schema!")
print("📌 Next: Run 02_build_schema.py")
