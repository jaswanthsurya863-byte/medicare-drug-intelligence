# ============================================================
# Medicare Drug Intelligence — Step 3: Diagnostic Queries
# ============================================================

import duckdb
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)
pd.set_option('display.float_format', '{:,.1f}'.format)

con = duckdb.connect("medicare.duckdb")
print("✅ DuckDB connected\n")

# ── Query 1: Overall Summary ─────────────────────────────────
print("=" * 60)
print("QUERY 1 — Overall Medicare Drug Spend (2024)")
print("=" * 60)
with open("sql/query_01_overall_summary.sql") as f:
    result = con.execute(f.read()).df()
print(result.to_string(index=False))

# ── Query 2: Top 20 Drugs ────────────────────────────────────
print("\n" + "=" * 60)
print("QUERY 2 — Top 20 Drugs by Total Medicare Spend")
print("=" * 60)
with open("sql/query_02_top_drugs_by_cost.sql") as f:
    result = con.execute(f.read()).df()
print(result.to_string(index=False))

# ── Query 3: GLP-1 Deep Dive ─────────────────────────────────
print("\n" + "=" * 60)
print("QUERY 3 — GLP-1 / Weight Loss Drug Deep Dive")
print("=" * 60)
with open("sql/query_03_glp1_deep_dive.sql") as f:
    result = con.execute(f.read()).df()
print(result.to_string(index=False))

# ── Query 4: Spend by State ──────────────────────────────────
print("\n" + "=" * 60)
print("QUERY 4 — Medicare Drug Spend by State")
print("=" * 60)
with open("sql/query_04_spend_by_state.sql") as f:
    result = con.execute(f.read()).df()
print(result.to_string(index=False))

# ── Query 5: Specialty Analysis ──────────────────────────────
print("\n" + "=" * 60)
print("QUERY 5 — Spend by Provider Specialty")
print("=" * 60)
with open("sql/query_05_specialty_analysis.sql") as f:
    result = con.execute(f.read()).df()
print(result.to_string(index=False))

# ── Query 6: Drug Category Breakdown ────────────────────────
print("\n" + "=" * 60)
print("QUERY 6 — Spend by Drug Category")
print("=" * 60)
with open("sql/query_06_drug_category_breakdown.sql") as f:
    result = con.execute(f.read()).df()
print(result.to_string(index=False))

con.close()
print("\n✅ Step 3 complete — all diagnostic queries done!")
print("📌 Next: Run 04_train_model.py")
