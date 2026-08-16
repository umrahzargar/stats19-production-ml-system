import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import streamlit as st

API_BASE_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)


# Page setup

st.set_page_config(
    page_title="STATS19 Severity Prediction",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700;800&family=Inter:wght@400;500;600&display=swap');

    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #06101f;
        border-right: 1px solid rgba(148, 163, 184, 0.08);
    }

    [data-testid="stSidebar"] * {
        color: #cbd5e1;
    }

    .sb-logo {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        color: #f1f5f9;
        letter-spacing: -0.03em;
        margin-bottom: 0.25rem;
    }

    .sb-tagline {
        font-size: 0.82rem;
        color: #64748b;
        line-height: 1.5;
        margin-bottom: 1rem;
    }

    .sb-accent-bar {
        height: 2px;
        width: 40px;
        background: #f59e0b;
        border-radius: 999px;
        margin-bottom: 1.2rem;
    }

    .sb-traffic {
        display: flex;
        gap: 6px;
        align-items: center;
        margin-bottom: 1.5rem;
    }

    .sb-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }

    .sb-pill {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.25);
        color: #fbbf24;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    .sb-meta {
        color: #475569;
        font-size: 0.8rem;
        line-height: 1.7;
    }

    .sb-meta b {
        color: #64748b;
        font-weight: 600;
    }

    /* ── Page heading ── */
    .page-header {
        margin-bottom: 1.75rem;
    }

    .page-eyebrow {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #ffffff !important;
        background: rgba(245, 158, 11, 0.22);
        border: 1px solid rgba(245, 158, 11, 0.45);
        border-radius: 4px;
        padding: 0.2rem 0.6rem;
        margin-bottom: 0.65rem;
    }

    .page-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.03em;
        color: #f1f5f9;
        margin-bottom: 0.45rem;
    }

    .page-subtitle {
        font-size: 0.95rem;
        color: #64748b;
        line-height: 1.65;
        max-width: 640px;
        margin-bottom: 0;
    }

    /* ── Section title ── */
    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #e2e8f0;
        letter-spacing: -0.01em;
        margin-top: 1.75rem;
        margin-bottom: 0.85rem;
        padding-left: 0.75rem;
        border-left: 3px solid #f59e0b;
    }

    /* ── KPI card ── */
    .kpi-card {
        padding: 1.1rem 1.1rem 0.9rem;
        border-radius: 14px;
        background: #0d1829;
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-top: 3px solid #f59e0b;
        min-height: 108px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: border-color 0.2s ease;
    }

    .kpi-card:hover {
        border-color: rgba(245, 158, 11, 0.55);
        border-top-color: #f59e0b;
    }

    .kpi-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #475569;
    }

    .kpi-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.7rem;
        font-weight: 800;
        color: #f1f5f9;
        font-variant-numeric: tabular-nums;
        line-height: 1.1;
    }

    .kpi-help {
        font-size: 0.72rem;
        color: #334155;
        margin-top: 0.2rem;
    }

    /* ── Info card ── */
    .info-card {
        padding: 1.1rem 1.25rem;
        border-radius: 14px;
        background: #0d1829;
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-left: 3px solid rgba(148, 163, 184, 0.1);
        height: 100%;
        transition: border-left-color 0.2s ease, background 0.2s ease;
    }

    .info-card:hover {
        border-left-color: #f59e0b;
        background: #0f1e35;
    }

    .info-card-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 0.45rem;
    }

    .info-card-text {
        font-size: 0.875rem;
        color: #64748b;
        line-height: 1.6;
    }

    /* ── Hero card ── */
    .hero-card {
        padding: 1.25rem 1.5rem;
        border-radius: 16px;
        background: #0d1829;
        border: 1px solid rgba(245, 158, 11, 0.18);
        border-left: 4px solid #f59e0b;
        margin-bottom: 1.5rem;
        font-size: 0.95rem;
        color: #94a3b8;
        line-height: 1.7;
    }

    /* ── Status boxes ── */
    .success-box {
        padding: 0.85rem 1rem 0.85rem 1.25rem;
        border-radius: 10px;
        background: rgba(34, 197, 94, 0.06);
        border: 1px solid rgba(34, 197, 94, 0.15);
        border-left: 3px solid #22c55e;
        color: #4ade80;
        font-size: 0.9rem;
        margin: 1rem 0;
    }

    .warning-box {
        padding: 0.85rem 1rem 0.85rem 1.25rem;
        border-radius: 10px;
        background: rgba(245, 158, 11, 0.06);
        border: 1px solid rgba(245, 158, 11, 0.15);
        border-left: 3px solid #f59e0b;
        color: #fbbf24;
        font-size: 0.9rem;
        margin: 1rem 0;
    }

    .danger-box {
        padding: 0.85rem 1rem 0.85rem 1.25rem;
        border-radius: 10px;
        background: rgba(239, 68, 68, 0.06);
        border: 1px solid rgba(239, 68, 68, 0.15);
        border-left: 3px solid #ef4444;
        color: #f87171;
        font-size: 0.9rem;
        margin: 1rem 0;
    }

    /* ── Disclaimer banner ── */
    .disclaimer-box {
        padding: 0.85rem 1rem 0.85rem 1.25rem;
        border-radius: 10px;
        background: rgba(148, 163, 184, 0.04);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-left: 3px solid #475569;
        color: #64748b;
        font-size: 0.875rem;
        margin: 1rem 0;
        line-height: 1.6;
    }

    /* ── Main content buttons ── */
    .block-container .stButton > button {
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.875rem;
        padding: 0.5rem 1.1rem;
        transition: all 0.15s ease;
    }

    .block-container .stButton > button:hover {
        transform: translateY(-1px);
    }

    .stDownloadButton > button {
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.875rem;
        padding: 0.5rem 1.1rem;
    }

    /* ── Sidebar nav buttons — inactive ── */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: 1px solid transparent !important;
        color: #4b5a72 !important;
        text-align: left !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        padding: 0.55rem 0.9rem !important;
        border-radius: 9px !important;
        width: 100% !important;
        letter-spacing: 0.01em !important;
        box-shadow: none !important;
        transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease !important;
        justify-content: flex-start !important;
        transform: none !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(245, 158, 11, 0.06) !important;
        color: #94a3b8 !important;
        border-color: rgba(245, 158, 11, 0.12) !important;
        box-shadow: none !important;
        transform: none !important;
    }

    /* ── Sidebar nav buttons — active (kind=primary) ── */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: rgba(245, 158, 11, 0.08) !important;
        border: 1px solid rgba(245, 158, 11, 0.2) !important;
        border-left: 3px solid #f59e0b !important;
        color: #fbbf24 !important;
        font-weight: 600 !important;
        box-shadow: none !important;
        padding-left: 0.75rem !important;
        transform: none !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: rgba(245, 158, 11, 0.11) !important;
        transform: none !important;
    }

    /* ── Streamlit metrics ── */
    [data-testid="stMetric"] {
        background: #0d1829;
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-top: 3px solid #f59e0b;
        padding: 1rem;
        border-radius: 14px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: #475569 !important;
    }

    [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 800 !important;
        font-variant-numeric: tabular-nums;
    }

    /* ── Expander ── */
    div[data-testid="stExpander"] {
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.1) !important;
        background: #0a1525;
    }

    /* ── Divider ── */
    hr {
        margin-top: 1.75rem;
        margin-bottom: 1.75rem;
        border-color: rgba(148, 163, 184, 0.08);
    }

    .small-note {
        color: #475569;
        font-size: 0.8rem;
        line-height: 1.7;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# File paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

METRICS_PATH = PROJECT_ROOT / "model" / "model_metrics.json"
DEMO_DATA_PATH = PROJECT_ROOT / "data" / "X_test_demo_sample.csv"
SHAP_GROUPED_PATH = (
    PROJECT_ROOT / "outputs" / "shap_grouped_feature_importance.xls"
)

OVERSAMPLING_PATH = (
    PROJECT_ROOT / "outputs" / "oversampling_sensitivity_summary.xls"
)

TEST_PREDICTIONS_PATH = (
    PROJECT_ROOT / "outputs" / "test_predictions.xls"
)



# Helper functions


@st.cache_data
def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


@st.cache_data
def load_table(path):
    path = Path(path)
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.read_excel(path)


def load_uploaded_table(uploaded_file):
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded_file)
    try:
        return pd.read_excel(uploaded_file)
    except Exception:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file)


