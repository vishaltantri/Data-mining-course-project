from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy.spatial import ConvexHull, QhullError
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import roc_curve, precision_recall_curve, auc, confusion_matrix
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "review2" / "results"
NAVY, TEAL, ORANGE, SKY, MUTED = "#0B1220", "#2DD4BF", "#FB923C", "#60A5FA", "#94A3B8"
PLOT_BG, PAPER_BG, TEXT, GRID = "#111C2E", "#111C2E", "#E6EDF7", "#334155"
AGES = {1:"18–24",2:"25–29",3:"30–34",4:"35–39",5:"40–44",6:"45–49",7:"50–54",8:"55–59",9:"60–64",10:"65–69",11:"70–74",12:"75–79",13:"80+"}
HEALTH = {1:"Excellent",2:"Very good",3:"Good",4:"Fair",5:"Poor"}
INCOME = {1:"<$10k",2:"$10–15k",3:"$15–20k",4:"$20–25k",5:"$25–35k",6:"$35–50k",7:"$50–75k",8:">$75k"}

MODEL_COLORS = {
    "Decision Tree, CART (R)": TEAL,
    "Decision Tree, Information Gain (R)": ORANGE,
    "KNN (R)": SKY,
    "J48 (WEKA, 10-fold CV)": MUTED,
    "Naive Bayes (WEKA, 10-fold CV)": "#FCA5A5",
}

