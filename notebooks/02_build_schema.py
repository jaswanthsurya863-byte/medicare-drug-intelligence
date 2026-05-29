# ============================================================
# Medicare Drug Intelligence — Step 2: Build Star Schema
# ============================================================
# What this script does:
#   1. Reads all 4 SQL files
#   2. Executes them in order inside DuckDB
#   3. Verifies every table was created correctly

import duckdb

print("✅ Packages loaded")

con = duckdb.connect("medicare.duckdb")
print("✅ DuckDB connected\n")

# ── SQL files to run in order ────────────────────────────────
sql_files = [
    ("dim_drug",          "sql/dim_drug.sql"),
    ("dim_geography",     "sql/dim_geography.sql"),
    ("dim_provider",      "sql/dim_provider.sql"),
    ("fact_prescriptions","sql/fact_prescriptions.sql"),
]

# ── Run each SQL file ────────────────────────────────────────
for table_name, filepath in sql_files:
    print(f"⏳ Building {table_name}...")
    with open(filepath, "r") as f:
        sql = f.read()
    con.execute(sql)
    count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"✅ {table_name}: {count:,} rows\n")

# ── Verify all tables exist ──────────────────────────────────
print("📋 All tables in DuckDB:")
tables = con.execute("SHOW TABLES").df()
print(tables.to_string(index=False))

# ── Quick join test ──────────────────────────────────────────
print("\n🔗 Join test — top 5 drugs by total cost with category:")
join_test = con.execute("""
    SELECT
        d.generic_name,
        d.brand_name,
        d.drug_category,
        ROUND(SUM(f.total_drug_cost) / 1e6, 1) AS total_cost_millions,
        SUM(f.total_claims) AS total_claims
    FROM fact_prescriptions f
    JOIN dim_drug d ON f.drug_key = d.drug_key
    GROUP BY d.generic_name, d.brand_name, d.drug_category
    ORDER BY SUM(f.total_drug_cost) DESC
    LIMIT 5
""").df()
print(join_test.to_string(index=False))

print("\n🌎 Join test — spend by region:")
region_test = con.execute("""
    SELECT
        g.region,
        ROUND(SUM(f.total_drug_cost) / 1e9, 2) AS total_spend_billions,
        SUM(f.total_claims) AS total_claims
    FROM fact_prescriptions f
    JOIN dim_geography g ON f.geo_key = g.geo_key
    GROUP BY g.region
    ORDER BY SUM(f.total_drug_cost) DESC
""").df()
print(region_test.to_string(index=False))

con.close()
print("\n✅ Step 2 complete — star schema is built!")
print("📌 Next: Run 03_diagnostic_queries.py")