def get_metric(metrics, possible_names, default=None):
    for name in possible_names:
        if name in metrics:
            return metrics[name]
    return default


def format_metric(value, decimals=3):
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.{decimals}f}"
    except Exception:
        return str(value)


def kpi_card(label, value, help_text=None):
    help_html = f"<div class='kpi-help'>{help_text}</div>" if help_text else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {help_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def info_card(title, text):
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-card-title">{title}</div>
            <div class="info-card-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def create_prediction_summary(batch_results):
    total_rows = len(batch_results)
    severe_count = int((batch_results["predicted_class"] == "Severe").sum())
    non_severe_count = int((batch_results["predicted_class"] == "Non-severe").sum())
    avg_probability = float(batch_results["severe_probability"].mean())
    max_probability = float(batch_results["severe_probability"].max())

    return total_rows, severe_count, non_severe_count, avg_probability, max_probability


def show_page_title(icon, title, subtitle, eyebrow=None):
    eyebrow_html = (
        f'<div class="page-eyebrow">{eyebrow}</div>' if eyebrow else ""
    )
    st.markdown(
        f"""<div class="page-header">
{eyebrow_html}
<div class="page-title">{icon}&nbsp; {title}</div>
<div class="page-subtitle">{subtitle}</div>
</div>""",
        unsafe_allow_html=True,
    )


def severity_message(predicted_class):
    if predicted_class == 1:
        st.markdown(
            "<div class='danger-box'><b>Predicted:</b> This case is classified as <b>Severe</b>.</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div class='success-box'><b>Predicted:</b> This case is classified as <b>Non-severe</b>.</div>",
            unsafe_allow_html=True
        )

def check_api_health():
    response = requests.get(
        f"{API_BASE_URL}/health",
        timeout=5
    )

    response.raise_for_status()

    return response.json()

def prepare_api_payload(row):
    record = row.iloc[0]

    payload = {}

    for column, value in record.items():
        if pd.isna(value):
            payload[column] = None
        elif hasattr(value, "item"):
            payload[column] = value.item()
        else:
            payload[column] = value

    return payload


def predict_single_case_via_api(row):
    payload = prepare_api_payload(row)

    response = requests.post(
        f"{API_BASE_URL}/predict",
        json=payload,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def predict_batch_via_api(data, source_filename):
    records = []

    for _, row in data.iterrows():
        clean_record = {}

        for column, value in row.items():
            if pd.isna(value):
                clean_record[column] = None
            elif hasattr(value, "item"):
                clean_record[column] = value.item()
            else:
                clean_record[column] = value

        records.append(clean_record)

    payload = {
        "source_filename": source_filename,
        "records": records,
    }

    response = requests.post(
        f"{API_BASE_URL}/predict/batch",
        json=payload,
        timeout=60,
    )

    response.raise_for_status()

    return response.json()

# Load required files

try:
    metrics = load_json(METRICS_PATH)
    demo_data = load_table(DEMO_DATA_PATH)
except Exception as e:
    st.error("The app could not load one or more required files.")
    st.exception(e)
    st.stop()


threshold = get_metric(
    metrics,
    possible_names=[
        "threshold",
        "final_threshold",
        "selected_threshold",
        "optimal_threshold",
        "best_threshold"
    ],
    default=0.5
)

try:
    threshold = float(threshold)
except Exception:
    threshold = 0.5



# Sidebar

with st.sidebar:
    try:
        api_health = check_api_health()

        st.markdown(
            "<div class='success-box'>● Backend connected</div>",
            unsafe_allow_html=True
        )
    except requests.RequestException:
        st.markdown(
            "<div class='danger-box'>● Backend unavailable</div>",
            unsafe_allow_html=True
        )
    st.markdown("<div class='sb-pill'>Portfolio · ML Demo</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-logo'>🚦 STATS19</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-accent-bar'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sb-tagline'>Road casualty severity prediction · XGBoost · 2023 GB data</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class='sb-traffic'>
            <div class='sb-dot' style='background:#ef4444;'></div>
            <div class='sb-dot' style='background:#f59e0b;'></div>
            <div class='sb-dot' style='background:#22c55e;'></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ── Navigation ──────────────────────────────────────
    if "page" not in st.session_state:
        st.session_state.page = "Home / Project Summary"

    NAV_ITEMS = [
        ("Home / Project Summary",   "🏠", "Home"),
        ("Prediction Demo",          "🔍", "Predictions"),
        ("Model Performance",        "📊", "Performance"),
        ("SHAP Feature Importance",  "🧠", "SHAP Analysis"),
        ("Oversampling Sensitivity", "⚖️", "Oversampling"),
        ("Limitations",              "⚠️", "Limitations"),
    ]

    for page_key, icon, label in NAV_ITEMS:
        is_active = st.session_state.page == page_key
        if st.button(
            f"{icon}  {label}",
            key=f"nav_{page_key}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.page = page_key
            st.rerun()

    page = st.session_state.page

    st.divider()
    st.markdown(
        f"""
        <div class='sb-meta'>
        <b>Model</b>&nbsp;&nbsp; Cost-sensitive XGBoost<br>
        <b>Threshold</b>&nbsp;&nbsp; {threshold:.3f}<br>
        <b>Demo rows</b>&nbsp;&nbsp; {demo_data.shape[0]:,}<br>
        <b>Features</b>&nbsp;&nbsp; {demo_data.shape[1]}
        </div>
        """,
        unsafe_allow_html=True
    )



# Page 1: Home

if page == "Home / Project Summary":
    show_page_title(
        "🚦",
        "Road Casualty Severity Prediction",
        "A machine learning model trained on 2023 Great Britain STATS19 road safety data — predicting whether a casualty is likely to be Severe or Non-severe.",
        eyebrow="STATS19 · XGBoost · Binary Classification"
    )

    st.markdown(
        """
        <div class="hero-card">
        The final model is a tuned <b>cost-sensitive XGBoost classifier</b> built to handle class imbalance
        between severe and slight casualties. It uses casualty, vehicle, collision, and road-related features
        drawn from the STATS19 reporting system for Great Britain.
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Dataset", "STATS19", "GB road safety records")
    with col2:
        kpi_card("Model", "XGBoost", "Cost-sensitive classifier")
    with col3:
        kpi_card("Target", "Binary", "Severe vs Non-severe")
    with col4:
        kpi_card("Threshold", f"{threshold:.3f}", "Decision cut-off")

    st.markdown("<div class='section-title'>What's in this app</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        info_card(
            "🔍 Prediction demo",
            "Try individual saved examples or upload a preprocessed STATS19-style file for batch prediction."
        )
    with col2:
        info_card(
            "📊 Model performance",
            "View Macro-F1, Severe recall, ROC-AUC, and Average Precision on the held-out test set."
        )
    with col3:
        info_card(
            "🧠 Interpretability",
            "Explore grouped SHAP feature importance to understand the strongest drivers behind predictions."
        )

    st.markdown(
        """
        <div class="disclaimer-box">
        <b>Disclaimer</b> — This is an academic and portfolio demonstration only.
        It should not be used for legal, medical, emergency, policing, insurance,
        or road safety decision-making of any kind.
        </div>
        """,
        unsafe_allow_html=True
    )



# Page 2: Prediction Demo

elif page == "Prediction Demo":
    show_page_title(
        "🔍",
        "Prediction Demo",
        "Test the trained XGBoost model using built-in examples or upload your own preprocessed STATS19-style data.",
        eyebrow="Interactive · Single & Batch"
    )

    st.markdown(
        """
        <div class="warning-box">
        <b>Note</b> — This app does not clean raw STATS19 files automatically.
        Uploaded files must already be prepared in the same format as the demo input file.
        </div>
        """,
        unsafe_allow_html=True
    )

    tab_single, tab_upload = st.tabs(
        ["🎯 Single Demo Prediction", "📤 Batch Upload Prediction"]
    )

    # ── Single prediction ──────────────────────────────────────
    with tab_single:
        st.markdown("<div class='section-title'>Try a built-in demo sample</div>", unsafe_allow_html=True)

        col_a, col_b = st.columns([2, 1])
        with col_a:
            row_number = st.selectbox(
                "Choose a demo sample",
                options=list(range(len(demo_data))),
                format_func=lambda x: f"Sample {x}",
                key="single_demo_sample"
            )

        with col_b:
            kpi_card("Demo Dataset", f"{demo_data.shape[0]} × {demo_data.shape[1]}", "Rows × features")

        selected_row = demo_data.iloc[[row_number]]

        if st.button(
            "🚀 Run prediction",
            type="primary",
            use_container_width=True,
            key="run_single_prediction"
        ):
            try:
                prediction_result = predict_single_case_via_api(selected_row)

                st.session_state["single_prediction_result"] = prediction_result
                st.session_state["single_prediction_row"] = row_number

            except requests.RequestException as e:
                st.error("The prediction API could not complete the request.")
                st.exception(e)


        if (
            "single_prediction_result" in st.session_state
            and st.session_state.get("single_prediction_row") == row_number
        ):
            prediction_result = st.session_state["single_prediction_result"]

            severe_probability = prediction_result["severe_probability"]
            predicted_class = prediction_result["predicted_class"]

            predicted_label = (
                "Severe"
                if predicted_class == 1
                else "Non-severe"
            )

            st.markdown(
                "<div class='section-title'>Prediction result</div>",
                unsafe_allow_html=True
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                kpi_card(
                    "Severe Probability",
                    f"{severe_probability:.3f}",
                    "Model risk score"
                )

            with col2:
                kpi_card(
                    "Decision Threshold",
                    f"{prediction_result['classification_threshold']:.3f}",
                    "Probability cut-off"
                )

            with col3:
                kpi_card(
                    "Predicted Class",
                    predicted_label,
                    "Final model output"
                )

            severity_message(predicted_class)

            st.caption(
                f"Prediction ID: {prediction_result['prediction_id']} · "
                f"Model version: {prediction_result['model_version']}"
            )

        with st.expander("View input features for this sample"):
            st.dataframe(
                selected_row.T.rename(columns={row_number: "Value"}),
                use_container_width=True
            )

    # ── Batch upload ──────────────────────────────────────────
    with tab_upload:
        st.markdown("<div class='section-title'>Upload your own STATS19-style file</div>", unsafe_allow_html=True)

        st.write(
            "Upload a file with the same feature columns as the demo input. "
            "This works with another year of STATS19 data after the same preprocessing pipeline has been applied."
        )

        template_csv = demo_data.head(20).to_csv(index=False).encode("utf-8")

        col1, col2 = st.columns([1, 1])
        with col1:
            st.download_button(
                label="⬇️ Download input template",
                data=template_csv,
                file_name="stats19_input_template.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            if st.button("🧹 Clear batch results", use_container_width=True):
                st.session_state.pop("batch_results", None)
                st.session_state.pop("batch_prediction_done", None)
                st.session_state.pop("uploaded_file_signature", None)
                st.rerun()

        uploaded_file = st.file_uploader(
            "Upload a preprocessed STATS19-style file",
            type=["csv", "xls", "xlsx"]
        )

        if uploaded_file is not None:
            file_signature = f"{uploaded_file.name}_{uploaded_file.size}"

            if st.session_state.get("uploaded_file_signature") != file_signature:
                st.session_state.pop("batch_results", None)
                st.session_state.pop("batch_prediction_done", None)
                st.session_state["uploaded_file_signature"] = file_signature

            try:
                uploaded_data = load_uploaded_table(uploaded_file)

                st.markdown("<div class='section-title'>File check</div>", unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    kpi_card("Uploaded Rows", f"{uploaded_data.shape[0]:,}", "Records in file")
                with col2:
                    kpi_card("Uploaded Columns", uploaded_data.shape[1], "Input variables")
                with col3:
                    kpi_card("Expected Columns", demo_data.shape[1], "Model feature schema")

                with st.expander("Preview uploaded file"):
                    st.dataframe(uploaded_data.head(10), use_container_width=True)

                expected_columns = list(demo_data.columns)
                uploaded_columns = list(uploaded_data.columns)

                missing_columns = [col for col in expected_columns if col not in uploaded_columns]
                extra_columns = [col for col in uploaded_columns if col not in expected_columns]

                if missing_columns:
                    st.markdown(
                        "<div class='danger-box'><b>Column check failed</b> — the uploaded file is missing required columns.</div>",
                        unsafe_allow_html=True
                    )
                    st.write("Missing columns:")
                    st.write(missing_columns)

                else:
                    if extra_columns:
                        st.markdown(
                            "<div class='warning-box'><b>Extra columns detected</b> — these will be ignored during prediction.</div>",
                            unsafe_allow_html=True
                        )
                        with st.expander("View extra columns"):
                            st.write(extra_columns)

                    uploaded_model_input = uploaded_data[expected_columns]

                    st.markdown(
                        "<div class='success-box'><b>Column check passed</b> — the file is ready for prediction.</div>",
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "🚀 Run batch prediction",
                        type="primary",
                        use_container_width=True
                    ):
                        try:
                            api_result = predict_batch_via_api(
                                data=uploaded_model_input,
                                source_filename=uploaded_file.name,
                            )

                            batch_results = uploaded_model_input.copy()

                            probabilities = [
                                result["severe_probability"]
                                for result in api_result["results"]
                            ]

                            predicted_classes = [
                                "Severe"
                                if result["predicted_class"] == 1
                                else "Non-severe"
                                for result in api_result["results"]
                            ]

                            batch_results.insert(
                                0,
                                "predicted_class",
                                predicted_classes
                            )

                            batch_results.insert(
                                0,
                                "severe_probability",
                                probabilities
                            )

                            st.session_state["batch_results"] = batch_results
                            st.session_state["batch_prediction_done"] = True

                            st.session_state["batch_id"] = api_result["batch_id"]
                            st.session_state["batch_model_version"] = api_result["model_version"]

                        except requests.RequestException as e:
                            st.error("The batch prediction API could not complete the request.")
                            st.exception(e)

                    if st.session_state.get("batch_prediction_done", False):
                        batch_results = st.session_state["batch_results"]

                        total_rows, severe_count, non_severe_count, avg_probability, max_probability = create_prediction_summary(
                            batch_results
                        )

                        st.markdown(
                            "<div class='success-box'>Batch prediction completed.</div>",
                            unsafe_allow_html=True
                        )
                        st.caption(
                            f"Batch ID: {st.session_state['batch_id']} · "
                            f"Model version: {st.session_state['batch_model_version']}"
                        )

                        st.markdown("<div class='section-title'>Prediction summary</div>", unsafe_allow_html=True)

                        col1, col2, col3, col4, col5 = st.columns(5)

                        with col1:
                            kpi_card("Total Rows", f"{total_rows:,}")
                        with col2:
                            kpi_card("Predicted Severe", f"{severe_count:,}")
                        with col3:
                            kpi_card("Non-severe", f"{non_severe_count:,}")
                        with col4:
                            kpi_card("Avg. Probability", f"{avg_probability:.3f}")
                        with col5:
                            kpi_card("Peak Probability", f"{max_probability:.3f}")

                        st.divider()

                        st.markdown("<div class='section-title'>Risk distribution</div>", unsafe_allow_html=True)

                        risk_counts = batch_results["predicted_class"].value_counts().reset_index()
                        risk_counts.columns = ["Predicted Class", "Count"]

                        st.bar_chart(
                            risk_counts,
                            x="Predicted Class",
                            y="Count",
                            use_container_width=True
                        )

                        st.divider()

                        st.markdown("<div class='section-title'>Explore prediction results</div>", unsafe_allow_html=True)

                        probability_cutoff = st.slider(
                            "Show cases with Severe probability ≥",
                            min_value=0.0,
                            max_value=1.0,
                            value=float(threshold),
                            step=0.01,
                            key="probability_cutoff_slider"
                        )

                        filtered_results = batch_results[
                            batch_results["severe_probability"] >= probability_cutoff
                        ].copy()

                        st.write(
                            f"Showing **{len(filtered_results):,}** of **{len(batch_results):,}** cases "
                            f"with Severe probability ≥ **{probability_cutoff:.2f}**."
                        )

                        priority_cols = ["severe_probability", "predicted_class"]
                        other_cols = [col for col in filtered_results.columns if col not in priority_cols]
                        display_cols = priority_cols + other_cols

                        st.dataframe(
                            filtered_results[display_cols]
                            .sort_values(by="severe_probability", ascending=False)
                            .head(100),
                            use_container_width=True,
                            column_config={
                                "severe_probability": st.column_config.ProgressColumn(
                                    "Severe Probability",
                                    min_value=0.0,
                                    max_value=1.0,
                                    format="%.3f"
                                ),
                                "predicted_class": st.column_config.TextColumn("Predicted Class")
                            }
                        )

                        st.divider()

                        st.markdown("<div class='section-title'>Highest risk cases</div>", unsafe_allow_html=True)

                        max_top_n = max(1, min(50, len(batch_results)))

                        top_risk_n = st.slider(
                            "Number of highest-risk cases to display",
                            min_value=1,
                            max_value=max_top_n,
                            value=min(10, max_top_n),
                            key="top_risk_slider"
                        )

                        top_risk_cases = batch_results.sort_values(
                            by="severe_probability",
                            ascending=False
                        ).head(top_risk_n)

                        st.dataframe(
                            top_risk_cases[display_cols],
                            use_container_width=True,
                            column_config={
                                "severe_probability": st.column_config.ProgressColumn(
                                    "Severe Probability",
                                    min_value=0.0,
                                    max_value=1.0,
                                    format="%.3f"
                                ),
                                "predicted_class": st.column_config.TextColumn("Predicted Class")
                            }
                        )

                        results_csv = batch_results.to_csv(index=False).encode("utf-8")

                        st.download_button(
                            label="⬇️ Download full prediction results",
                            data=results_csv,
                            file_name="stats19_batch_predictions.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

            except Exception as e:
                st.error("The uploaded file could not be processed.")
                st.exception(e)



# Page 3: Model Performance

elif page == "Model Performance":
    show_page_title(
        "📊",
        "Model Performance",
        "Key test-set metrics for the final cost-sensitive XGBoost model.",
        eyebrow="Evaluation · Test Set"
    )

    macro_f1 = get_metric(metrics, ["macro_f1", "macro-F1", "Macro-F1", "f1_macro"])
    severe_recall = get_metric(metrics, ["severe_recall", "Severe recall", "recall_severe"])
    severe_precision = get_metric(metrics, ["severe_precision", "Severe precision", "precision_severe"])
    roc_auc = get_metric(metrics, ["roc_auc", "ROC-AUC", "roc_auc_score"])
    avg_precision = get_metric(metrics, ["average_precision", "Average precision", "avg_precision"])

    col1, col2, col3 = st.columns(3)

    with col1:
        kpi_card("Macro-F1", format_metric(macro_f1), "Balance across classes")
    with col2:
        kpi_card("Severe Recall", format_metric(severe_recall), "Detection of Severe class")
    with col3:
        kpi_card("Severe Precision", format_metric(severe_precision), "Correctness of Severe predictions")

    col4, col5, col6 = st.columns(3)

    with col4:
        kpi_card("ROC-AUC", format_metric(roc_auc), "Ranking performance")
    with col5:
        kpi_card("Average Precision", format_metric(avg_precision), "Precision-recall curve area")
    with col6:
        kpi_card("Decision Threshold", format_metric(threshold), "Final classification cut-off")

    st.divider()

    with st.expander("View raw metrics JSON"):
        st.json(metrics)

    if TEST_PREDICTIONS_PATH.exists():
        st.markdown("<div class='section-title'>Prediction output sample</div>", unsafe_allow_html=True)
        predictions = load_table(TEST_PREDICTIONS_PATH)
        st.dataframe(predictions.head(30), use_container_width=True)
    else:
        st.warning("test_predictions.xls was not found.")



# Page 4: SHAP Feature Importance

elif page == "SHAP Feature Importance":
    show_page_title(
        "🧠",
        "SHAP Feature Importance",
        "Grouped SHAP values showing which input features contributed most to the model's predictions.",
        eyebrow="Interpretability · Grouped SHAP"
    )

    if SHAP_GROUPED_PATH.exists():
        shap_df = load_table(SHAP_GROUPED_PATH)

        possible_feature_cols = [
            "feature", "grouped_feature", "original_feature", "Feature"
        ]
        possible_value_cols = [
            "mean_abs_shap", "mean_absolute_shap", "importance",
            "shap_importance", "Mean |SHAP|", "mean_abs_shap_value"
        ]

        feature_col = None
        value_col = None

        for col in possible_feature_cols:
            if col in shap_df.columns:
                feature_col = col
                break

        for col in possible_value_cols:
            if col in shap_df.columns:
                value_col = col
                break

        if feature_col is None:
            feature_col = shap_df.columns[0]

        if value_col is None:
            numeric_cols = shap_df.select_dtypes(include=np.number).columns.tolist()
            if numeric_cols:
                value_col = numeric_cols[0]

        if feature_col is not None and value_col is not None:
            col1, col2 = st.columns([1, 3])

            with col1:
                top_n = st.slider(
                    "Top features to show",
                    5,
                    min(30, len(shap_df)),
                    15
                )

            top_features = (
                shap_df[[feature_col, value_col]]
                .sort_values(by=value_col, ascending=False)
                .head(top_n)
                .set_index(feature_col)
            )

            st.markdown("<div class='section-title'>Top SHAP features</div>", unsafe_allow_html=True)
            st.bar_chart(top_features, use_container_width=True)

            with st.expander("View SHAP feature importance table"):
                st.dataframe(top_features, use_container_width=True)

            with st.expander("Preview raw SHAP file"):
                st.dataframe(shap_df.head(20), use_container_width=True)
        else:
            st.warning("Could not automatically identify SHAP feature and importance columns.")
    else:
        st.error("SHAP grouped feature importance file not found.")



# Page 5: Oversampling Sensitivity

elif page == "Oversampling Sensitivity":
    show_page_title(
        "⚖️",
        "Oversampling Sensitivity",
        "A supplementary experiment comparing cost-sensitive XGBoost with a RandomOverSampler variant.",
        eyebrow="Experiment · Supplementary"
    )

    st.markdown(
        """
        <div class="hero-card">
        This experiment tests whether oversampling the minority Severe class improves detection.
        The final project retained the cost-sensitive XGBoost model because RandomOverSampler did not
        meaningfully improve Severe-class recall.
        </div>
        """,
        unsafe_allow_html=True
    )

    if OVERSAMPLING_PATH.exists():
        oversampling_df = load_table(OVERSAMPLING_PATH)

        st.markdown("<div class='section-title'>Oversampling comparison</div>", unsafe_allow_html=True)
        st.dataframe(oversampling_df, use_container_width=True)

        st.markdown(
            """
            <div class="success-box">
            <b>Final decision</b> — Cost-sensitive XGBoost remains the selected model.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error("Oversampling sensitivity file not found.")



# Page 6: Limitations

elif page == "Limitations":
    show_page_title(
        "⚠️",
        "Limitations",
        "Important scope boundaries and responsible-use notes for this model.",
        eyebrow="Responsible AI · Scope"
    )

    col1, col2 = st.columns(2)

    with col1:
        info_card(
            "2023 data only",
            "The model was trained on a single year of STATS19 data and may not generalise well to other years or road conditions."
        )
        info_card(
            "Risk screening only",
            "Treat this as a risk-screening demonstration, not a definitive severity classifier or operational tool."
        )
        info_card(
            "Class imbalance",
            "Severe casualties are much less frequent than slight ones, making accurate prediction of the minority class inherently difficult."
        )

    with col2:
        info_card(
            "Calibration not fully assessed",
            "Predicted probabilities should not be interpreted as perfectly calibrated real-world risk estimates."
        )
        info_card(
            "Limited spatial detail",
            "More granular road, junction, traffic, and geospatial features could substantially improve future model performance."
        )
        info_card(
            "Portfolio demo",
            "This app must not be used for legal, clinical, emergency response, insurance, or policing decisions."
        )

    st.markdown(
        """
        <div class="danger-box">
        <b>Responsible use</b> — This app is for academic and portfolio demonstration only
        and is not intended for operational decision-making.
        </div>
        """,
        unsafe_allow_html=True
    )