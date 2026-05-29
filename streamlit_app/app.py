# ============================================================
# Medicare Drug Intelligence — Streamlit App
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import shap
import plotly.express as px
import plotly.graph_objects as go

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Medicare Drug Intelligence",
    page_icon="💊",
    layout="wide"
)

# ── Load Model & Data ────────────────────────────────────────
@st.cache_resource
def load_model():
    with open("models/xgb_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("models/shap_explainer.pkl", "rb") as f:
        explainer = pickle.load(f)
    with open("models/label_encoders.pkl", "rb") as f:
        encoders = pickle.load(f)
    return model, explainer, encoders

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/provider_predictions.csv")

model, explainer, encoders = load_model()
df = load_data()

# ── Pre-computed summary stats ───────────────────────────────
TOTAL_SPEND_B      = 226.74
TOTAL_CLAIMS       = 1_479_628_807
TOTAL_PROVIDERS    = 1_139_455
TOP_DRUG           = "Eliquis (Apixaban)"
TOP_DRUG_COST_B    = 19.9
GLP1_TOTAL_B       = 24.6

# ── Drug category data ───────────────────────────────────────
CATEGORY_DATA = pd.DataFrame({
    "Category": ["Other", "Diabetes", "Blood Thinners",
                 "GLP-1 / Weight Loss", "Oncology / Specialty",
                 "Respiratory", "Immunology / Biologics",
                 "Cardiology", "Neurology / Mental Health"],
    "Spend_B":  [103.2, 25.6, 25.5, 24.6, 16.8, 10.5, 10.5, 6.0, 4.0],
    "Pct":      [45.5, 11.3, 11.2, 10.9, 7.4, 4.6, 4.6, 2.6, 1.8]
})

TOP_DRUGS_DATA = pd.DataFrame({
    "Drug": ["Eliquis", "Ozempic", "Jardiance", "Mounjaro", "Xarelto",
             "Trelegy", "Trulicity", "Farxiga", "Humira", "Revlimid"],
    "Generic": ["Apixaban", "Semaglutide", "Empagliflozin", "Tirzepatide",
                "Rivaroxaban", "Fluticasone/Umeclidineum", "Dulaglutide",
                "Dapagliflozin", "Adalimumab", "Lenalidomide"],
    "Category": ["Blood Thinners", "GLP-1 / Weight Loss", "Diabetes",
                 "GLP-1 / Weight Loss", "Blood Thinners", "Respiratory",
                 "GLP-1 / Weight Loss", "Diabetes", "Immunology / Biologics",
                 "Oncology / Specialty"],
    "Cost_M": [19876, 12376, 10679, 5825, 5437, 4833, 4787, 4662, 3795, 3788],
    "Cost_Per_Patient": [4085, 7598, 4875, 9598, 6139, 4727, 11284, 5225, 141542, 179527]
})

STATE_DATA = pd.DataFrame({
    "state": ["CA","NY","FL","TX","PA","OH","NC","MI","IL","GA",
               "NJ","MA","TN","IN","MO","VA","AL","SC","AZ","KY"],
    "total_cost_millions": [21262,18174,16839,15746,11128,9043,8138,7821,7537,7304,
                             6264,5922,5660,5191,4834,4686,4398,4167,4104,3992],
    "region": ["West","Northeast","South","South","Northeast","Midwest","South",
                "Midwest","Midwest","South","Northeast","Northeast","South",
                "Midwest","Midwest","South","South","South","West","South"]
})

# ── Sidebar ──────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/pill.png", width=60)
st.sidebar.title("Medicare Drug Intelligence")
st.sidebar.markdown("**2024 CMS Part D Analysis**")
st.sidebar.markdown("*28M records · 1.1M providers · $226B spend*")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "💊 National Drug Dashboard",
    "🔬 Provider Risk Predictor",
    "🗺️ State Intelligence Map"
])

