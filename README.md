# Medicare Drug Spending Intelligence

## Business Context
The U.S. spends over $200 billion annually on Medicare Part D prescription drugs.
This project analyses 5 years of real CMS prescriber data to answer four questions:

- **Where** is Medicare drug spending concentrated?
- **Which** drugs and providers drive the highest costs?
- **What** geographic patterns exist in prescribing behaviour?
- **Can** we predict high-cost drug utilisation by provider?

## Key Questions Answered
| Question | Finding |
|---|---|
| Top cost-driving drugs | TBD after analysis |
| Highest-spend states | TBD after analysis |
| Provider specialty patterns | TBD after analysis |
| Year-over-year cost trend | TBD after analysis |

## Live Dashboard
👉 Streamlit App — coming soon

## Tech Stack
| Layer | Tool |
|---|---|
| Database | DuckDB |
| Data Processing | Python, Pandas |
| SQL Modelling | Star Schema (fact + dimensions) |
| ML Layer | XGBoost + SHAP |
| Visualisation | Streamlit + Plotly |
| Data Source | CMS Medicare Part D (public) |

## Data Source
[CMS Medicare Part D Prescribers by Provider and Drug](https://data.cms.gov/provider-summary-by-type-of-service/medicare-part-d-prescribers/medicare-part-d-prescribers-by-provider-and-drug)
- Real government data — millions of prescriptions
- Provider name, drug name, total claims, total cost, beneficiary count
- State-level geographic breakdown

## Project Structure
```
medicare-drug-intelligence/
├── data/
│   ├── raw/                  # CMS downloaded data
│   └── processed/            # DuckDB exports
├── notebooks/
│   ├── 01_load_and_explore.py
│   ├── 02_build_schema.py
│   ├── 03_diagnostic_queries.py
│   ├── 04_train_model.py
│   └── 05_export.py
├── sql/
│   ├── dim_drug.sql
│   ├── dim_provider.sql
│   ├── dim_geography.sql
│   ├── fact_prescriptions.sql
│   └── queries/
├── streamlit_app/
│   └── app.py
└── models/
```
