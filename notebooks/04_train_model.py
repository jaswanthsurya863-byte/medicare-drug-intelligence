# ============================================================
# Medicare Drug Intelligence — Step 4: Train ML Model
# ============================================================
# Goal: Predict which prescribers are HIGH-COST
# (above median drug spend) using their prescribing patterns
#
# Why this matters: Insurance companies and pharmacy benefit
# managers use exactly this kind of model to flag providers
# for review and cost management programs.

import duckdb
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import shap

print("✅ Packages loaded")

con = duckdb.connect("medicare.duckdb")
print("✅ DuckDB connected\n")

# ── 1. Build Provider-Level Feature Table ────────────────────
print("⏳ Building provider feature table (may take 1 min)...")

provider_features = con.execute("""
    SELECT
        f.npi,
        p.specialty_group,
        p.state,
        g.region,

        -- Volume features
        COUNT(DISTINCT f.drug_key)                          AS unique_drugs_prescribed,
        SUM(f.total_claims)                                 AS total_claims,
        SUM(f.total_beneficiaries)                          AS total_patients,
        SUM(f.total_drug_cost)                              AS total_drug_cost,

        -- Efficiency features
        ROUND(AVG(f.cost_per_claim), 2)                     AS avg_cost_per_claim,
        ROUND(AVG(f.cost_per_beneficiary), 2)               AS avg_cost_per_patient,

        -- GLP-1 / high-cost drug exposure
        SUM(CASE WHEN d.drug_category = 'GLP-1 / Weight Loss'
                 THEN f.total_claims ELSE 0 END)            AS glp1_claims,
        SUM(CASE WHEN d.drug_category = 'Oncology / Specialty'
                 THEN f.total_claims ELSE 0 END)            AS oncology_claims,
        SUM(CASE WHEN d.drug_category = 'Immunology / Biologics'
                 THEN f.total_claims ELSE 0 END)            AS biologic_claims,
        SUM(CASE WHEN d.drug_category = 'Blood Thinners'
                 THEN f.total_claims ELSE 0 END)            AS blood_thinner_claims,

        -- 65+ patient share
        ROUND(
            SUM(f.ge65_claims) * 100.0 / NULLIF(SUM(f.total_claims), 0)
        , 1)                                                AS pct_ge65_claims

    FROM fact_prescriptions f
    JOIN dim_provider p  ON f.npi = p.npi
    JOIN dim_geography g ON f.geo_key = g.geo_key
    JOIN dim_drug d      ON f.drug_key = d.drug_key
    GROUP BY f.npi, p.specialty_group, p.state, g.region
    HAVING SUM(f.total_claims) >= 50          -- exclude very low-volume prescribers
""").df()

print(f"✅ Provider features built: {len(provider_features):,} providers")
print(f"📊 Features shape: {provider_features.shape}")

# ── 2. Define Target: High-Cost Prescriber ───────────────────
median_cost = provider_features['total_drug_cost'].median()
provider_features['is_high_cost'] = (
    provider_features['total_drug_cost'] > median_cost
).astype(int)

print(f"\n💰 Median provider drug spend: ${median_cost:,.0f}")
print(f"📊 High-cost rate: {provider_features['is_high_cost'].mean():.2%}")

# ── 3. Encode Categorical Features ──────────────────────────
le_specialty = LabelEncoder()
le_region    = LabelEncoder()

provider_features['specialty_encoded'] = le_specialty.fit_transform(
    provider_features['specialty_group'].fillna('Unknown')
)
provider_features['region_encoded'] = le_region.fit_transform(
    provider_features['region'].fillna('Other')
)

# ── 4. Select Features ───────────────────────────────────────
feature_cols = [
    'unique_drugs_prescribed',
    'total_claims',
    'total_patients',
    'avg_cost_per_claim',
    'avg_cost_per_patient',
    'glp1_claims',
    'oncology_claims',
    'biologic_claims',
    'blood_thinner_claims',
    'pct_ge65_claims',
    'specialty_encoded',
    'region_encoded'
]

# Fill any nulls
provider_features[feature_cols] = provider_features[feature_cols].fillna(0)

X = provider_features[feature_cols]
y = provider_features['is_high_cost'].values

print(f"\n📊 Features: {len(feature_cols)}")
print(f"📊 Total providers for training: {len(X):,}")

# ── 5. Train / Test Split ────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\n✅ Train: {len(X_train):,} | Test: {len(X_test):,}")

# ── 6. Train XGBoost ─────────────────────────────────────────
neg, pos = np.bincount(y_train)
scale = neg / pos

model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    scale_pos_weight=scale,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='auc',
    early_stopping_rounds=20,
    verbosity=0
)

model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False
)
print("✅ Model trained!")

# ── 7. Evaluate ──────────────────────────────────────────────
y_pred_proba = model.predict_proba(X_test)[:, 1]
y_pred       = (y_pred_proba >= 0.5).astype(int)
auc          = roc_auc_score(y_test, y_pred_proba)

print(f"\n📊 ROC-AUC Score: {auc:.4f}")
print("\n📋 Classification Report:")
print(classification_report(y_test, y_pred,
      target_names=['Standard Cost', 'High Cost']))

# ── 8. SHAP Explainability ───────────────────────────────────
print("\n🔍 Computing SHAP values...")
explainer   = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)
print("✅ SHAP explainer ready")

# Feature importance summary
shap_importance = pd.DataFrame({
    'Feature':    feature_cols,
    'Mean_SHAP':  np.abs(shap_values).mean(axis=0)
}).sort_values('Mean_SHAP', ascending=False)

print("\n🏆 Top features by SHAP importance:")
print(shap_importance.to_string(index=False))

# ── 9. Save Model + Predictions ─────────────────────────────
import os
os.makedirs("models", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

with open("models/xgb_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("models/shap_explainer.pkl", "wb") as f:
    pickle.dump(explainer, f)

with open("models/label_encoders.pkl", "wb") as f:
    pickle.dump({'specialty': le_specialty, 'region': le_region}, f)

# Save full predictions for Streamlit
full_proba = model.predict_proba(X)[:, 1]
provider_features['high_cost_probability'] = full_proba
provider_features['predicted_high_cost']   = (full_proba >= 0.5).astype(int)

# Add provider name back for display
provider_names = con.execute("""
    SELECT npi, last_name, first_name, city, specialty
    FROM dim_provider
""").df()

output_df = provider_features.merge(provider_names, on='npi', how='left')
output_df.to_csv("data/processed/provider_predictions.csv", index=False)

con.close()

print(f"\n✅ Model saved  → models/xgb_model.pkl")
print(f"✅ Predictions  → data/processed/provider_predictions.csv")
print(f"\n🎯 Final AUC: {auc:.4f}")
print("📌 Next: Run 05_export.py")