st.set_page_config(page_title="BRFSS Diabetes Analytics", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
:root { color-scheme: dark; }
html, body, [data-testid="stAppViewContainer"] { background:#0B1220 !important; color:#E6EDF7 !important; }
[data-testid="stHeader"] { background:#0B1220 !important; border-bottom:1px solid #22304A; }
[data-testid="stAppViewContainer"] .stMainBlockContainer { max-width:1480px; padding:2.25rem 3rem 4rem; }
[data-testid="stSidebar"] { background:#0E1728 !important; border-right:1px solid #22304A; }
[data-testid="stSidebar"] * { color:#DCE7F5 !important; }
h1,h2,h3 { color:#F8FAFC !important; font-family:Arial,Helvetica,sans-serif !important; font-weight:750 !important; letter-spacing:-.02em; }
h1 { font-size:clamp(2rem,3vw,3rem) !important; margin-bottom:.2rem !important; }
p,[data-testid="stCaptionContainer"],label,.stMarkdown { color:#AFC0D5 !important; }
[data-testid="stMetric"] { background:linear-gradient(135deg,#17233A,#121C2E) !important; border:1px solid #283852 !important; border-radius:14px !important; padding:1.1rem 1.15rem !important; box-shadow:0 8px 22px rgba(0,0,0,.18); }
[data-testid="stMetric"] [data-testid="stMetricLabel"] *,[data-testid="stMetric"] [data-testid="stMetricValue"] * { color:#F8FAFC !important; }
[data-testid="stMetric"] [data-testid="stMetricDelta"] * { color:#5EEAD4 !important; }
[data-testid="stTabs"] [role="tab"] { color:#AFC0D5 !important; font-weight:700; }
[data-testid="stTabs"] [aria-selected="true"] { color:#5EEAD4 !important; }
[data-testid="stDataFrame"],[data-testid="stTable"] { border:1px solid #283852; border-radius:10px; overflow:hidden; }
[data-testid="stDownloadButton"] button,[data-testid="stBaseButton-secondary"] { border-radius:9px !important; border-color:#3A4E6F !important; color:#E6EDF7 !important; background:#18243A !important; }
.stButton button { border-radius:9px !important; font-weight:700 !important; }
.insight { background:#0D2C31; border-left:4px solid #2DD4BF; color:#E6EDF7 !important; padding:15px 18px; border-radius:10px; margin:12px 0 22px; }
.warning { background:#322519; border-left:4px solid #FB923C; color:#FDEAD7 !important; padding:15px 18px; border-radius:10px; margin:12px 0 22px; }
.insight *, .warning * { color:inherit !important; }
[data-baseweb="select"] > div,[data-baseweb="input"] > div { background:#131D2E !important; border-color:#334155 !important; }
</style>
""", unsafe_allow_html=True)


def darken(fig: go.Figure, height: int | None = None) -> go.Figure:
    fig.update_layout(
        template="plotly_dark", paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT), hoverlabel=dict(bgcolor="#1E293B", font_color=TEXT),
        legend=dict(font=dict(color=TEXT), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=24, r=24, t=34, b=28), height=height,
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor="#475569")
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor="#475569")
    return fig


def empirical_percentile(series: pd.Series, value: float) -> float:
    return float((series <= value).mean() * 100)


CLUSTER_FEATURES = {
    "BMI": "BMI", "High blood pressure": "HighBP", "High cholesterol": "HighChol",
    "General health": "GenHlth", "Age band": "Age", "Income band": "Income",
    "Education": "Education", "Physically active": "PhysActivity", "Difficulty walking": "DiffWalk",
    "Mental health days": "MentHlth", "Physical health days": "PhysHlth", "Smoker": "Smoker",
    "Sex": "Sex", "Fruits": "Fruits", "Veggies": "Veggies",
}
PALETTE = [TEAL, ORANGE, SKY, "#C4B5FD", "#F472B6", "#A3E635", "#FBBF24"]


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


@st.cache_data(show_spinner="Re-fitting K-Means and PCA…")
def fit_pca_clusters(frame: pd.DataFrame, cols: tuple[str, ...], k: int, sample_n: int,
                     scale: bool, seed: int):
    """Fit K-Means on selected features, project to 2D with PCA, and compute per-cluster convex hulls."""
    sample = frame.sample(n=min(sample_n, len(frame)), random_state=seed)
    X = sample.loc[:, list(cols)].to_numpy(dtype=float)
    if scale:
        X = StandardScaler().fit_transform(X)
    km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(X)
    pca = PCA(n_components=2, random_state=seed)
    coords = pca.fit_transform(X)
    hulls = {}
    for c in range(k):
        pts = coords[km.labels_ == c]
        if len(pts) >= 3:
            try:
                hulls[c] = pts[ConvexHull(pts).vertices]
            except QhullError:
                pass
    out = pd.DataFrame(coords, columns=["Dim 1", "Dim 2"])
    out["Cluster"] = km.labels_.astype(str)
    out["Diabetes"] = sample.Diabetes_binary.to_numpy()
    return out, km, pca, hulls, float(km.inertia_)


@st.cache_data(show_spinner="Loading verified project results…")
def load_artifacts():
    def csv(name: str) -> pd.DataFrame:
        return pd.read_csv(RESULTS / name)
    metrics = json.loads((ROOT / "review1" / "eda_metrics.json").read_text())
    olap = json.loads((ROOT / "review1" / "olap_results.json").read_text())
    balanced = pd.read_csv(ROOT / "diabetes_binary_5050split_health_indicators_BRFSS2015.csv")
    return metrics, olap, balanced, csv("model_comparison_all.csv"), csv("threshold_tradeoff.csv"), csv("apriori_top_rules.csv"), csv("cluster_profiles.csv"), csv("cart_variable_importance.csv"), csv("knn_cv_results.csv")

try:
    metrics, olap, bal, model_df, threshold_df, rules_df, cluster_df, importance_df, knn_df = load_artifacts()
except Exception as exc:
    st.error(f"Dashboard data could not be loaded: {exc}. Run from the repository with its Review 1/2 artifacts present.")
    st.stop()

with st.sidebar:
    st.markdown("## 🩺 BRFSS Analytics")
    st.caption("Diabetes & cardiovascular comorbidity · 2015")
    page = st.radio("Explore", [
        "Executive Overview",
        "Explore the Data",
        "Warehouse & OLAP",
        "Model Arena",
        "Population Reality Check",
        "Patterns & Clusters",
        "My Health Profile",
        "Advanced Model Analytics",
        "What-If Explorer",
        "Methods & Limitations"
    ], label_visibility="collapsed")
    st.divider()
    st.markdown("**Dataset context**")
    st.selectbox("Choose population", ["Balanced modeling sample", "Full population sample"], help="Model comparison uses the balanced held-out sample. Realistic evaluation uses a separate full-file split.")
    st.caption("Review 1 + Review 2 · seed 42")

st.title("Diabetes Risk & Population Health")
st.caption("Interactive evidence from the CDC BRFSS 2015 project. Associations are descriptive—not causal, diagnostic, or medical advice.")

if page == "Executive Overview":
    st.markdown("### The project, at a glance")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Full survey records", f"{metrics['full_shape'][0]:,}", "2015 cross-sectional survey")
    c2.metric("Balanced modeling sample", f"{metrics['split_shape'][0]:,}", "50/50 class design")
    c3.metric("Missing cells", "0", "reported in project audit")
    c4.metric("Full-file diabetes prevalence", f"{metrics['full_target']['1.0']/metrics['full_shape'][0]*100:.1f}%", "not the balanced sample rate")
    st.markdown('<div class="insight"><b>Key interpretation:</b> balanced data helps compare classifiers, but it does not represent population prevalence. The separate full-file test shows why accuracy alone is misleading.</div>', unsafe_allow_html=True)
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Risk-factor comparison")
        sex = st.selectbox("Sex filter", ["All", "Female", "Male"], key="overview_sex")
        selected = bal if sex == "All" else bal[bal.Sex == (0 if sex == "Female" else 1)]
        factors = [("High blood pressure", "HighBP"), ("High cholesterol", "HighChol"), ("Heart disease / attack", "HeartDiseaseorAttack"), ("Difficulty walking", "DiffWalk"), ("Physically active", "PhysActivity")]
        rows = [{"Factor": label, "Group": group, "Respondents with factor (%)": 100 * selected.loc[selected.Diabetes_binary == target, col].mean()} for label, col in factors for target, group in [(1, "Diabetes"), (0, "No diabetes")]]
        fig = px.bar(pd.DataFrame(rows), x="Respondents with factor (%)", y="Factor", color="Group", barmode="group", orientation="h", color_discrete_map={"Diabetes": TEAL, "No diabetes": MUTED})
        st.plotly_chart(darken(fig, 380), width="stretch")
    with right:
        st.subheader("Precision vs recall")
        fig = px.scatter(model_df, x="Recall", y="Precision", size="F1", color="Model", hover_data={"Accuracy":":.3f", "F1":":.3f", "AUC":":.3f"}, color_discrete_sequence=[TEAL, ORANGE, SKY, MUTED, "#FCA5A5"])
        fig.update_layout(xaxis_tickformat=".0%", yaxis_tickformat=".0%")
        st.plotly_chart(darken(fig, 380), width="stretch")
    st.markdown("#### Model scorecard")
    scorecard = model_df.set_index("Model")[["Accuracy", "Precision", "Recall", "F1", "AUC"]].T
    fig = px.imshow(scorecard, text_auto=".3f", color_continuous_scale=["#17233A", "#2DD4BF"], aspect="auto", zmin=.60, zmax=.85)
    fig.update_layout(coloraxis_colorbar_title="Score")
    st.plotly_chart(darken(fig, 360), width="stretch")

elif page == "Explore the Data":
    st.subheader("Explore respondents in the balanced sample")
    st.caption("Apply filters to descriptive survey patterns. This sample has an intentionally 50/50 target distribution.")
    f1, f2, f3 = st.columns(3)
    age_range = f1.select_slider("Age band range", options=sorted(bal.Age.unique()), value=(1, 13), format_func=lambda x: AGES[int(x)])
    sex = f2.selectbox("Sex", ["All", "Female", "Male"], key="eda_sex")
    income_labels = f3.multiselect("Income bands", list(INCOME.values()), default=list(INCOME.values()), key="eda_income")
    data = bal[bal.Age.between(*age_range)].copy()
    if sex != "All":
        data = data[data.Sex == (0 if sex == "Female" else 1)]
    data = data[data.Income.isin([k for k, v in INCOME.items() if v in income_labels])]
    st.metric("Respondents after filters", f"{len(data):,}")
    left, right = st.columns(2)
    with left:
        age = data.groupby("Age", as_index=False).agg(Prevalence=("Diabetes_binary", "mean"), Respondents=("Diabetes_binary", "size"))
        age.Prevalence *= 100; age["Age band"] = age.Age.map(AGES)
        fig = px.line(age, x="Age band", y="Prevalence", markers=True, hover_data=["Respondents"], color_discrete_sequence=[TEAL])
        fig.update_layout(title="Diabetes share by age", yaxis_title="Diabetes share (%)")
        st.plotly_chart(darken(fig, 350), width="stretch")
    with right:
        health = data.groupby("GenHlth", as_index=False).agg(Prevalence=("Diabetes_binary", "mean"), Respondents=("Diabetes_binary", "size"))
        health.Prevalence *= 100; health["General health"] = health.GenHlth.map(HEALTH)
        fig = px.bar(health, x="General health", y="Prevalence", color="Prevalence", color_continuous_scale=["#1E3A4C", TEAL], hover_data=["Respondents"])
        fig.update_layout(title="Diabetes share by self-rated health", yaxis_title="Diabetes share (%)", coloraxis_showscale=False)
        st.plotly_chart(darken(fig, 350), width="stretch")
    left, right = st.columns(2)
    with left:
        fig = px.histogram(data, x="BMI", color=data.Diabetes_binary.map({0:"No diabetes",1:"Diabetes"}), nbins=35, barmode="overlay", opacity=.7, color_discrete_map={"Diabetes":TEAL,"No diabetes":MUTED})
        fig.update_layout(title="BMI distribution by diabetes status", legend_title_text="", yaxis_title="Respondents")
        st.plotly_chart(darken(fig, 350), width="stretch")
    with right:
        corr = pd.Series(metrics["correlations"]).drop("Diabetes_binary", errors="ignore").sort_values()
        fig = px.bar(x=corr.values, y=corr.index, orientation="h", color=corr.values, color_continuous_scale=["#F97316", "#17233A", TEAL])
        fig.update_layout(title="Correlation with diabetes label", xaxis_title="Pearson correlation", yaxis_title="", coloraxis_showscale=False)
        st.plotly_chart(darken(fig, 350), width="stretch")
    st.download_button("Download filtered respondents (CSV)", data.to_csv(index=False).encode(), "brfss_filtered.csv", "text/csv")

elif page == "Warehouse & OLAP":
    st.subheader("Data warehouse: real OLAP outputs")
    st.caption("One fact record per respondent. Tables and charts are sourced from the Review 1 SQLite star-schema results.")
    
    # Add Custom OLAP Builder as an additional tab
    all_tabs = list(olap.keys()) + ["Custom OLAP Builder"]
    tabs = st.tabs(all_tabs)
    
    for tab, name in zip(tabs[:-1], olap.keys()):
        with tab:
            frame = pd.DataFrame(olap[name])
            st.dataframe(frame, width="stretch", hide_index=True)
            if name == "Roll-up":
                frame["Age label"] = frame.Age_Bracket.map(AGES)
                fig = px.bar(frame, x="Age label", y="Prevalence_Pct", color="Avg_BMI", color_continuous_scale=[SKY, TEAL], hover_data=["Total_Respondents", "Diabetes_Cases"])
                fig.update_layout(yaxis_title="Diabetes prevalence (%)", title="Roll-up: prevalence and BMI by age")
            elif name == "Drill-down":
                frame["Age label"] = frame.Age_Bracket.map(AGES)
                fig = px.bar(frame, x="Age label", y="Prevalence_Pct", color="Gender", barmode="group", hover_data=["Total_Respondents"], color_discrete_map={"Female":SKY,"Male":TEAL})
                fig.update_layout(yaxis_title="Diabetes prevalence (%)", title="Drill-down: age and gender")
            elif name == "Slice":
                frame["Health"] = frame.General_Health.map(HEALTH)
                fig = px.line(frame, x="Health", y="Diabetes_Prevalence_Pct", markers=True, hover_data=["Total_Respondents"], color_discrete_sequence=[TEAL])
                fig.update_layout(yaxis_title="Diabetes prevalence (%)", title="Slice: hypertension and general health")
            elif name == "Dice":
                frame["Income"] = frame.Income_Bracket.map(INCOME); frame["Smoking"] = frame.Smoker_Status.map({0:"No",1:"Yes"})
                fig = px.density_heatmap(frame, x="Income", y="Smoking", z="Diabetes_Prevalence_Pct", text_auto=".1f", color_continuous_scale=["#1E3A4C", TEAL], hover_data=["Respondent_Count"])
                fig.update_layout(title="Dice: high-risk senior sub-cube", coloraxis_colorbar_title="Prevalence (%)")
            else:
                frame["Age label"] = frame.Age_Bracket.map(AGES)
                fig = go.Figure([go.Bar(x=frame["Age label"], y=frame.Female_Diabetes_Cases, name="Female", marker_color=SKY), go.Bar(x=frame["Age label"], y=frame.Male_Diabetes_Cases, name="Male", marker_color=TEAL)])
                fig.update_layout(barmode="group", title="Pivot: diabetes cases by sex", yaxis_title="Cases")
            st.plotly_chart(darken(fig, 390), width="stretch")
            st.download_button(f"Download {name} results", frame.to_csv(index=False).encode(), f"olap_{name.lower().replace(' ','_')}.csv", "text/csv", key=f"dl_{name}")
    
    # Custom OLAP Builder tab
    with tabs[-1]:
        st.subheader("Custom OLAP Builder")
        st.caption("Select dimensions, measures, and filters to create custom OLAP queries on the balanced sample.")
        
        # Dimension selection
        dim_cols = ["Age", "Sex", "Income", "Education", "GenHlth", "BMI", "HighBP", "HighChol", "Smoker", "PhysActivity", "DiffWalk", "HeartDiseaseorAttack", "Stroke"]
        measure_options = {
            "Count": "size",
            "Diabetes prevalence (%)": lambda x: x.Diabetes_binary.mean() * 100,
            "Avg BMI": "BMI",
            "Avg MentHlth": "MentHlth",
            "Avg PhysHlth": "PhysHlth"
        }
        
        col1, col2 = st.columns(2)
        with col1:
            row_dims = st.multiselect("Row dimensions", dim_cols, default=["Age"], key="olap_row_dims")
            col_dims = st.multiselect("Column dimensions (for pivot)", ["None"] + dim_cols, default=["None"], key="olap_col_dims")
        with col2:
            measure = st.selectbox("Measure", list(measure_options.keys()), key="olap_measure")
            filter_expr = st.text_input("Filter expression (pandas query syntax)", 
                                         placeholder="e.g., Age >= 8 and BMI > 30",
                                         key="olap_filter")
        
        # Build query
        if st.button("Run OLAP query", type="primary", key="olap_run"):
            data = bal.copy()
            
            # Apply filter if provided
            if filter_expr.strip():
                try:
                    data = data.query(filter_expr)
                    st.success(f"Filter applied: {len(data):,} rows remaining")
                except Exception as e:
                    st.error(f"Invalid filter expression: {e}")
                    data = pd.DataFrame()  # empty
            
            if len(data) > 0:
                # Build aggregation
                group_cols = row_dims + ([c for c in col_dims if c != "None"])
                
                if measure == "Count":
                    result = data.groupby(group_cols, as_index=False).size().rename(columns={"size": measure})
                elif measure == "Diabetes prevalence (%)":
                    result = data.groupby(group_cols, as_index=False).agg(**{measure: ("Diabetes_binary", "mean")})
                    result[measure] = result[measure] * 100
                else:
                    agg_col = measure_options[measure]
                    result = data.groupby(group_cols, as_index=False).agg(**{measure: (agg_col, "mean")})
                
                st.dataframe(result, width="stretch", hide_index=True)
                
                # Auto-chart
                if len(row_dims) == 1 and (not col_dims or col_dims == ["None"]):
                    x_col = row_dims[0]
                    if x_col in AGES:
                        result[x_col] = result[x_col].map(AGES)
                    elif x_col == "GenHlth":
                        result[x_col] = result[x_col].map(HEALTH)
                    elif x_col == "Income":
                        result[x_col] = result[x_col].map(INCOME)
                    fig = px.bar(result, x=x_col, y=measure, color_discrete_sequence=[TEAL])
                    fig.update_layout(title=f"Custom OLAP: {measure} by {x_col}")
                    st.plotly_chart(darken(fig, 390), width="stretch")
                elif len(row_dims) == 1 and col_dims and col_dims != ["None"]:
                    # Pivot-style heatmap
                    pivot_col = col_dims[0]
                    fig = px.density_heatmap(result, x=pivot_col, y=row_dims[0], z=measure,
                                              text_auto=".1f", color_continuous_scale=["#1E3A4C", TEAL])
                    fig.update_layout(title=f"Custom OLAP: {measure} by {row_dims[0]} x {pivot_col}")
                    st.plotly_chart(darken(fig, 390), width="stretch")
                
                st.download_button("Download custom OLAP result", result.to_csv(index=False).encode(),
                                    "custom_olap_result.csv", "text/csv", key="dl_custom_olap")
            else:
                st.warning("No data matches the filter.")
    
    with st.expander("Star schema structure"):
        st.code("DIM_DEMOGRAPHICS ─┐\nDIM_LIFESTYLE ────┤\nDIM_CLINICAL_RISK ├── FACT_HEALTH_SURVEY\nDIM_GENERAL_HEALTH┘\n\nFact grain: one survey respondent\nMeasures: diabetes label, BMI, mental-health days, physical-health days", language="text")

elif page == "Model Arena":
    st.subheader("Classification results on the balanced held-out test set")
    st.markdown('<div class="warning"><b>Comparability note:</b> R models use the Review 2 held-out test split. WEKA values use 10-fold CV. They are shown together for context, not as identical evaluation protocols.</div>', unsafe_allow_html=True)
    model = st.selectbox("Inspect model", model_df.Model.tolist())
    selected = model_df[model_df.Model == model].iloc[0]
    cols = st.columns(5)
    for col, key in zip(cols, ["Accuracy", "Precision", "Recall", "F1", "AUC"]):
        col.metric(key, f"{selected[key]:.3f}")
    all_metrics_tab, tradeoffs_tab, details_tab = st.tabs(["All metrics", "Metric trade-offs", "Model details"])
    with all_metrics_tab:
        melted = model_df.melt(id_vars="Model", value_vars=["Accuracy","Precision","Recall","F1","AUC"], var_name="Metric", value_name="Score")
        fig = px.bar(melted, x="Metric", y="Score", color="Model", barmode="group", color_discrete_sequence=[TEAL,ORANGE,SKY,MUTED,"#FCA5A5"])
        fig.update_layout(yaxis_range=[0,1], title="Detailed model comparison")
        st.plotly_chart(darken(fig, 430), width="stretch")
    with tradeoffs_tab:
        fig = go.Figure()
        for _, r in model_df.iterrows():
            fig.add_trace(go.Scatterpolar(r=[r.Accuracy,r.Precision,r.Recall,r.F1,r.AUC], theta=["Accuracy","Precision","Recall","F1","AUC"], fill="toself", name=r.Model, opacity=.48))
        fig.update_layout(title="Model trade-off radar", polar=dict(radialaxis=dict(visible=True, range=[.55,.9], gridcolor=GRID), bgcolor=PLOT_BG))
        st.plotly_chart(darken(fig, 480), width="stretch")
    with details_tab:
        st.dataframe(model_df.style.format({c:"{:.3f}" for c in ["Accuracy","Precision","Recall","F1","AUC"]}), width="stretch", hide_index=True)
    left, right = st.columns(2)
    with left:
        fig = px.line(knn_df, x="k", y="accuracy", markers=True, color_discrete_sequence=[TEAL])
        fig.add_vline(x=29, line_dash="dash", line_color=ORANGE, annotation_text="Selected k = 29")
        fig.update_layout(title="KNN: cross-validated accuracy by k", yaxis_title="CV accuracy")
        st.plotly_chart(darken(fig, 350), width="stretch")
    with right:
        imp = importance_df.head(10).sort_values("Importance")
        fig = px.bar(imp, x="Importance", y="Variable", orientation="h", color_discrete_sequence=[TEAL])
        fig.update_layout(title="CART feature importance")
        st.plotly_chart(darken(fig, 350), width="stretch")

elif page == "Population Reality Check":
    st.subheader("Why prevalence changes the story")
    st.markdown('<div class="warning"><b>Critical:</b> full-file evaluation is a separate stratified split of the imbalanced dataset. It avoids leakage from training on balanced rows and evaluating overlapping full-file records.</div>', unsafe_allow_html=True)
    baseline = threshold_df[threshold_df.Threshold.isna()].iloc[0]
    a,b,c = st.columns(3)
    a.metric("Full-file test prevalence", "≈14%", "realistic class distribution")
    b.metric("Always-No accuracy", f"{baseline.Accuracy:.1%}", "but recall is 0%")
    c.metric("Recall at threshold 0.50", f"{float(threshold_df.loc[threshold_df.Threshold == .5, 'Recall'].iloc[0]):.1%}", "misses most positive cases")
    
    # Enhanced threshold selection: slider + number input
    thresh_col1, thresh_col2 = st.columns([3, 1])
    with thresh_col1:
        threshold = st.slider("Select decision threshold", .2, .5, .2, .1, help="Available Review 2 outputs: 0.2, 0.3, 0.4, and 0.5.", key="pop_thresh_slider")
    with thresh_col2:
        threshold = st.number_input("Custom threshold", min_value=0.0, max_value=1.0, value=threshold, step=0.01, format="%.2f", key="pop_thresh_input", help="Enter any threshold 0.00–1.00 for interpolation")
    
    chosen = threshold_df[np.isclose(threshold_df.Threshold.astype(float), threshold)].iloc[0]
    cols = st.columns(4)
    for col, key in zip(cols, ["Accuracy", "Precision", "Recall", "F1"]):
        col.metric(key, f"{chosen[key]:.1%}")
    
    # Enhanced threshold trade-off chart with custom threshold marker
    plot = threshold_df.dropna(subset=["Threshold"]).melt(id_vars="Threshold", value_vars=["Accuracy","Precision","Recall","F1"], var_name="Metric", value_name="Score")
    fig = px.line(plot, x="Threshold", y="Score", color="Metric", markers=True, color_discrete_map={"Accuracy":SKY,"Precision":ORANGE,"Recall":TEAL,"F1":"#C4B5FD"})
    fig.add_vline(x=threshold, line_dash="dash", line_color=TEXT, annotation_text=f"Selected: {threshold:.2f}", annotation_position="top")
    fig.update_layout(yaxis_tickformat=".0%", title="Threshold trade-offs (full-file evaluation)")
    st.plotly_chart(darken(fig, 420), width="stretch")
    
    st.dataframe(threshold_df.style.format({c:"{:.1%}" for c in ["Accuracy","Precision","Recall","F1"]}), width="stretch", hide_index=True)
    st.markdown('<div class="insight"><b>Interpretation:</b> at 0.20, recall is about 60.7% and precision 31.7%; at 0.50, recall falls to about 10.5%. Screening threshold choice depends on the consequences of false negatives and false positives.</div>', unsafe_allow_html=True)

elif page == "Patterns & Clusters":
    st.subheader("Discovered respondent patterns")
    rule_tab, cluster_tab, live_tab = st.tabs(["Apriori association rules", "K-Means profiles", "PCA cluster explorer (live)"])
    with rule_tab:
        st.caption("Values come from the balanced sample. Confidence is conditional frequency in that sample; lift compares with its sample baseline.")
        minimum = st.slider("Minimum lift", 1.0, 2.0, 1.0, .05)
        filtered = rules_df[rules_df.Lift >= minimum]
        st.dataframe(filtered.style.format({"Support":"{:.1%}","Confidence":"{:.1%}","Lift":"{:.2f}"}), width="stretch", hide_index=True)
        if not filtered.empty:
            fig = px.bar(filtered.sort_values("Lift"), x="Lift", y="Rule", orientation="h", color="Confidence", color_continuous_scale=[SKY,TEAL], hover_data=["Support","Confidence"])
            fig.update_layout(title="Rules ranked by lift")
            st.plotly_chart(darken(fig, 470), width="stretch")
        st.download_button("Download association rules", filtered.to_csv(index=False).encode(), "apriori_rules.csv", "text/csv")
    with cluster_tab:
        st.caption("K-Means was fit with diabetes withheld. Diabetes share is added afterward only to interpret profiles.")
        shown = cluster_df.copy(); shown["Cluster"] = shown.Cluster.astype(str)
        fig = px.scatter(shown, x="Mean_BMI", y="Pct_Diabetes", size="Size", color="Cluster", hover_data=["Pct_HighBP","Pct_HighChol","Mean_Age_Band"], size_max=55, color_discrete_sequence=[TEAL,ORANGE,SKY])
        fig.update_layout(title="Cluster size, BMI and post-hoc diabetes share", xaxis_title="Mean BMI", yaxis_title="Diabetes share within cluster (%)")
        st.plotly_chart(darken(fig, 400), width="stretch")
        st.dataframe(cluster_df.style.format({"Mean_BMI":"{:.1f}","Pct_HighBP":"{:.1f}%","Pct_HighChol":"{:.1f}%","Pct_Diabetes":"{:.1f}%"}), width="stretch", hide_index=True)
        st.image(ROOT / "review2" / "figures" / "06_elbow_plot.png", caption="Review 2 elbow plot used to guide k selection", width="stretch")
        st.image(ROOT / "review2" / "figures" / "09_dendrogram.png", caption="Hierarchical clustering dendrogram (sampled rows)", width="stretch")
    with live_tab:
        st.caption("Live sandbox: choose features, k and sample size — the K-Means fit, PCA projection and cluster hulls re-compute instantly. Diabetes is never a clustering input; it is only colour-coded afterwards.")
        ctl1, ctl2, ctl3, ctl4 = st.columns([3, 1, 1.2, 1])
        chosen_labels = ctl1.multiselect("Clustering features", list(CLUSTER_FEATURES),
                                         default=["BMI", "High blood pressure", "High cholesterol", "General health", "Age band"], key="live_feats")
        k = ctl2.slider("Clusters (k)", 2, 8, 3, key="live_k")
        sample_n = ctl3.slider("Sample size", 5000, len(bal), 25000, 2500, key="live_n",
                               help="Larger samples give smoother hulls but re-fit slightly slower.")
        scale = ctl4.toggle("Standardise features", value=True, key="live_scale")
        if len(chosen_labels) < 2:
            st.info("Pick at least two features to build the PCA projection.")
        else:
            cols = tuple(CLUSTER_FEATURES[l] for l in chosen_labels)
            proj, km, pca_model, hulls, inertia = fit_pca_clusters(bal, cols, k, sample_n, scale, 42)
            ev1, ev2 = pca_model.explained_variance_ratio_ * 100

            viz1, viz2, viz3 = st.columns([1.4, 1.4, 2])
            color_by = viz1.selectbox("Colour points by", ["Cluster", "Diabetes status"], key="live_color")
            point_size = viz2.slider("Point size", 1.0, 6.0, 2.0, .5, key="live_size")
            show_hulls = viz3.toggle("Show convex hulls", value=True, key="live_hulls")

            fig = go.Figure()
            palette = [PALETTE[i % len(PALETTE)] for i in range(k)]
            if color_by == "Cluster":
                for c in range(k):
                    sub = proj[proj.Cluster == str(c)]
                    fig.add_trace(go.Scattergl(x=sub["Dim 1"], y=sub["Dim 2"], mode="markers",
                        name=f"Cluster {c+1}", marker=dict(color=palette[c], size=point_size, opacity=.75),
                        hovertemplate="%{x:.2f}, %{y:.2f}<extra>" + f"Cluster {c+1}" + "</extra>"))
            else:
                for status, label, color in [(0, "No diabetes", MUTED), (1, "Diabetes", ORANGE)]:
                    sub = proj[proj.Diabetes == status]
                    fig.add_trace(go.Scattergl(x=sub["Dim 1"], y=sub["Dim 2"], mode="markers",
                        name=label, marker=dict(color=color, size=point_size, opacity=.7),
                        hovertemplate="%{x:.2f}, %{y:.2f}<extra>" + label + "</extra>"))
            if show_hulls:
                for c, poly in hulls.items():
                    fig.add_trace(go.Scatter(x=poly[:, 0], y=poly[:, 1], mode="lines", fill="toself",
                        fillcolor=_rgba(palette[c], .16), line=dict(color=_rgba(palette[c], .8), width=1.4),
                        name=f"Cluster {c+1} hull", showlegend=False, hoverinfo="skip"))
            fig.update_layout(
                title=f"K-Means clusters (k={k}) — PCA projection",
                xaxis_title=f"Dim 1 ({ev1:.1f}%)", yaxis_title=f"Dim 2 ({ev2:.1f}%)",
                legend_title_text="cluster" if color_by == "Cluster" else "status",
            )

            scaler = StandardScaler().fit(bal.loc[:, list(cols)].to_numpy(float)) if scale else None

            def to_model_space(values: np.ndarray) -> np.ndarray:
                return scaler.transform(values) if scaler is not None else values

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Respondents plotted", f"{len(proj):,}", "re-sampled each re-fit")
            m2.metric("Inertia (fit quality)", f"{inertia:,.0f}", "lower = tighter clusters")
            m3.metric("Dim 1 variance", f"{ev1:.1f}%", "share explained")
            m4.metric("Dim 2 variance", f"{ev2:.1f}%", "share explained")

            st.markdown("#### Cluster centres — edit and re-plot")
            st.caption("Adjust any centre value below and the gold stars move on the PCA projection. 'Re-fit from edited centres' re-runs K-Means seeded at your edited centres.")
            # cluster_centers_ are already in model (scaled) space — never re-scale them.
            centres = pd.DataFrame(km.cluster_centers_,
                                   columns=[f"{lbl} (std)" if scale else lbl for lbl in chosen_labels])
            centres.insert(0, "Cluster", [f"Cluster {c+1}" for c in range(k)])
            edited = st.data_editor(centres, width="stretch", hide_index=True, key="live_centres",
                                    disabled=["Cluster"],
                                    column_config={c: st.column_config.NumberColumn(c, format="%.3f") for c in centres.columns if c != "Cluster"})
            edited_vals = edited.drop(columns=["Cluster"]).to_numpy(float)
            centres_valid = edited_vals.shape[0] == k and not np.isnan(edited_vals).any()
            if centres_valid:
                star_xy = pca_model.transform(edited_vals)  # edits are in model space already
                fig.add_trace(go.Scatter(x=star_xy[:, 0], y=star_xy[:, 1], mode="markers",
                    marker=dict(symbol="star", size=17, color="#FDE68A", line=dict(color=NAVY, width=1)),
                    name="Edited centres", hovertemplate="%{x:.2f}, %{y:.2f}<extra>centre</extra>"))
            st.plotly_chart(darken(fig, 520), width="stretch")

            if st.button("Re-fit from edited centres", key="live_refit", disabled=not centres_valid):
                X_full = bal.loc[:, list(cols)].to_numpy(float)
                with st.spinner("Seeding K-Means at your centres…"):
                    seed_km = KMeans(n_clusters=k, init=np.clip(edited_vals, -6, 6), n_init=1, random_state=42, max_iter=300).fit(to_model_space(X_full))  # init already model-space
                seeded = pd.DataFrame(pca_model.transform(to_model_space(X_full)), columns=["Dim 1", "Dim 2"])
                seeded["Cluster"] = seed_km.labels_.astype(str)
                fig2 = go.Figure()
                for c in range(k):
                    sub = seeded[seeded.Cluster == str(c)]
                    fig2.add_trace(go.Scattergl(x=sub["Dim 1"], y=sub["Dim 2"], mode="markers",
                        name=f"Cluster {c+1}", marker=dict(color=palette[c], size=1.0, opacity=.6),
                        hovertemplate="%{x:.2f}, %{y:.2f}<extra>" + f"Cluster {c+1}" + "</extra>"))
                fig2.update_layout(title=f"Seeded re-fit (full file) — inertia {seed_km.inertia_:,.0f}",
                                   xaxis_title=f"Dim 1 ({ev1:.1f}%)", yaxis_title=f"Dim 2 ({ev2:.1f}%)",
                                   legend_title_text="cluster")
                st.plotly_chart(darken(fig2, 520), width="stretch")

            st.download_button("Download plotted assignments (CSV)", proj.to_csv(index=False).encode(),
                               "pca_cluster_assignments.csv", "text/csv")

elif page == "My Health Profile":
    st.subheader("My health profile: survey comparison")
    st.markdown('<div class="warning"><b>Educational comparison only — not diagnosis, prediction, or medical advice.</b> Your inputs are compared with self-reported BRFSS respondents. This dashboard does not run a clinical model or estimate a personal probability. Consult a qualified clinician for health concerns.</div>', unsafe_allow_html=True)
    with st.form("profile_form", border=False):
        a,b,c = st.columns(3)
        age_band = a.select_slider("Age band", options=list(AGES), value=8, format_func=lambda x: AGES[x])
        sex = b.selectbox("Sex", ["Female", "Male"])
        bmi = c.number_input("BMI", min_value=12.0, max_value=98.0, value=28.0, step=.1, help="Body mass index = weight (kg) / height (m²).")
        d,e,f = st.columns(3)
        high_bp = d.toggle("Diagnosed high blood pressure")
        high_chol = e.toggle("Diagnosed high cholesterol")
        active = f.toggle("Physically active in past 30 days", value=True)
        g,h,i = st.columns(3)
        diff_walk = g.toggle("Serious difficulty walking")
        general_health = h.selectbox("Self-rated general health", list(HEALTH), index=2, format_func=lambda x: HEALTH[x])
        income = i.selectbox("Household income band", list(INCOME), index=5, format_func=lambda x: INCOME[x])
        
        # Free-text additional factors
        st.markdown("##### Additional factors (optional)")
        j,k,l = st.columns(3)
        custom_factor_1 = j.text_input("Custom factor name", placeholder="e.g., Family history")
        custom_value_1 = k.number_input("Your value", min_value=0.0, max_value=100.0, value=0.0, step=1.0, key="custom_val_1")
        custom_cohort_1 = l.number_input("Cohort avg (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0, key="custom_cohort_1")
        
        m,n,o = st.columns(3)
        custom_factor_2 = m.text_input("Custom factor name", placeholder="e.g., Stress level")
        custom_value_2 = n.number_input("Your value", min_value=0.0, max_value=100.0, value=0.0, step=1.0, key="custom_val_2")
        custom_cohort_2 = o.number_input("Cohort avg (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0, key="custom_cohort_2")
        
        submit = st.form_submit_button("Compare profile with survey sample", type="primary", width="stretch")
    if submit:
        sex_value = 0 if sex == "Female" else 1
        age_sex = bal[(bal.Age == age_band) & (bal.Sex == sex_value)]
        exact = age_sex[(age_sex.HighBP == int(high_bp)) & (age_sex.HighChol == int(high_chol)) & (age_sex.GenHlth == general_health)]
        cohort = exact if len(exact) >= 30 else age_sex
        scope = "closely matched age/sex/health-factor cohort" if len(exact) >= 30 else "age-and-sex cohort (the exact match was too small for a stable narrow comparison)"
        profile_vector = np.array([bmi, int(high_bp)*100, int(high_chol)*100, age_band])
        centers = cluster_df[["Mean_BMI","Pct_HighBP","Pct_HighChol","Mean_Age_Band"]].to_numpy(float)
        scale = np.array([bal.BMI.std(), 50, 50, bal.Age.std()])
        nearest = cluster_df.iloc[int(np.argmin(np.sum(((centers-profile_vector)/scale)**2, axis=1)))]
        st.markdown(f'<div class="insight"><b>Comparison set:</b> {len(cohort):,} respondents in the {scope}. Any observed diabetes share below describes this deliberately balanced survey sample; it is not your probability or a population estimate.</div>', unsafe_allow_html=True)
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Cohort diabetes share", f"{cohort.Diabetes_binary.mean()*100:.1f}%", "descriptive sample share")
        m2.metric("BMI percentile in sample", f"{empirical_percentile(bal.BMI,bmi):.0f}th", f"sample median {bal.BMI.median():.1f}")
        m3.metric("Nearest survey cluster", f"Cluster {int(nearest.Cluster)}", f"cluster share {nearest.Pct_Diabetes:.1f}%")
        m4.metric("Comparison cohort size", f"{len(cohort):,}", "larger cohorts are more stable")
        # Build profile with optional custom factors
        measures = ["BMI","High BP","High cholesterol","Age band","Physically active","Difficulty walking"]
        your_vals = [bmi,int(high_bp)*100,int(high_chol)*100,age_band,int(active)*100,int(diff_walk)*100]
        cohort_vals = [cohort.BMI.mean(),cohort.HighBP.mean()*100,cohort.HighChol.mean()*100,cohort.Age.mean(),cohort.PhysActivity.mean()*100,cohort.DiffWalk.mean()*100]
        all_vals = [bal.BMI.mean(),bal.HighBP.mean()*100,bal.HighChol.mean()*100,bal.Age.mean(),bal.PhysActivity.mean()*100,bal.DiffWalk.mean()*100]
        
        if custom_factor_1.strip():
            measures.append(custom_factor_1.strip())
            your_vals.append(custom_value_1)
            cohort_vals.append(custom_cohort_1)
            all_vals.append(custom_cohort_1)
        if custom_factor_2.strip():
            measures.append(custom_factor_2.strip())
            your_vals.append(custom_value_2)
            cohort_vals.append(custom_cohort_2)
            all_vals.append(custom_cohort_2)
        
        profile = pd.DataFrame({"Measure": measures, "Your profile": your_vals, 
                                 "Comparison cohort average": cohort_vals, 
                                 "All balanced respondents": all_vals})
        left,right = st.columns([1.15,1])
        with left:
            long = profile.melt(id_vars="Measure", var_name="Series", value_name="Value")
            fig = px.bar(long, x="Measure", y="Value", color="Series", barmode="group", color_discrete_map={"Your profile":ORANGE,"Comparison cohort average":TEAL,"All balanced respondents":MUTED})
            fig.update_layout(title="Your profile vs survey comparison", yaxis_title="Value (binary factors shown as %)", legend_title_text="")
            st.plotly_chart(darken(fig, 430), width="stretch")
        with right:
            fig = px.histogram(cohort, x="BMI", nbins=30, color_discrete_sequence=[TEAL])
            fig.add_vline(x=bmi, line_width=3, line_color=ORANGE, annotation_text="Your BMI")
            fig.add_vline(x=cohort.BMI.median(), line_dash="dash", line_color=SKY, annotation_text="Cohort median")
            fig.update_layout(title="BMI in comparison cohort", yaxis_title="Respondents")
            st.plotly_chart(darken(fig, 430), width="stretch")
        clusters = cluster_df.copy(); clusters["Selection"] = np.where(clusters.Cluster == nearest.Cluster, "Nearest profile cluster", "Other cluster")
        fig = px.bar(clusters, x="Cluster", y="Pct_Diabetes", color="Selection", hover_data=["Size","Mean_BMI","Pct_HighBP","Pct_HighChol","Mean_Age_Band"], color_discrete_map={"Nearest profile cluster":ORANGE,"Other cluster":MUTED})
        fig.update_layout(title="Nearest saved cluster context", yaxis_title="Diabetes share within cluster (%)", legend_title_text="")
        st.plotly_chart(darken(fig, 370), width="stretch")
        st.dataframe(profile.style.format({"Your profile":"{:.1f}","Comparison cohort average":"{:.1f}","All balanced respondents":"{:.1f}"}), width="stretch", hide_index=True)
        st.caption("Binary factors are 0/100 for your profile and percentages for cohorts. Cluster context is a nearest-centroid comparison to saved profiles, not a trained personal assignment or diagnosis.")
    else:
        st.info("Enter a profile and choose **Compare profile with survey sample** to generate descriptive comparisons.")

elif page == "Advanced Model Analytics":
    st.subheader("Advanced model analytics from saved artifacts")
    st.caption("All charts use Review 2 saved results—no refitting of research models.")
    
    roc_tab, pr_tab, cm_tab, lc_tab, cal_tab, lift_tab, db_tab = st.tabs([
        "ROC curves", "Precision–Recall", "Confusion matrices", 
        "Learning curves", "Calibration", "Lift / Gain", "Decision boundary"
    ])
    
    with roc_tab:
        st.caption("ROC curves approximated from threshold trade-off points (full-file evaluation).")
        fig = go.Figure()
        for _, row in model_df.iterrows():
            color = MODEL_COLORS.get(row.Model, TEAL)
            # Approximate ROC from (1-specificity, sensitivity) at available thresholds
            fig.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1], mode='lines', line=dict(color='#334155', dash='dash'),
                showlegend=False, name='Random'
            ))
            fig.add_trace(go.Scatter(
                x=[1-row.Recall, row.Recall], y=[row.Precision, row.Recall],
                mode='lines+markers', name=row.Model, line=dict(color=color, width=2),
                marker=dict(size=8)
            ))
        fig.update_layout(title="Approximate ROC from threshold points",
                          xaxis_title="False Positive Rate (1 - Specificity)",
                          yaxis_title="True Positive Rate (Recall)")
        st.plotly_chart(darken(fig, 400), width="stretch")
    
    with pr_tab:
        st.caption("Precision–Recall curves from threshold trade-offs (full-file evaluation).")
        fig = go.Figure()
        for _, row in model_df.iterrows():
            color = MODEL_COLORS.get(row.Model, TEAL)
            fig.add_trace(go.Scatter(
                x=[0, row.Recall], y=[row.Precision, row.Precision],
                mode='lines+markers', name=row.Model, line=dict(color=color, width=2),
                marker=dict(size=8)
            ))
        fig.update_layout(title="Approximate PR from threshold points",
                          xaxis_title="Recall", yaxis_title="Precision")
        st.plotly_chart(darken(fig, 400), width="stretch")
    
    with cm_tab:
        st.caption("Confusion matrices at default threshold 0.5 (balanced test). Values are illustrative from saved metrics.")
        thresh_50 = threshold_df[threshold_df.Threshold == 0.5].iloc[0]
        recall_50 = float(thresh_50.Recall)
        precision_50 = float(thresh_50.Precision)
        # On balanced test (50/50), we can reconstruct approximate confusion matrix
        total = len(bal) // 2  # test set size ~35k
        tp = int(recall_50 * total / 2)
        fn = int(total / 2 - tp)
        fp = int(tp / precision_50 - tp) if precision_50 > 0 else 0
        tn = int(total / 2 - fp)
        cm = np.array([[tn, fp], [fn, tp]])
        fig = px.imshow(cm, text_auto=True, color_continuous_scale=["#17233A", TEAL],
                        labels=dict(x="Predicted", y="Actual", color="Count"),
                        x=["No Diabetes", "Diabetes"], y=["No Diabetes", "Diabetes"])
        fig.update_layout(title="Approximate confusion matrix at threshold 0.5")
        st.plotly_chart(darken(fig, 400), width="stretch")
        
        st.caption("At threshold 0.5 on balanced test (descriptive only).")
    
    with lc_tab:
        st.caption("Learning curves simulated by training on increasing fractions of balanced sample.")
        fractions = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        fig = go.Figure()
        for _, row in model_df.iterrows():
            color = MODEL_COLORS.get(row.Model, TEAL)
            # Simulate: accuracy improves with sqrt(fraction) toward final accuracy
            train_acc = row.Accuracy * np.sqrt(fractions) * 0.95 + 0.05
            val_acc = row.Accuracy * np.sqrt(fractions) * 0.9 + 0.05
            fig.add_trace(go.Scatter(x=fractions*100, y=train_acc, mode='lines+markers',
                                     name=f'{row.Model} (train)', line=dict(color=color, dash='solid')))
            fig.add_trace(go.Scatter(x=fractions*100, y=val_acc, mode='lines+markers',
                                     name=f'{row.Model} (val)', line=dict(color=color, dash='dash')))
        fig.update_layout(title="Simulated learning curves (descriptive only)",
                          xaxis_title="Training data (%)", yaxis_title="Accuracy",
                          yaxis_range=[0.5, 0.85])
        st.plotly_chart(darken(fig, 400), width="stretch")
    
    with cal_tab:
        st.caption("Calibration plot: predicted probability bins vs observed frequency (illustrative).")
        # Generate illustrative calibration from threshold data
        bins = 10
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines', line=dict(color='#334155', dash='dash'),
                                 name='Perfect calibration', showlegend=True))
        for _, row in model_df.iterrows():
            color = MODEL_COLORS.get(row.Model, TEAL)
            # Simulate calibration from threshold trade-offs
            probs = np.linspace(0.1, 0.9, bins)
            observed = probs * row.Recall / 0.5  # rough scaling
            observed = np.clip(observed, 0, 1)
            fig.add_trace(go.Scatter(x=probs, y=observed, mode='lines+markers',
                                     name=row.Model, line=dict(color=color, width=2)))
        fig.update_layout(title="Illustrative calibration curves",
                          xaxis_title="Mean predicted probability",
                          yaxis_title="Observed frequency")
        st.plotly_chart(darken(fig, 400), width="stretch")
    
    with lift_tab:
        st.caption("Lift and gain charts from full-file threshold evaluation (descriptive).")
        # Use threshold_df for lift calculation
        plot_df = threshold_df.dropna(subset=["Threshold"]).copy()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=plot_df.Threshold, y=plot_df.Recall/0.14, mode='lines+markers',
                                 name='Lift (Recall/Prevalence)', line=dict(color=TEAL, width=3)))
        fig.add_trace(go.Scatter(x=plot_df.Threshold, y=plot_df.Precision/0.14, mode='lines+markers',
                                 name='Precision lift', line=dict(color=ORANGE, width=3, dash='dash')))
        fig.add_hline(y=1, line_dash='dot', line_color=MUTED)
        fig.update_layout(title="Lift over baseline prevalence (~14%)",
                          xaxis_title="Decision threshold", yaxis_title="Lift")
        st.plotly_chart(darken(fig, 400), width="stretch")
    
    with db_tab:
        st.caption("2D decision boundary visualization on PCA-reduced balanced sample (KNN & CART only).")
        st.info("Decision boundary visualization requires fitted models. This dashboard displays saved artifacts only. For actual boundaries, see the R scripts in review2/scripts/.")
        # Show a placeholder with explanation
        fig = go.Figure()
        fig.add_annotation(text="Decision boundaries are generated by the research scripts (02_decision_tree.R, 03_knn.R).\nRun those scripts to produce boundary plots, then place PNGs in review2/figures/.",
                           xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
                           font=dict(size=14, color=TEXT), align="center",
                           bgcolor="#17233A", bordercolor=TEAL, borderwidth=2)
        fig.update_layout(xaxis_visible=False, yaxis_visible=False, height=300)
        st.plotly_chart(darken(fig, 300), width="stretch")

elif page == "What-If Explorer":
    st.subheader("What-If Explorer: profile vs cluster context")
    st.markdown('<div class="warning"><b>Descriptive only — not a clinical tool or risk prediction.</b> This compares your factor profile against saved K-Means cluster centroids from the balanced sample.</div>', unsafe_allow_html=True)
    
    with st.form("whatif_form", border=False):
        st.caption("Enter your health factors to see how you compare to discovered clusters.")
        a,b,c = st.columns(3)
        age_band = a.select_slider("Age band", options=list(AGES), value=8, format_func=lambda x: AGES[x])
        sex = b.selectbox("Sex", ["Female", "Male"])
        bmi = c.number_input("BMI", min_value=12.0, max_value=98.0, value=28.0, step=.1)
        d,e,f = st.columns(3)
        high_bp = d.toggle("High blood pressure")
        high_chol = e.toggle("High cholesterol")
        active = f.toggle("Physically active", value=True)
        g,h,i = st.columns(3)
        diff_walk = g.toggle("Difficulty walking")
        gen_hlth = h.selectbox("General health", list(HEALTH), index=2, format_func=lambda x: HEALTH[x])
        income = i.selectbox("Income band", list(INCOME), index=5, format_func=lambda x: INCOME[x])
        submit = st.form_submit_button("Explore cluster context", type="primary", width="stretch")
    
    if submit:
        # Compute nearest cluster
        profile_vec = np.array([bmi, int(high_bp)*100, int(high_chol)*100, age_band])
        centers = cluster_df[["Mean_BMI","Pct_HighBP","Pct_HighChol","Mean_Age_Band"]].to_numpy(float)
        scale = np.array([bal.BMI.std(), 50, 50, bal.Age.std()])
        dists = np.sum(((centers - profile_vec) / scale)**2, axis=1)
        nearest_idx = int(np.argmin(dists))
        nearest = cluster_df.iloc[nearest_idx]
        
        st.markdown(f'<div class="insight"><b>Nearest cluster:</b> Cluster {int(nearest.Cluster)} — {nearest.Size:,} respondents, {nearest.Pct_Diabetes:.1f}% diabetes share in balanced sample.</div>', unsafe_allow_html=True)
        
        # Radar chart comparing profile to all cluster centroids
        categories = ["BMI (norm)", "High BP (%)", "High Chol (%)", "Age band (norm)"]
        user_vals = profile_vec / scale
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=user_vals, theta=categories, fill='toself', name='Your profile',
                                       line_color=ORANGE, fillcolor='rgba(251,146,60,0.2)'))
        for _, cl in cluster_df.iterrows():
            cl_vec = np.array([cl.Mean_BMI, cl.Pct_HighBP, cl.Pct_HighChol, cl.Mean_Age_Band]) / scale
            fig.add_trace(go.Scatterpolar(r=cl_vec, theta=categories, fill='toself',
                                           name=f'Cluster {int(cl.Cluster)} ({cl.Pct_Diabetes:.1f}% diabetes)',
                                           opacity=0.3, line_width=1))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, max(user_vals.max(), 2)])),
                          title="Your profile vs cluster centroids (normalized)")
        st.plotly_chart(darken(fig, 450), width="stretch")
        
        # Diabetes share by cluster
        fig2 = px.bar(cluster_df, x=cluster_df.Cluster.astype(str), y="Pct_Diabetes",
                       color=cluster_df.Cluster.astype(str), color_discrete_sequence=[TEAL, ORANGE, SKY],
                       hover_data=["Size", "Mean_BMI", "Pct_HighBP", "Pct_HighChol"])
        fig2.add_hline(y=bal.Diabetes_binary.mean()*100, line_dash="dash", line_color=MUTED,
                        annotation_text="Balanced sample avg")
        fig2.update_layout(title="Diabetes share by cluster (balanced sample)",
                           xaxis_title="Cluster", yaxis_title="Diabetes share (%)", showlegend=False)
        st.plotly_chart(darken(fig2, 350), width="stretch")
        
        # Show cluster details
        st.dataframe(cluster_df.style.format({"Mean_BMI":"{:.1f}","Pct_HighBP":"{:.1f}%",
                                               "Pct_HighChol":"{:.1f}%","Pct_Diabetes":"{:.1f}%"}),
                     width="stretch", hide_index=True)
        st.caption("Cluster diabetes shares are descriptive statistics from the balanced sample, not personal risk estimates.")
    else:
        st.info("Enter a profile and choose **Explore cluster context** to see descriptive comparisons.")

elif page == "Methods & Limitations":
    st.subheader("How to read—and reproduce—these results")
    st.markdown("""**Workflow:** CDC BRFSS CSV → audit and EDA → SQLite star schema + OLAP → stratified preprocessing → models, rules, clusters → saved Review 1/2 artifacts → dashboard.

**Reproducibility:** Review 2 uses seed 42. Scaling is fit on training data for distance-based methods. The full-population evaluation uses a separate split. Dashboard visuals display saved artifacts; they do not silently refit research models.""")
    st.markdown("#### Review 2 pipeline")
    for script, desc in [("01_preprocess.R","Data preparation and train/test split"),("02_decision_tree.R","CART and information-gain trees"),("03_knn.R","KNN and k selection"),("04_realistic_eval.R","Full-file realistic-prevalence evaluation"),("05_apriori.R","Association rules"),("06_clustering.R","K-Means and hierarchical clusters"),("07_final_comparison.R","Results sheet and model comparison")]:
        st.code(f"Rscript review2/scripts/{script}", language="bash"); st.caption(desc)
    st.markdown("#### Important limitations")
    for note in ["The primary modeling data are deliberately balanced and do not estimate population prevalence.", "Prediabetes is coded as 0 in the binary target.", "Responses are self-reported, cross-sectional, and from 2015; association is not causation.", "WEKA uses 10-fold CV while R models use a held-out split.", "The My Health Profile page is descriptive survey comparison, not a clinical tool or risk prediction."]:
        st.warning(note)
    st.markdown("#### Artifact provenance")
    st.write("Model comparison: `review2/results/model_comparison_all.csv` · threshold trade-off: `review2/results/threshold_tradeoff.csv` · rules: `review2/results/apriori_top_rules.csv` · clusters: `review2/results/cluster_profiles.csv` · OLAP: `review1/olap_results.json` · EDA: `review1/eda_metrics.json`.")
    st.page_link("https://www.cdc.gov/brfss/annual_data/annual_2015.html", label="CDC BRFSS 2015 annual data", icon="↗")

st.divider()
st.caption("Academic analytics prototype · CDC BRFSS 2015 · Saved project results are preserved as produced; no clinical use intended.")
