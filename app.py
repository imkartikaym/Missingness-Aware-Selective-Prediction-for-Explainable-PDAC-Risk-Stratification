from __future__ import annotations

from pathlib import Path
import re
import io
import json
import math
import html

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# PDAC-GUARD | Research dashboard
# This dashboard summarizes project evaluation outputs and audits uploaded
# datasets. It deliberately does not produce clinical predictions because no
# verified serialized model artifact is distributed with this frontend.
# -----------------------------------------------------------------------------

APP_DIR = Path(__file__).resolve().parent
TABLE_DIR = APP_DIR / "data" / "tables"
FIGURE_DIR = APP_DIR / "data" / "figures"

st.set_page_config(
    page_title="PDAC-GUARD | Research Workspace",
    page_icon=str(APP_DIR / "assets" / "pdac_guard_mark.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

# Theme-aligned design system
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
      :root {
        --ink:#172A3A; --muted:#66788A; --line:#DFE7EF; --paper:#FFFFFF;
        --canvas:#F5F8FC; --teal:#287D8E; --teal2:#44A3A8; --blue:#4467C4;
        --green:#26856B; --amber:#B7791F; --red:#B74755;
      }
      html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
      .stApp { background:var(--canvas); }
      [data-testid="stHeader"] { background:rgba(245,248,252,0.90); }
      [data-testid="stSidebar"] { background:#101E2C; border-right:1px solid #203447; }
      [data-testid="stSidebar"] * { color:#E9F1F7; }
      [data-testid="stSidebar"] [data-testid="stRadio"] label { border-radius:10px; padding:7px 10px; }
      [data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#203447; }
      [data-testid="stSidebar"] hr { border-color:#2A3E50; }
      .block-container { padding-top:1.45rem; padding-bottom:3rem; max-width:1480px; }
      h1,h2,h3 { font-family:'Manrope','DM Sans',sans-serif; letter-spacing:-0.035em; color:var(--ink); }
      h1 { font-weight:800; }
      h2 { font-weight:750; margin-top:0.4rem; }
      h3 { font-weight:700; }
      p, li { color:#415569; }
      [data-testid="stMetric"] { background:var(--paper); border:1px solid var(--line); padding:17px 18px; border-radius:16px; box-shadow:0 4px 16px rgba(29,54,75,0.035); }
      [data-testid="stMetricLabel"] { color:#687B8C; font-size:0.83rem; }
      [data-testid="stMetricValue"] { color:var(--ink); font-family:'Manrope',sans-serif; font-weight:800; }
      [data-testid="stMetricDelta"] { font-size:0.78rem; }
      [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
      [data-testid="stPlotlyChart"] { border:1px solid var(--line); border-radius:16px; background:#fff; padding:7px; }
      .brand { display:flex; align-items:center; gap:11px; margin:2px 0 20px 0; }
      .brand-mark { width:38px; height:38px; border-radius:12px; background:linear-gradient(140deg,#48B7AF,#3676B9); display:flex; align-items:center; justify-content:center; color:white; font-weight:800; font-family:'Manrope',sans-serif; box-shadow:0 6px 18px rgba(46,146,164,.27); }
      .brand-name { font:800 18px 'Manrope',sans-serif; color:#F7FBFF; letter-spacing:-.04em; line-height:1.15; }
      .brand-sub { color:#8FA7B9; font-size:10px; letter-spacing:.16em; text-transform:uppercase; margin-top:4px; }
      .side-label { color:#8097A8 !important; text-transform:uppercase; font-size:10px; letter-spacing:.16em; font-weight:700; margin:18px 0 8px 2px; }
      .hero { background:linear-gradient(122deg,#142B3D 0%,#1D4E64 59%,#287D8E 100%); border-radius:22px; padding:30px 32px; color:white; position:relative; overflow:hidden; border:1px solid rgba(255,255,255,.1); box-shadow:0 12px 35px rgba(24,58,78,.13); }
      .hero:after { content:''; position:absolute; right:-40px; top:-110px; width:340px; height:340px; border:1px solid rgba(255,255,255,.15); border-radius:50%; box-shadow:0 0 0 40px rgba(255,255,255,.035),0 0 0 82px rgba(255,255,255,.025); }
      .hero-kicker { font-size:11px; font-weight:700; letter-spacing:.19em; color:#BCEAE7; text-transform:uppercase; margin-bottom:12px; position:relative; z-index:1; }
      .hero-title { color:#FFFFFF; font:800 clamp(28px,3.5vw,42px)/1.09 'Manrope',sans-serif; letter-spacing:-.055em; max-width:760px; position:relative; z-index:1; }
      .hero-copy { color:#D7E9F0; font-size:14px; line-height:1.65; max-width:710px; margin-top:15px; position:relative; z-index:1; }
      .hero-foot { display:flex; flex-wrap:wrap; gap:8px; margin-top:20px; position:relative; z-index:1; }
      .pill { border:1px solid rgba(220,244,248,.24); background:rgba(255,255,255,.075); color:#E9F7F8; border-radius:999px; padding:6px 11px; font-size:11px; font-weight:600; }
      .section-head { display:flex; align-items:flex-end; justify-content:space-between; gap:12px; margin:26px 0 12px 0; }
      .section-title { color:var(--ink); font:750 20px 'Manrope',sans-serif; letter-spacing:-.035em; }
      .section-caption { color:var(--muted); font-size:12px; margin-top:4px; }
      .panel { background:#FFFFFF; border:1px solid var(--line); border-radius:16px; padding:19px 20px; box-shadow:0 4px 16px rgba(29,54,75,.025); height:100%; }
      .panel-label { color:#6D8091; font-size:11px; font-weight:700; letter-spacing:.11em; text-transform:uppercase; }
      .panel-value { color:var(--ink); font:800 27px 'Manrope',sans-serif; letter-spacing:-.05em; margin-top:9px; }
      .panel-note { color:#78899A; font-size:12px; line-height:1.5; margin-top:6px; }
      .status { display:inline-flex; align-items:center; gap:7px; border-radius:999px; padding:6px 10px; font-size:11px; font-weight:700; }
      .status-dot { width:6px; height:6px; border-radius:50%; background:currentColor; display:inline-block; }
      .status-blue { background:#E8F1FA; color:#365F92; }
      .status-green { background:#E5F5EF; color:#23785D; }
      .status-amber { background:#FFF4DF; color:#9A650F; }
      .status-red { background:#FCEBED; color:#A33A47; }
      .callout { border:1px solid #D8E8EC; background:#F0F8F9; padding:14px 16px; border-radius:13px; color:#345765; font-size:13px; line-height:1.6; }
      .callout.warning { background:#FFF8E9; border-color:#F2E1B8; color:#75551C; }
      .callout.danger { background:#FFF0F1; border-color:#F4CDD1; color:#853D45; }
      .callout.success { background:#EDF8F3; border-color:#CFEBDD; color:#28684F; }
      .mini-kicker { font-size:10px; letter-spacing:.16em; color:#92D8D6; text-transform:uppercase; font-weight:700; }
      .muted-small { color:#768797; font-size:11px; }
      .footer { border-top:1px solid var(--line); padding-top:17px; margin-top:38px; color:#8091A0; font-size:11px; display:flex; justify-content:space-between; gap:14px; flex-wrap:wrap; }
      .stButton button { border-radius:10px; font-weight:700; }
      .stDownloadButton button { border-radius:10px; font-weight:700; }
      [data-testid="stForm"] { background:white; border:1px solid var(--line); border-radius:16px; padding:18px; }
      div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input { border-radius:10px; }
      @media (max-width: 768px) { .hero { padding:22px; } .hero-title {font-size:28px;} .block-container {padding-left:1rem;padding-right:1rem;} }
    </style>
    """,
    unsafe_allow_html=True,
)

PALETTE = {
    "navy": "#203B50",
    "teal": "#287D8E",
    "aqua": "#44A3A8",
    "blue": "#4467C4",
    "purple": "#8B77C7",
    "green": "#26856B",
    "amber": "#B7791F",
    "red": "#B74755",
    "muted": "#718396",
}


def load_table(filename: str) -> pd.DataFrame:
    path = TABLE_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


BASELINE = load_table("baseline_model_metrics.csv")
STRESS = load_table("step4_missingness_scenario_metrics.csv")
REPEATED = load_table("random_masking_stress_results.csv")
GROUP_METRICS = load_table("group_heldout_metrics_all_models.csv")
CALIBRATION = load_table("canonical_step12_calibration_uncertainty.csv")
MISS_BY_GROUP = load_table("ca19_missingness_by_group_and_class.csv")
MISS_TESTS = load_table("ca19_missingness_inference.csv")
COHORT_COMPOSITION = load_table("cohort_composition.csv")
ORIGIN_COMPOSITION = load_table("origin_composition.csv")
FEATURE_AUDIT = load_table("data_integrity_feature_audit.csv")


def section(title: str, caption: str | None = None):
    if caption:
        st.markdown(
            f'<div class="section-head"><div><div class="section-title">{title}</div><div class="section-caption">{caption}</div></div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f'<div class="section-head"><div class="section-title">{title}</div></div>', unsafe_allow_html=True)


def panel(label: str, value: str, note: str = ""):
    st.markdown(
        f'<div class="panel"><div class="panel-label">{label}</div><div class="panel-value">{value}</div><div class="panel-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def make_chart(fig: go.Figure, height: int = 340):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=8, r=8, t=38, b=8),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="white",
        font=dict(family="DM Sans, sans-serif", color="#415569", size=12),
        title_font=dict(family="Manrope, sans-serif", color="#172A3A", size=15),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10)),
        xaxis=dict(showgrid=False, zeroline=False, linecolor="#E5ECF2", tickfont=dict(color="#6B7D8D")),
        yaxis=dict(showgrid=True, gridcolor="#EDF1F5", zeroline=False, linecolor="#E5ECF2", tickfont=dict(color="#6B7D8D")),
    )
    return fig


def nav_label(label: str, count: str | None = None) -> str:
    return label if not count else f"{label}  ·  {count}"


def normalize_col(value: object) -> str:
    text = str(value).strip()
    text = re.sub(r"\s*\((?:U/ml|mg/ml|ng/ml|U/mL|mg/mL|ng/mL)\)\s*", "", text, flags=re.I)
    text = re.sub(r"\s*(?:U/ml|mg/ml|ng/ml)\s*$", "", text, flags=re.I)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def canonical_key(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalize_col(value).lower())


FEATURE_ALIASES = {
    "Plasma CA19-9": {"plasmaca199", "ca199", "ca199plasma", "plasmaca19_9"},
    "LYVE1": {"lyve1", "urinelyve1"},
    "REG1B": {"reg1b"},
    "TFF1": {"tff1"},
    "Age": {"age", "patientage"},
    "Creatinine": {"creatinine", "urinecreatinine"},
}


def find_column(columns, canonical: str) -> str | None:
    keys = {canonical_key(c): c for c in columns}
    target_key = canonical_key(canonical)
    if target_key in keys:
        return keys[target_key]
    for alias in FEATURE_ALIASES.get(canonical, set()):
        if alias in keys:
            return keys[alias]
    return None


def read_uploaded_file(uploaded) -> tuple[pd.DataFrame, str]:
    name = uploaded.name.lower()
    uploaded.seek(0)
    if name.endswith(".csv"):
        df = pd.read_csv(uploaded)
        return df, "CSV"
    if name.endswith((".xlsx", ".xlsm", ".xls")):
        xls = pd.ExcelFile(uploaded)
        preferred = next((s for s in xls.sheet_names if s.strip().lower() == "samples"), xls.sheet_names[0])
        df = pd.read_excel(xls, sheet_name=preferred)
        return df, f"Excel · sheet: {preferred}"
    raise ValueError("Upload a CSV or Excel workbook (.csv, .xlsx, .xlsm, .xls).")


def audit_uploaded_dataset(raw: pd.DataFrame) -> dict:
    df = raw.copy()
    original_columns = list(df.columns)
    df.columns = [normalize_col(c) for c in df.columns]
    features = {name: find_column(df.columns, name) for name in FEATURE_ALIASES}

    target_col = None
    for col in df.columns:
        if canonical_key(col) in {"ispdac", "pdactarget", "pdaclabel"}:
            target_col = col
            break
    diag_col = None
    if target_col is None:
        for col in df.columns:
            key = canonical_key(col)
            if "diagnosis" in key and ("control" in key or "benign" in key or "pdac" in key):
                diag_col = col
                break

    labels = pd.Series(np.nan, index=df.index, dtype="float64")
    if target_col is not None:
        numeric_target = pd.to_numeric(df[target_col], errors="coerce")
        numeric_nonmissing = numeric_target.dropna()
        if not numeric_nonmissing.empty and numeric_nonmissing.isin([0, 1]).all():
            labels.loc[numeric_target.notna()] = numeric_target.loc[numeric_target.notna()].astype(float)
        else:
            # Handle common textual binary labels without guessing arbitrary codes.
            text = df[target_col].astype(str).str.strip().str.lower()
            pos = text.isin({"pdac", "positive", "case", "1", "true"})
            neg = text.isin({"non-pdac", "nonpdac", "control", "benign", "negative", "0", "false"})
            labels.loc[pos] = 1.0
            labels.loc[neg] = 0.0
    elif diag_col is not None:
        diagnosis = pd.to_numeric(df[diag_col], errors="coerce")
        labels.loc[diagnosis.isin([1, 2, 3])] = (diagnosis.loc[diagnosis.isin([1, 2, 3])] == 3).astype(float)

    group_col = next((c for c in df.columns if "cohort" in canonical_key(c)), None)
    origin_col = next((c for c in df.columns if "sampleorigin" in canonical_key(c) or canonical_key(c) == "origin"), None)
    sample_id_col = next((c for c in df.columns if canonical_key(c) in {"sampleid", "sample", "participantid", "subjectid", "id"}), None)

    feature_audit = []
    for canonical, matched in features.items():
        if matched is None:
            feature_audit.append({"Feature": canonical, "Column found": "No", "Missing n": np.nan, "Missing %": np.nan, "Non-numeric nonempty": np.nan, "Negative finite": np.nan})
            continue
        series = pd.to_numeric(df[matched], errors="coerce")
        nonempty = df[matched].notna() & (df[matched].astype(str).str.strip() != "")
        bad = int((nonempty & series.isna()).sum())
        finite = series[np.isfinite(series)]
        feature_audit.append({
            "Feature": canonical,
            "Column found": "Yes",
            "Missing n": int(series.isna().sum()),
            "Missing %": float(series.isna().mean() * 100),
            "Non-numeric nonempty": bad,
            "Negative finite": int((finite < 0).sum()),
        })

    labeled_count = int(labels.notna().sum())
    pdac_count = int((labels == 1).sum())
    nonpdac_count = int((labels == 0).sum())
    return {
        "df": df,
        "original_columns": original_columns,
        "features": features,
        "target_col": target_col,
        "diag_col": diag_col,
        "labels": labels,
        "feature_audit": pd.DataFrame(feature_audit),
        "group_col": group_col,
        "origin_col": origin_col,
        "sample_id_col": sample_id_col,
        "labeled_count": labeled_count,
        "unlabeled_count": int(labels.isna().sum()),
        "pdac_count": pdac_count,
        "nonpdac_count": nonpdac_count,
    }


def fmt_auc(value) -> str:
    try:
        if pd.isna(value): return "Not estimable"
        return f"{float(value):.3f}"
    except Exception:
        return "—"


def fmt_percent(value) -> str:
    try:
        if pd.isna(value): return "—"
        return f"{float(value)*100:.1f}%"
    except Exception:
        return "—"


# Sidebar / brand
with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-mark">PG</div><div><div class="brand-name">PDAC-GUARD</div><div class="brand-sub">Research intelligence</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="side-label">Workspace</div>', unsafe_allow_html=True)
    page = st.radio(
        "Navigate",
        ["Overview", "Case Readiness", "Dataset Studio", "Model Benchmarks", "Missingness Lab", "Cohort Shift", "Calibration", "Methods & Limits"],
        label_visibility="collapsed",
        key="main_navigation",
    )
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="side-label">Study snapshot</div>', unsafe_allow_html=True)
    st.markdown("<div style='font-size:12px;color:#BDD0DC;line-height:1.8'>Debernardi source dataset<br>590 labelled records<br>6 primary predictors<br>12 analysis stages</div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="side-label">Safety status</div>', unsafe_allow_html=True)
    st.markdown('<span class="status status-amber"><span class="status-dot"></span>Research-only prototype</span>', unsafe_allow_html=True)
    st.markdown("<div style='font-size:10px;color:#8097A8;line-height:1.6;margin-top:9px'>No clinically validated prediction service is bundled. Uploaded files are processed in this app session only.</div>", unsafe_allow_html=True)


def render_footer():
    st.markdown(
        '<div class="footer"><span>PDAC-GUARD · Missingness-aware selective prediction research</span><span>Research use only · Not a diagnostic device</span></div>',
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Overview
# -----------------------------------------------------------------------------
if page == "Overview":
    st.markdown(
        """
        <div class="hero">
          <div class="hero-kicker">Pancreatic cancer biomarker research</div>
          <div class="hero-title">Understand model reliability<br>before trusting the score.</div>
          <div class="hero-copy">A research workspace for exploring PDAC biomarker performance under missing data, group shift, calibration uncertainty and selective prediction. Built around the current 12-step study audit.</div>
          <div class="hero-foot"><span class="pill">590 labelled records</span><span class="pill">6 primary predictors</span><span class="pill">5-fold baseline evaluation</span><span class="pill">12-stage research workflow</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Labelled records", "590", "of 596 source rows")
    c2.metric("PDAC cases", "199", "33.7% of labelled cohort")
    c3.metric("Baseline AUC · Soft Voting", "0.9419", "pooled out-of-fold")
    c4.metric("CA19-9 missing", "40.7%", "240 / 590 records")

    section("Study signal", "Three findings that shape how the model should be interpreted")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        panel("Baseline discrimination", "0.9419", "Soft Voting ROC-AUC on the original source dataset. High internal discrimination is not clinical validation.")
    with col_b:
        panel("Severe biomarker outage", "0.6245", "ROC-AUC when all four principal biomarker measurements are unavailable in the stress-test scenario.")
    with col_c:
        panel("Accepted-case trade-off", "5.0%", "Selective risk at about 70.8% coverage for a confidence-only gate; all-PDAC automatic true-positive rate was 56.8%.")

    section("Baseline model comparison", "Cross-validated reference metrics from the consolidated audit")
    if not BASELINE.empty:
        m = BASELINE.copy()
        m = m.sort_values("ROC-AUC", ascending=True)
        fig = px.bar(m, x="ROC-AUC", y="Model", orientation="h", color="Model", text=m["ROC-AUC"].map(lambda x: f"{x:.3f}"),
                     color_discrete_sequence=[PALETTE["teal"], PALETTE["blue"], PALETTE["aqua"], PALETTE["purple"]])
        fig.update_traces(textposition="outside", cliponaxis=False, marker_line_width=0)
        fig.update_layout(showlegend=False, xaxis_title="ROC-AUC", yaxis_title="", xaxis_range=[0.82, 1.0])
        st.plotly_chart(make_chart(fig, 300), use_container_width=True)
        st.dataframe(m[["Model", "ROC-AUC", "Brier score", "Sensitivity at 0.5", "Specificity at 0.5", "Baseline audit"]].sort_values("ROC-AUC", ascending=False).style.format({"ROC-AUC":"{:.4f}","Brier score":"{:.4f}","Sensitivity at 0.5":"{:.1%}","Specificity at 0.5":"{:.1%}"}), use_container_width=True, hide_index=True)
    else:
        st.info("Baseline metric table is not available in the bundled data folder.")

    section("Interpretation guardrails", "What the dashboard will and will not claim")
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="callout success"><b>Supported by the current analysis</b><br>Missingness stress tests, group-held-out comparisons, calibration summaries, and observed associations between diagnosis and CA19-9 availability.</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="callout warning"><b>Not established</b><br>Clinical utility, causality of missingness, a MAR/MNAR mechanism, a universal best abstention gate, or independent external validation.</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Case readiness
# -----------------------------------------------------------------------------
elif page == "Case Readiness":
    st.title("Case readiness")
    st.caption("Enter a research record to audit input completeness. This page does not estimate disease risk or generate a diagnosis.")
    st.markdown('<div class="callout warning"><b>Prediction disabled.</b> The current package contains evaluation reports, not a verified serialized model. This form performs only an input-quality check and never returns a PDAC probability.</div>', unsafe_allow_html=True)
    st.write("")
    with st.form("case_readiness_form"):
        st.subheader("Biomarker measurements")
        st.caption("Leave any measurement blank when it is unavailable. Use the units that match the original dataset and study protocol.")
        b1, b2 = st.columns(2)
        with b1:
            ca19 = st.text_input("Plasma CA19-9", placeholder="Value or blank")
            lyve1 = st.text_input("LYVE1", placeholder="Value or blank")
        with b2:
            reg1b = st.text_input("REG1B", placeholder="Value or blank")
            tff1 = st.text_input("TFF1", placeholder="Value or blank")
        st.subheader("Clinical variables")
        c1, c2 = st.columns(2)
        with c1:
            age = st.text_input("Age", placeholder="Years")
        with c2:
            creatinine = st.text_input("Creatinine", placeholder="Value or blank")
        audit_case = st.form_submit_button("Audit input completeness", type="primary", use_container_width=True)
    if audit_case:
        values = {"Plasma CA19-9": ca19, "LYVE1": lyve1, "REG1B": reg1b, "TFF1": tff1, "Age": age, "Creatinine": creatinine}
        parsed = {}
        errors = []
        for name, raw in values.items():
            raw = str(raw).strip()
            if not raw:
                parsed[name] = None
                continue
            try:
                number = float(raw)
                if not math.isfinite(number):
                    raise ValueError
                if name in {"Plasma CA19-9", "LYVE1", "REG1B", "TFF1", "Creatinine"} and number < 0:
                    errors.append(f"{name}: negative values require review.")
                parsed[name] = number
            except Exception:
                parsed[name] = None
                errors.append(f"{name}: enter a numeric value or leave blank.")
        biomarker_names = ["Plasma CA19-9", "LYVE1", "REG1B", "TFF1"]
        observed_biomarkers = sum(parsed[n] is not None for n in biomarker_names)
        observed_total = sum(v is not None for v in parsed.values())
        if errors:
            st.markdown('<div class="callout danger"><b>Input validation needs attention</b><br>' + "<br>".join(errors) + "</div>", unsafe_allow_html=True)
        a, b, c = st.columns(3)
        a.metric("Observed biomarkers", f"{observed_biomarkers}/4")
        b.metric("Observed primary inputs", f"{observed_total}/6")
        c.metric("Missing inputs", f"{6-observed_total}/6")
        absent = [name for name, val in parsed.items() if val is None]
        if observed_biomarkers == 0:
            st.markdown('<div class="callout danger"><b>Input completeness: critical</b><br>None of the four primary biomarkers is present. This research UI would block automated scoring even if a compatible model were later added.</div>', unsafe_allow_html=True)
        elif observed_biomarkers < 3:
            st.markdown('<div class="callout warning"><b>Input completeness: limited</b><br>Fewer than three of the four primary biomarkers are present. This count is an exploratory research guardrail, not a validated clinical threshold.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="callout success"><b>Input completeness: recorded</b><br>At least three primary biomarkers are present. This is only an input-quality status; it is not a prediction of PDAC risk or permission to use this record clinically.</div>', unsafe_allow_html=True)
        st.write("**Inputs needing review:** " + (", ".join(absent) if absent else "None recorded as missing."))
        st.markdown('<div class="callout warning"><b>No risk score was calculated.</b> A compatible model artifact, locked preprocessing pipeline, validation documentation, and required governance review are not included in this frontend package.</div>', unsafe_allow_html=True)
        case_csv = pd.DataFrame([{**parsed, "observed_biomarkers": observed_biomarkers, "observed_primary_inputs": observed_total, "risk_score_calculated": False}]).to_csv(index=False).encode("utf-8")
        st.download_button("Download input audit (CSV)", data=case_csv, file_name="pdac_guard_input_readiness_audit.csv", mime="text/csv")

# -----------------------------------------------------------------------------
# Dataset studio
# -----------------------------------------------------------------------------
elif page == "Dataset Studio":
    st.title("Dataset studio")
    st.caption("Upload a source workbook to audit feature completeness, label availability and basic cohort composition locally in this session.")
    uploader = st.file_uploader("Upload source data", type=["csv", "xlsx", "xlsm", "xls"], help="Excel workbooks are read from the SAMPLES sheet when present; otherwise the first sheet is used.")
    st.markdown('<div class="muted-small">Files are processed in the running app session. This package does not write uploaded datasets to disk.</div>', unsafe_allow_html=True)
    if uploader is not None:
        try:
            uploaded_df, source_note = read_uploaded_file(uploader)
            st.session_state["uploaded_dataset"] = uploaded_df
            st.session_state["uploaded_dataset_name"] = uploader.name
            st.session_state["uploaded_source_note"] = source_note
        except Exception as exc:
            st.error(f"Could not read this file: {exc}")
    if "uploaded_dataset" in st.session_state:
        raw = st.session_state["uploaded_dataset"]
        audit = audit_uploaded_dataset(raw)
        safe_name = html.escape(str(st.session_state.get('uploaded_dataset_name', 'uploaded file')))
        safe_note = html.escape(str(st.session_state.get('uploaded_source_note', '')))
        st.markdown(f"<div class='status status-blue'><span class='status-dot'></span>Loaded: {safe_name} · {safe_note}</div>", unsafe_allow_html=True)
        st.write("")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", f"{len(audit['df']):,}")
        c2.metric("Columns", f"{audit['df'].shape[1]:,}")
        c3.metric("Labelled records", f"{audit['labeled_count']:,}")
        c4.metric("Unlabelled / unmapped", f"{audit['unlabeled_count']:,}")
        if audit['target_col']:
            st.caption(f"Binary target detected: `{audit['target_col']}`")
        elif audit['diag_col']:
            st.caption(f"Diagnosis mapping detected: `{audit['diag_col']}`; code 3 is treated as PDAC, codes 1 and 2 as non-PDAC.")
        else:
            st.warning("A recognized `is_PDAC` or diagnosis column was not found. The app will show feature audits but cannot summarize target classes.")
        cc1, cc2 = st.columns([1.1, 1.2])
        with cc1:
            section("Feature audit", "Expected primary inputs")
            st.dataframe(audit["feature_audit"], use_container_width=True, hide_index=True)
            csv = audit["feature_audit"].to_csv(index=False).encode("utf-8")
            st.download_button("Export feature audit", csv, "pdac_guard_feature_audit.csv", "text/csv")
        with cc2:
            section("Label composition", "Only recognized labels are summarized")
            if audit['target_col'] or audit['diag_col']:
                labels_df = pd.DataFrame({"Class": ["Non-PDAC", "PDAC", "Unlabelled / unmapped"], "Count": [audit['nonpdac_count'], audit['pdac_count'], audit['unlabeled_count']]})
                f = px.pie(labels_df, names="Class", values="Count", hole=0.68, color="Class", color_discrete_map={"Non-PDAC": PALETTE["blue"], "PDAC": PALETTE["teal"], "Unlabelled / unmapped": "#D7DEE6"})
                f.update_traces(textposition="inside", textinfo="percent+label", marker=dict(line=dict(color="white", width=2)))
                st.plotly_chart(make_chart(f, 325), use_container_width=True)
            else:
                st.info("Add or map a known target column to see class composition.")
        section("Missingness profile", "Percentage of records missing each required predictor")
        fa = audit["feature_audit"].copy()
        fa = fa[fa["Column found"] == "Yes"].sort_values("Missing %", ascending=True)
        if not fa.empty:
            fig = px.bar(fa, x="Missing %", y="Feature", orientation="h", color="Missing %", color_continuous_scale=["#D7F1EA", "#44A3A8", "#B74755"], text=fa["Missing %"].map(lambda x: f"{x:.1f}%"))
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_layout(coloraxis_showscale=False, xaxis_title="Missing values (%)", yaxis_title="", xaxis_range=[0, min(110, max(10, float(fa["Missing %"].max())*1.2))])
            st.plotly_chart(make_chart(fig, 310), use_container_width=True)
        if audit["group_col"]:
            section("Cohort counts", f"Group field detected: {audit['group_col']}")
            grp = audit["df"][audit["group_col"]].fillna("Missing").astype(str).value_counts().rename_axis("Group").reset_index(name="Records")
            st.dataframe(grp, use_container_width=True, hide_index=True)
        if audit["origin_col"]:
            section("Sample-origin counts", f"Group field detected: {audit['origin_col']}")
            grp = audit["df"][audit["origin_col"]].fillna("Missing").astype(str).value_counts().rename_axis("Sample origin").reset_index(name="Records")
            st.dataframe(grp, use_container_width=True, hide_index=True)
        with st.expander("Preview normalized input rows"):
            st.dataframe(audit["df"].head(30), use_container_width=True, hide_index=True)
        st.caption("This is an audit view, not a model evaluation. It does not retrain, validate or score a predictive model.")
    else:
        st.markdown('<div class="panel"><div class="panel-label">Getting started</div><div class="panel-value" style="font-size:22px">Bring your study workbook</div><div class="panel-note">Use the original workbook containing a <b>SAMPLES</b> sheet, or a CSV export with the six project predictors and a diagnosis/target field. The app will validate the schema and show missingness before any model work is attempted.</div></div>', unsafe_allow_html=True)
        st.write("")
        st.markdown("**Expected predictor fields**")
        st.dataframe(pd.DataFrame({"Canonical feature": list(FEATURE_ALIASES.keys()), "Role": ["Biomarker"]*4 + ["Clinical"]*2}), use_container_width=True, hide_index=True)
        st.markdown('<div class="callout warning"><b>Data privacy</b><br>Use only data you are authorized to process. Do not upload identifiable patient information to a shared or public deployment.</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Model benchmarks
# -----------------------------------------------------------------------------
elif page == "Model Benchmarks":
    st.title("Model benchmarks")
    st.caption("Internal five-fold out-of-fold baseline metrics. Threshold metrics use probability 0.5 unless otherwise stated.")
    if BASELINE.empty:
        st.error("Baseline metrics could not be loaded from the bundled tables.")
    else:
        m = BASELINE.copy()
        metric_options = {"ROC-AUC": "ROC-AUC", "Brier score (lower is better)": "Brier score", "Sensitivity at 0.5": "Sensitivity at 0.5", "Specificity at 0.5": "Specificity at 0.5"}
        selected_metric_label = st.selectbox("Compare models by", list(metric_options.keys()))
        metric = metric_options[selected_metric_label]
        sorted_m = m.sort_values(metric, ascending=(metric == "Brier score"))
        fig = px.bar(sorted_m, x=metric, y="Model", orientation="h", color="Model", text=sorted_m[metric].map(lambda x: f"{x:.3f}"), color_discrete_sequence=[PALETTE["teal"], PALETTE["blue"], PALETTE["aqua"], PALETTE["purple"]])
        fig.update_traces(textposition="outside", cliponaxis=False, marker_line_width=0)
        if metric == "ROC-AUC":
            fig.update_layout(xaxis_range=[0.80, 1.0])
        elif metric == "Brier score":
            fig.update_layout(xaxis_range=[0, max(0.14, float(m[metric].max())*1.25)])
        else:
            fig.update_layout(xaxis_range=[0, 1.08])
        fig.update_layout(showlegend=False, xaxis_title=selected_metric_label, yaxis_title="")
        st.plotly_chart(make_chart(fig, 335), use_container_width=True)
        show = m.copy()
        for col in ["ROC-AUC", "Brier score", "Sensitivity at 0.5", "Specificity at 0.5"]:
            show[col] = show[col].astype(float)
        st.dataframe(show[["Model", "ROC-AUC", "Brier score", "Sensitivity at 0.5", "Specificity at 0.5", "Baseline audit"]].sort_values("ROC-AUC", ascending=False).style.format({"ROC-AUC":"{:.4f}","Brier score":"{:.4f}","Sensitivity at 0.5":"{:.1%}","Specificity at 0.5":"{:.1%}"}), use_container_width=True, hide_index=True)
        st.download_button("Download baseline comparison CSV", m.to_csv(index=False).encode("utf-8"), "pdac_guard_baseline_model_metrics.csv", "text/csv")
    section("How to read these metrics")
    a, b = st.columns(2)
    with a:
        st.markdown('<div class="callout"><b>Discrimination · ROC-AUC</b><br>Measures ranking quality across thresholds. It does not specify the sensitivity achieved at one threshold and does not prove calibrated probabilities.</div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="callout"><b>Calibration · Brier score</b><br>Measures squared error of predicted probabilities; lower is better. It depends on prevalence and does not replace sensitivity/specificity review.</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Missingness lab
# -----------------------------------------------------------------------------
elif page == "Missingness Lab":
    st.title("Missingness lab")
    st.caption("Stress-test results from the study notebooks. These are retrospective simulations on the source dataset, not patient-level guarantees.")
    if not STRESS.empty:
        scenario_labels = {
            "baseline_no_extra_mask": "Baseline · no additional masking",
            "random_mask_10pct": "10% random masking",
            "random_mask_20pct": "20% random masking",
            "random_mask_30pct": "30% random masking",
            "CA19_9_unavailable": "CA19-9 unavailable",
            "LYVE1_unavailable": "LYVE1 unavailable",
            "all_four_biomarkers_unavailable": "All four biomarkers unavailable",
        }
        ss = STRESS.copy()
        ss["Scenario label"] = ss["scenario"].map(scenario_labels).fillna(ss["scenario"])
        available_scenarios = set(ss["scenario"])
        ordered_scenarios = [s for s in scenario_labels if s in available_scenarios]
        ss = ss.set_index("scenario").loc[ordered_scenarios].reset_index()
        chart_metric = st.radio("Metric to plot", ["ROC-AUC", "Brier score", "Sensitivity", "Specificity"], horizontal=True)
        ycol = {"ROC-AUC":"ROC_AUC", "Brier score":"Brier_score", "Sensitivity":"sensitivity_at_0.5", "Specificity":"specificity_at_0.5"}[chart_metric]
        fig = px.bar(ss, x="Scenario label", y=ycol, color="Scenario label", color_discrete_sequence=[PALETTE["teal"],PALETTE["aqua"],PALETTE["blue"],PALETTE["purple"],PALETTE["amber"],PALETTE["green"],PALETTE["red"]], text=ss[ycol].map(lambda x: f"{x:.3f}"))
        fig.update_traces(textposition="outside", cliponaxis=False, marker_line_width=0)
        fig.update_layout(showlegend=False, xaxis_title="Scenario", yaxis_title=chart_metric, xaxis_tickangle=-22)
        if chart_metric in {"ROC-AUC", "Sensitivity", "Specificity"}:
            fig.update_layout(yaxis_range=[0, 1.08])
        st.plotly_chart(make_chart(fig, 380), use_container_width=True)
        display = ss[["Scenario label", "n", "ROC_AUC", "Brier_score", "error_rate_at_0.5", "sensitivity_at_0.5", "specificity_at_0.5"]].rename(columns={"Scenario label":"Scenario", "n":"N", "ROC_AUC":"ROC-AUC", "Brier_score":"Brier score", "error_rate_at_0.5":"Error rate @ 0.5", "sensitivity_at_0.5":"Sensitivity @ 0.5", "specificity_at_0.5":"Specificity @ 0.5"})
        st.dataframe(display.style.format({"ROC-AUC":"{:.3f}","Brier score":"{:.3f}","Error rate @ 0.5":"{:.1%}","Sensitivity @ 0.5":"{:.1%}","Specificity @ 0.5":"{:.1%}"}), use_container_width=True, hide_index=True)
        st.download_button("Download missingness scenario table", display.to_csv(index=False).encode("utf-8"), "pdac_guard_missingness_scenarios.csv", "text/csv")
    section("Repeated random-masking experiment", "Five independent masking draws per percentage; results are mean ± SD")
    if not REPEATED.empty:
        rm = REPEATED[(REPEATED["Model"].str.lower() == "soft voting") & REPEATED["Scenario"].str.startswith("random_mask_")].copy()
        rm["Mask %"] = rm["Scenario"].str.extract(r"(\d+)").astype(float)
        rm = rm.sort_values("Mask %")
        metric_choice = st.selectbox("Repeated-mask outcome", ["AUC_mean", "Brier_mean", "Sensitivity_mean"], format_func=lambda x: {"AUC_mean":"ROC-AUC", "Brier_mean":"Brier score", "Sensitivity_mean":"Sensitivity at 0.5"}[x])
        sdcol = {"AUC_mean":"AUC_sd", "Brier_mean":"Brier_sd", "Sensitivity_mean":None}[metric_choice]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=rm["Mask %"], y=rm[metric_choice], mode="lines+markers", line=dict(color=PALETTE["teal"], width=3), marker=dict(size=9), name="Mean"))
        if sdcol:
            fig.add_trace(go.Scatter(x=rm["Mask %"], y=rm[metric_choice], mode="markers", marker=dict(color=PALETTE["teal"], size=9), error_y=dict(type="data", array=rm[sdcol].fillna(0), visible=True), name="SD"))
        base_val = rm[metric_choice].iloc[0] if False else None
        fig.update_layout(title="Performance as additional values are masked", xaxis_title="Randomly masked values (%)", yaxis_title=metric_choice.replace("_mean", "").replace("_", " "))
        st.plotly_chart(make_chart(fig, 320), use_container_width=True)
        st.dataframe(rm[["Scenario", "Repeats", "AUC_mean", "AUC_sd", "Brier_mean", "Brier_sd", "Sensitivity_mean", "Specificity_mean"]].style.format({"AUC_mean":"{:.4f}", "AUC_sd":"{:.4f}", "Brier_mean":"{:.4f}", "Brier_sd":"{:.4f}", "Sensitivity_mean":"{:.1%}", "Specificity_mean":"{:.1%}"}), use_container_width=True, hide_index=True)
    st.markdown('<div class="callout warning"><b>Interpret carefully</b><br>Random masking is a simulated stress test. It does not reproduce every real-world missingness mechanism. The AUC deterioration supports robustness testing, not claims that missingness has a particular cause.</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Cohort shift
# -----------------------------------------------------------------------------
elif page == "Cohort Shift":
    st.title("Cohort shift")
    st.caption("Leave-one-group-out evaluation on cohorts and sample origins within the source dataset. This is internal domain-shift evaluation, not external validation.")
    if GROUP_METRICS.empty:
        st.error("Group-held-out table is missing.")
    else:
        available_group_types = GROUP_METRICS["group_type"].dropna().unique().tolist()
        group_type = st.radio("Evaluate grouping", available_group_types, horizontal=True, format_func=lambda x: "Patient cohort" if x == "Patient's Cohort" else "Sample origin")
        df = GROUP_METRICS[GROUP_METRICS["group_type"] == group_type].copy()
        order = df[["heldout_group", "n_test"]].drop_duplicates().sort_values("n_test", ascending=False)["heldout_group"].tolist()
        model = st.selectbox("Model", sorted(df["model"].dropna().unique()), index=sorted(df["model"].dropna().unique()).index("Soft Voting") if "Soft Voting" in df["model"].unique() else 0)
        picked = df[df["model"] == model].copy()
        picked["heldout_group"] = pd.Categorical(picked["heldout_group"], categories=order, ordered=True)
        picked = picked.sort_values("heldout_group")
        plotted = picked[picked["roc_auc"].notna()]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=plotted["heldout_group"].astype(str), y=plotted["roc_auc"], marker_color=PALETTE["teal"], text=plotted["roc_auc"].map(lambda x:f"{x:.3f}"), textposition="outside", error_y=dict(type="data", symmetric=False, array=(plotted["roc_auc_ci95_high"]-plotted["roc_auc"]).clip(lower=0), arrayminus=(plotted["roc_auc"]-plotted["roc_auc_ci95_low"]).clip(lower=0), visible=True)))
        fig.update_layout(title=f"{model} · group-held-out ROC-AUC", yaxis_title="ROC-AUC (95% bootstrap CI)", xaxis_title="Held-out group", yaxis_range=[0,1.12])
        st.plotly_chart(make_chart(fig, 360), use_container_width=True)
        st.dataframe(picked[["heldout_group", "n_test", "n_PDAC", "PDAC_prevalence", "roc_auc", "roc_auc_ci95_low", "roc_auc_ci95_high", "brier_score", "sensitivity_at_0_5", "specificity_at_0_5"]].rename(columns={"heldout_group":"Held-out group", "n_test":"N", "n_PDAC":"PDAC N", "PDAC_prevalence":"PDAC prevalence", "roc_auc":"ROC-AUC", "roc_auc_ci95_low":"AUC CI low", "roc_auc_ci95_high":"AUC CI high", "brier_score":"Brier score", "sensitivity_at_0_5":"Sensitivity @ 0.5", "specificity_at_0_5":"Specificity @ 0.5"}).style.format({"PDAC prevalence":"{:.1%}", "ROC-AUC":"{:.3f}", "AUC CI low":"{:.3f}", "AUC CI high":"{:.3f}", "Brier score":"{:.3f}", "Sensitivity @ 0.5":"{:.1%}", "Specificity @ 0.5":"{:.1%}"}), use_container_width=True, hide_index=True)
    section("Group composition audit", "Prevalence varies substantially across the source groups")
    composition = pd.concat([COHORT_COMPOSITION.assign(grouping="Patient cohort"), ORIGIN_COMPOSITION.assign(grouping="Sample origin")], ignore_index=True) if not COHORT_COMPOSITION.empty and not ORIGIN_COMPOSITION.empty else pd.DataFrame()
    if not composition.empty:
        comp = composition.rename(columns={"field":"Group type", "group":"Group", "n":"N", "non_PDAC_n":"Non-PDAC N", "PDAC_n":"PDAC N", "share_of_dataset":"Share of dataset"})
        comp["PDAC prevalence"] = comp["PDAC N"] / comp["N"]
        st.dataframe(comp[["Group type", "Group", "N", "Non-PDAC N", "PDAC N", "PDAC prevalence", "Share of dataset"]].style.format({"PDAC prevalence":"{:.1%}", "Share of dataset":"{:.1%}"}), use_container_width=True, hide_index=True)
    st.markdown('<div class="callout warning"><b>Small or single-class groups</b><br>ESP has few records and UCL has no PDAC cases. ROC-AUC and sensitivity are not estimable for a held-out group with only one outcome class; do not rank models from these small subsets alone.</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Calibration
# -----------------------------------------------------------------------------
elif page == "Calibration":
    st.title("Calibration & uncertainty")
    st.caption("Calibration metrics are computed from fixed group-held-out predictions. Bootstrap intervals do not include model-retraining uncertainty.")
    if CALIBRATION.empty:
        st.error("Calibration uncertainty table is missing.")
    else:
        heldout_type = st.radio("Group definition", CALIBRATION["group_type"].dropna().unique().tolist(), horizontal=True, format_func=lambda x: "Patient cohort" if x == "Patient's Cohort" else "Sample origin")
        cal = CALIBRATION[CALIBRATION["group_type"] == heldout_type].copy()
        models = sorted(cal["model"].dropna().unique())
        chosen_models = st.multiselect("Models to display", models, default=[m for m in ["Soft Voting", "Logistic Regression", "Random Forest"] if m in models])
        cal = cal[cal["model"].isin(chosen_models)]
        metric_cal = st.radio("Calibration summary", ["ECE_5bin", "brier_score"], horizontal=True, format_func=lambda x: "Equal-frequency ECE (5 bins)" if x == "ECE_5bin" else "Brier score")
        if not cal.empty:
            lo_col, hi_col = ("ECE_ci95_low", "ECE_ci95_high") if metric_cal == "ECE_5bin" else ("brier_ci95_low", "brier_ci95_high")
            fig = go.Figure()
            colors = {"Logistic Regression":PALETTE["blue"], "Random Forest":PALETTE["teal"], "XGBoost":PALETTE["purple"], "Soft Voting":PALETTE["aqua"]}
            for model_name in chosen_models:
                one = cal[cal["model"] == model_name].sort_values("heldout_group")
                if one.empty: continue
                yerr_plus = (one[hi_col] - one[metric_cal]).clip(lower=0)
                yerr_minus = (one[metric_cal] - one[lo_col]).clip(lower=0)
                fig.add_trace(go.Scatter(x=one["heldout_group"], y=one[metric_cal], mode="lines+markers", name=model_name, line=dict(width=2.5, color=colors.get(model_name, PALETTE["navy"])), marker=dict(size=8), error_y=dict(type="data", symmetric=False, array=yerr_plus, arrayminus=yerr_minus, visible=True)))
            fig.update_layout(title="Group-wise calibration metric with 95% bootstrap intervals", xaxis_title="Held-out group", yaxis_title="Lower is better")
            st.plotly_chart(make_chart(fig, 365), use_container_width=True)
        display_cal = cal[["group_type", "heldout_group", "model", "n", "PDAC_prevalence", "roc_auc", "roc_auc_ci95_low", "roc_auc_ci95_high", "brier_score", "brier_ci95_low", "brier_ci95_high", "ECE_5bin", "ECE_ci95_low", "ECE_ci95_high", "calibration_intercept", "calibration_slope"]].copy()
        st.dataframe(display_cal.style.format({"PDAC_prevalence":"{:.1%}", "roc_auc":"{:.3f}", "roc_auc_ci95_low":"{:.3f}", "roc_auc_ci95_high":"{:.3f}", "brier_score":"{:.3f}", "brier_ci95_low":"{:.3f}", "brier_ci95_high":"{:.3f}", "ECE_5bin":"{:.3f}", "ECE_ci95_low":"{:.3f}", "ECE_ci95_high":"{:.3f}", "calibration_intercept":"{:.3f}", "calibration_slope":"{:.3f}"}), use_container_width=True, hide_index=True)
        st.download_button("Download calibration table", display_cal.to_csv(index=False).encode("utf-8"), "pdac_guard_calibration_uncertainty.csv", "text/csv")
    st.markdown('<div class="callout"><b>Metric interpretation</b><br>AUC measures ranking, Brier score measures probabilistic prediction error, and ECE summarizes bin-level calibration error. A small sample and a small number of bins can make ECE unstable; inspect intervals and group prevalence alongside the point estimate.</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Methods / limits
# -----------------------------------------------------------------------------
elif page == "Methods & Limits":
    st.title("Methods & limitations")
    st.caption("A transparent summary of the analysis that this application visualizes.")
    section("Study specification", "Primary evaluation snapshot")
    c1,c2,c3 = st.columns(3)
    with c1: panel("Source data", "Debernardi et al.", "Published case-control biomarker dataset; 590 labelled records retained from 596 source rows.")
    with c2: panel("Target", "PDAC vs non-PDAC", "199 PDAC cases and 391 non-PDAC records (208 benign disease; 183 controls).")
    with c3: panel("Primary features", "6 inputs", "Plasma CA19-9, LYVE1, REG1B, TFF1, age and creatinine.")

    section("Analysis pathway")
    steps = [
        ("01", "Baseline evaluation", "Pooled out-of-fold discrimination, Brier score and threshold metrics."),
        ("02–08", "Selective prediction", "Confidence gates, biomarker-count guardrails, coverage–risk trade-offs, and retention experiments."),
        ("09", "Data integrity", "Diagnosis coding, duplicate identifiers and predictor missingness audit."),
        ("10", "Group-held-out evaluation", "Leave-one-cohort-out and leave-one-origin-out internal domain-shift experiments."),
        ("11–12", "Missingness & calibration", "Group-by-diagnosis missingness associations, calibration metrics and bootstrap intervals."),
    ]
    for n,title,desc in steps:
        st.markdown(f'<div class="panel" style="display:flex;gap:16px;align-items:flex-start;margin-bottom:10px"><div style="font:800 17px Manrope;color:#287D8E;min-width:55px">{n}</div><div><div style="font:700 15px Manrope;color:#172A3A">{title}</div><div class="panel-note">{desc}</div></div></div>', unsafe_allow_html=True)

    section("Preprocessing and evaluation")
    st.markdown("""
    - Biomarker measurements are log-transformed after nonnegative clipping in the primary pipeline, with imputation and scaling fitted inside each training fold.
    - The baseline model comparison uses out-of-fold probabilities. Selective-prediction thresholds are chosen from development/inner-fold predictions before evaluation on held-out folds.
    - Group-held-out tests exclude a cohort or sample-origin group from model fitting; these evaluate internal domain shift, not independent external validation.
    - CA19-9 missingness association tests are observational. They do not establish why data are missing and cannot distinguish missing-at-random from missing-not-at-random on their own.
    """)
    section("Known limitations")
    st.markdown('<div class="callout warning"><b>Research only.</b> The underlying dataset is retrospective case-control data. Simulated masking is not a replacement for real-world missingness testing. Bootstrap intervals based on fixed predictions omit retraining uncertainty. Some origin groups are small or single-class. No compatible independent external validation is included. The frontend does not provide a diagnosis, medical advice or a patient-care recommendation.</div>', unsafe_allow_html=True)
    section("Reference")
    st.markdown("Debernardi S, O’Brien H, Alghamdi AS, et al. A combination of urinary biomarker panel and PancRISK score for earlier detection of pancreatic cancer: a case-control study. *PLOS Medicine*. 2020;17(12):e1003489. [https://doi.org/10.1371/journal.pmed.1003489](https://doi.org/10.1371/journal.pmed.1003489). Data supplement: [https://doi.org/10.1371/journal.pmed.1003489.s009](https://doi.org/10.1371/journal.pmed.1003489.s009).")

render_footer()