# ============================================================
# PAGE 1 — National Drug Dashboard
# ============================================================
if page == "💊 National Drug Dashboard":

    st.title("💊 Medicare Drug Spending Intelligence — 2024")
    st.markdown("*$226 billion in real U.S. government prescription data — where is it going?*")
    st.markdown("---")

    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Medicare Drug Spend", "$226.7B", "2024 actual")
    c2.metric("Total Prescriptions", "1.48 Billion", "claims filed")
    c3.metric("Unique Prescribers", "1,139,455", "across all states")
    c4.metric("Most Expensive Drug", "Eliquis", "$19.9B alone")

    st.markdown("---")

    # Row 1: Top drugs + Category breakdown
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Top 10 Drugs by Total Medicare Spend")
        fig1 = px.bar(
            TOP_DRUGS_DATA.sort_values("Cost_M"),
            x="Cost_M", y="Drug",
            orientation="h",
            color="Category",
            color_discrete_map={
                "Blood Thinners":        "#e74c3c",
                "GLP-1 / Weight Loss":   "#9b59b6",
                "Diabetes":              "#3498db",
                "Respiratory":           "#1abc9c",
                "Immunology / Biologics":"#e67e22",
                "Oncology / Specialty":  "#2c3e50"
            },
            labels={"Cost_M": "Total Cost ($M)", "Drug": ""},
            title="Eliquis leads — but GLP-1 drugs are surging"
        )
        fig1.update_layout(showlegend=True, height=420)
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.subheader("Spend by Therapeutic Category")
        fig2 = px.pie(
            CATEGORY_DATA,
            values="Spend_B",
            names="Category",
            title="GLP-1 drugs now = 10.9% of ALL Medicare drug spend",
            hole=0.4
        )
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        fig2.update_layout(showlegend=False, height=420)
        st.plotly_chart(fig2, use_container_width=True)

    # Row 2: GLP-1 deep dive + Cost per patient
    st.markdown("---")
    st.subheader("🔥 The GLP-1 Story — Ozempic, Mounjaro & the $24.6B Question")

    glp1_data = pd.DataFrame({
        "Drug":       ["Ozempic", "Mounjaro", "Trulicity", "Rybelsus", "Wegovy"],
        "Cost_M":     [12376, 5825, 4787, 1309, 107],
        "Patients":   [1628946, 606944, 424212, 80079, 4247],
        "Cost_Per_Patient": [7598, 9598, 11284, 16350, 25256]
    })

    col_c, col_d = st.columns(2)

    with col_c:
        fig3 = px.bar(glp1_data, x="Drug", y="Cost_M",
                      color="Cost_M",
                      color_continuous_scale="Purples",
                      title="GLP-1 Total Spend by Drug ($M)",
                      labels={"Cost_M": "Total Cost ($M)"})
        fig3.update_layout(showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        fig4 = px.bar(glp1_data, x="Drug", y="Cost_Per_Patient",
                      color="Cost_Per_Patient",
                      color_continuous_scale="Reds",
                      title="Annual Cost Per Patient ($) — Wegovy costs $25K/patient/year",
                      labels={"Cost_Per_Patient": "Annual Cost Per Patient ($)"})
        fig4.update_layout(showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    st.info("""
    **Key Insight:** Ozempic alone costs Medicare **$12.4 billion** for 1.6 million patients.
    Mounjaro costs **$9,598 per patient per year**. Wegovy costs **$25,256 per patient per year**.
    GLP-1 drugs went from near-zero to **10.9% of all Medicare drug spend** — and they are still growing.
    """)

# ============================================================
# PAGE 2 — Provider Risk Predictor
# ============================================================
elif page == "🔬 Provider Risk Predictor":

    st.title("🔬 Provider High-Cost Risk Predictor")
    st.markdown("Enter a provider's prescribing profile to predict whether they are a high-cost prescriber")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Prescribing Volume")
        unique_drugs    = st.slider("Unique Drugs Prescribed", 1, 100, 15)
        total_claims    = st.number_input("Total Annual Claims", 50, 100000, 2000)
        total_patients  = st.number_input("Total Annual Patients", 10, 50000, 500)
        pct_ge65        = st.slider("% of Patients Age 65+", 0, 100, 70)

    with col2:
        st.subheader("Drug Mix & Profile")
        avg_cost_claim  = st.number_input("Avg Cost Per Claim ($)", 10, 50000, 300)
        avg_cost_patient= st.number_input("Avg Cost Per Patient ($)", 50, 500000, 1500)
        glp1_claims     = st.number_input("GLP-1 Drug Claims (Ozempic/Mounjaro)", 0, 20000, 0)
        oncology_claims = st.number_input("Oncology Drug Claims", 0, 10000, 0)
        biologic_claims = st.number_input("Biologic Drug Claims", 0, 10000, 0)
        blood_thinner_claims = st.number_input("Blood Thinner Claims", 0, 20000, 0)
        specialty       = st.selectbox("Provider Specialty", sorted(
            encoders['specialty'].classes_.tolist()))
        region          = st.selectbox("Region", sorted(
            encoders['region'].classes_.tolist()))

    if st.button("🔬 Predict High-Cost Risk", type="primary"):

        # Encode inputs
        spec_encoded = encoders['specialty'].transform([specialty])[0]
        reg_encoded  = encoders['region'].transform([region])[0]

        input_data = pd.DataFrame([{
            "unique_drugs_prescribed": unique_drugs,
            "total_claims":            total_claims,
            "total_patients":          total_patients,
            "avg_cost_per_claim":      avg_cost_claim,
            "avg_cost_per_patient":    avg_cost_patient,
            "glp1_claims":             glp1_claims,
            "oncology_claims":         oncology_claims,
            "biologic_claims":         biologic_claims,
            "blood_thinner_claims":    blood_thinner_claims,
            "pct_ge65_claims":         pct_ge65,
            "specialty_encoded":       spec_encoded,
            "region_encoded":          reg_encoded
        }])

        prob = model.predict_proba(input_data)[0][1]

        st.markdown("---")
        st.subheader("Prediction Result")

        r1, r2, r3 = st.columns(3)

        if prob >= 0.7:
            risk_label    = "🔴 HIGH COST RISK"
            priority      = "Immediate Review"
        elif prob >= 0.4:
            risk_label    = "🟡 MODERATE RISK"
            priority      = "Monitor Closely"
        else:
            risk_label    = "🟢 STANDARD COST"
            priority      = "Routine Monitoring"

        r1.metric("High-Cost Probability", f"{prob:.1%}")
        r2.metric("Risk Classification",   risk_label)
        r3.metric("Recommended Action",    priority)

        # SHAP explanation
        st.subheader("Why is this provider flagged?")
        st.markdown("*SHAP values show which factors are driving the prediction*")

        shap_vals = explainer.shap_values(input_data)
        feature_names = [
            "Unique Drugs", "Total Claims", "Total Patients",
            "Avg Cost/Claim", "Avg Cost/Patient", "GLP-1 Claims",
            "Oncology Claims", "Biologic Claims", "Blood Thinner Claims",
            "% Age 65+", "Specialty", "Region"
        ]

        shap_df = pd.DataFrame({
            "Feature":   feature_names,
            "SHAP Value": shap_vals[0]
        }).sort_values("SHAP Value", key=abs, ascending=False).head(8)

        shap_df["Impact"] = shap_df["SHAP Value"].apply(
            lambda x: "Increases Cost Risk 🔴" if x > 0 else "Reduces Cost Risk 🟢")

        fig_shap = px.bar(shap_df, x="SHAP Value", y="Feature",
                          orientation="h", color="Impact",
                          color_discrete_map={
                              "Increases Cost Risk 🔴": "#e74c3c",
                              "Reduces Cost Risk 🟢":  "#2ecc71"
                          },
                          title="What's driving this provider's cost risk?")
        st.plotly_chart(fig_shap, use_container_width=True)

        # Recommendation
        st.subheader("💡 Recommended Action")
        if prob >= 0.7:
            st.error("""
            **High-Cost Provider — Immediate Review Recommended**
            - Flag for pharmacy benefit management review
            - Audit top 5 drugs by cost for this provider
            - Check for GLP-1 or biologic over-prescribing patterns
            - Consider prior authorization requirements
            """)
        elif prob >= 0.4:
            st.warning("""
            **Moderate Risk — Monitor Prescribing Patterns**
            - Add to monthly cost monitoring dashboard
            - Review drug mix for high-cost alternatives
            - Check formulary adherence
            """)
        else:
            st.success("""
            **Standard Cost Provider — Routine Monitoring**
            - No immediate action required
            - Continue standard quarterly review
            """)

# ============================================================
# PAGE 3 — State Intelligence Map
# ============================================================
elif page == "🗺️ State Intelligence Map":

    st.title("🗺️ Medicare Drug Spend — State Intelligence Map")
    st.markdown("Which states are driving the $226 billion bill?")
    st.markdown("---")

    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Highest Spend State",  "California",  "$21.3B")
    c2.metric("Highest Spend Region", "South",        "$87.6B — 38.6%")
    c3.metric("Spend per Prescriber", "Georgia",      "$236K avg — highest")
    c4.metric("Lowest Spend State",   "Wyoming",      "$190M")

    st.markdown("---")

    # Choropleth map
    st.subheader("Total Medicare Drug Spend by State ($M)")

    # Full state data for map
    all_states = pd.DataFrame({
        "state": ["CA","NY","FL","TX","PA","OH","NC","MI","IL","GA",
                   "NJ","MA","TN","IN","MO","VA","AL","SC","AZ","KY",
                   "LA","WI","WA","MD","MN","CT","CO","OK","OR","MS",
                   "AR","IA","KS","NV","WV","NE","UT","ME","ID","NM",
                   "NH","HI","RI","DE","DC","SD","MT","VT","ND","AK","WY"],
        "spend_M": [21262,18174,16839,15746,11128,9043,8138,7821,7537,7304,
                    6264,5922,5660,5191,4834,4686,4398,4167,4104,3992,
                    3910,3841,3562,3421,3287,3245,2738,2667,2293,2245,
                    2169,1965,1877,1554,1497,1273,1243,1081,991,947,
                    851,781,753,734,553,550,525,417,412,266,190]
    })

    fig_map = px.choropleth(
        all_states,
        locations="state",
        locationmode="USA-states",
        color="spend_M",
        scope="usa",
        color_continuous_scale="Reds",
        labels={"spend_M": "Spend ($M)"},
        title="Medicare Part D Drug Spend by State — 2024"
    )
    fig_map.update_layout(height=480)
    st.plotly_chart(fig_map, use_container_width=True)

    # Region breakdown
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Spend by Region")
        region_data = pd.DataFrame({
            "Region":    ["South", "Northeast", "Midwest", "West"],
            "Spend_B":   [87.57, 48.39, 47.63, 40.46],
            "Pct":       [38.6, 21.3, 21.0, 17.8]
        })
        fig_region = px.bar(region_data, x="Region", y="Spend_B",
                            color="Region",
                            color_discrete_map={
                                "South":     "#e74c3c",
                                "Northeast": "#3498db",
                                "Midwest":   "#2ecc71",
                                "West":      "#f39c12"
                            },
                            title="The South spends more than Northeast + Midwest on drugs",
                            labels={"Spend_B": "Total Spend ($B)"})
        fig_region.update_layout(showlegend=False)
        st.plotly_chart(fig_region, use_container_width=True)

    with col_b:
        st.subheader("Top 10 States — Spend per Prescriber")
        top10 = STATE_DATA.copy()
        top10["spend_per_prescriber"] = (
            top10["total_cost_millions"] * 1_000_000 /
            [113975,79262,78092,75623,52365,44830,37687,38086,42228,30920]
        ).round(0)
        top10 = top10.sort_values("spend_per_prescriber", ascending=False).head(10)
        fig_spp = px.bar(top10, x="state", y="spend_per_prescriber",
                         color="region",
                         title="Avg Medicare Drug Spend Per Prescriber by State",
                         labels={"spend_per_prescriber": "Spend per Prescriber ($)",
                                 "state": "State"})
        st.plotly_chart(fig_spp, use_container_width=True)

    st.markdown("---")
    st.caption("Medicare Drug Intelligence | CMS Part D Data 2024 | Built with DuckDB · XGBoost · SHAP · Streamlit")
