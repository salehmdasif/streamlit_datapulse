"""
DataPulse — Universal Data Analytics Dashboard
Phase 1 + 2: Data Ingestion, Auto Cleaning, Profiling & EDA
Author: Abu Salah Mohammad Asif | Ravelweb Ltd
"""

import io
import streamlit as st
import pandas as pd
import numpy as np
from modules.cleaner  import DataCleaner
from modules.profiler import DataProfiler, DOMAIN_COLORS
from modules.eda      import (
    plot_correlation_heatmap,
    plot_distribution,
    plot_categorical_bar,
    plot_scatter,
    plot_group_comparison,
    plot_trend,
    plot_feature_importance,
    get_summary_stats,
)
from modules.analyzer import (
    correlation_analysis,
    group_comparison,
    trend_analysis,
    run_regression,
)
from modules.domain_insights import (
    MarketingInsights,
    SalesInsights,
    FinanceInsights,
    HRInsights,
)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataPulse",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ─ Base ─────────────────────────────────────────── */
html, body, [class*="css"], * {
    font-family: 'Inter', sans-serif !important;
    border-radius: 0 !important;
    box-sizing: border-box;
}

/* ─ Remove default Streamlit padding ────────────── */
.main .block-container {
    padding-top: 0 !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 1200px !important;
}

/* ─ Sidebar ──────────────────────────────────────── */
[data-testid="stSidebar"],
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
div[data-testid="stSidebarContent"] {
    background-color: #0d1117 !important;
}
section[data-testid="stSidebar"] {
    border-right: 1px solid #21262d !important;
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] small { color: #8b949e !important; }
section[data-testid="stSidebar"] strong,
section[data-testid="stSidebar"] b    { color: #e6edf3 !important; }
section[data-testid="stSidebar"] a    { color: #58a6ff !important; text-decoration: none !important; }
section[data-testid="stSidebar"] hr   { border: none !important; border-top: 1px solid #21262d !important; margin: 0.6rem 0 !important; }
section[data-testid="stSidebar"] .stButton > button {
    background-color: #21262d !important; color: #e6edf3 !important;
    border: 1px solid #30363d !important; width: 100% !important;
    font-size: 0.78rem !important; padding: 0.4rem 0.8rem !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #30363d !important; border-color: #58a6ff !important;
}

/* ─ Main Buttons ─────────────────────────────────── */
.stButton > button {
    background-color: #111827 !important;
    color: #ffffff !important;
    border: 1px solid #374151 !important;
    font-weight: 500 !important;
    font-size: 0.83rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.45rem 1.4rem !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background-color: #1f2937 !important;
    border-color: #9ca3af !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ─ Tabs ─────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0 !important;
    border-bottom: 1px solid #e5e7eb !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #9ca3af !important;
    padding: 0.55rem 1.2rem !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px !important;
}
.stTabs [aria-selected="true"] {
    color: #111827 !important;
    background: transparent !important;
    border-bottom: 2px solid #111827 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.2rem !important;
}

/* ─ File Uploader ────────────────────────────────── */
[data-testid="stFileUploadDropzone"] {
    border: 2px dashed #d1d5db !important;
    background: #fafafa !important;
    padding: 1.8rem !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #111827 !important;
    background: #f3f4f6 !important;
}
[data-testid="stFileUploadDropzone"] p {
    color: #6b7280 !important;
    font-size: 0.85rem !important;
}
/* Hide file uploader label entirely */
.stFileUploader > label,
[data-testid="stFileUploader"] > label,
[data-testid="stFileUploader"] [data-testid="InputInstructions"] {
    display: none !important;
}

/* ─ Text Input ───────────────────────────────────── */
.stTextInput input {
    border: 1px solid #e5e7eb !important;
    border-bottom: 2px solid #d1d5db !important;
    background: #fafafa !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 0.8rem !important;
    color: #111827 !important;
}
.stTextInput input:focus {
    border-bottom-color: #111827 !important;
    background: #ffffff !important;
    box-shadow: none !important;
}

/* ─ Selectbox ────────────────────────────────────── */
.stSelectbox > label { font-size: 0.78rem !important; color: #6b7280 !important; }
.stSelectbox [data-baseweb="select"] > div {
    border: 1px solid #e5e7eb !important;
    background: #fafafa !important;
    font-size: 0.82rem !important;
}
.stSelectbox [data-baseweb="select"] > div:focus-within {
    border-color: #111827 !important;
    box-shadow: none !important;
}

/* ─ Expander ─────────────────────────────────────── */
details[data-testid="stExpander"] {
    border: 1px solid #e5e7eb !important;
    background: #fafafa !important;
}
details[data-testid="stExpander"] summary {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: #374151 !important;
    padding: 0.7rem 1rem !important;
    background: #f3f4f6 !important;
}
details[data-testid="stExpander"] summary:hover {
    background: #e9ebef !important;
}

/* ─ Dataframe ────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #e5e7eb !important;
}
[data-testid="stDataFrame"] table {
    font-size: 0.8rem !important;
}

/* ─ Download Button ──────────────────────────────── */
[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 1.2rem !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #f3f4f6 !important;
    border-color: #111827 !important;
}

/* ─ Caption / small text ─────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #9ca3af !important;
    font-size: 0.75rem !important;
}

/* ─ Hide Streamlit chrome ────────────────────────── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Custom UI Components ──────────────────────────────────────────────────────

def notice(msg, kind="info"):
    """Custom notification box replacing st.success / st.error / st.info."""
    palette = {
        "success": ("#f0fdf4", "#16a34a", "#15803d", "✓"),
        "error":   ("#fef2f2", "#dc2626", "#991b1b", "✕"),
        "warning": ("#fffbeb", "#d97706", "#92400e", "!"),
        "info":    ("#f8fafc", "#374151", "#111827", "i"),
    }
    bg, border, text, icon = palette.get(kind, palette["info"])
    st.markdown(
        f"<div style='background:{bg};border-left:3px solid {border};"
        f"padding:0.7rem 1rem;margin:0.6rem 0;font-size:0.83rem;color:{text};'>"
        f"<strong>{icon}</strong> &nbsp;{msg}</div>",
        unsafe_allow_html=True
    )

def metric_row(items):
    """
    Render a row of custom metric cards.
    items: list of (label, value, delta_str_or_None, delta_positive_bool)
    """
    cols = st.columns(len(items))
    for col, (label, value, delta, good) in zip(cols, items):
        delta_html = ""
        if delta:
            color = "#16a34a" if good else "#dc2626"
            delta_html = (
                f"<div style='font-size:0.7rem;color:{color};"
                f"margin-top:0.15rem;font-weight:500;'>{delta}</div>"
            )
        col.markdown(
            f"<div style='border:1px solid #e5e7eb;padding:0.9rem 1.1rem;"
            f"background:#fafafa;'>"
            f"<div style='font-size:0.68rem;color:#9ca3af;font-weight:600;"
            f"letter-spacing:0.06em;text-transform:uppercase;'>{label}</div>"
            f"<div style='font-size:1.45rem;font-weight:700;color:#111827;"
            f"margin-top:0.2rem;line-height:1.2;'>{value}</div>"
            f"{delta_html}</div>",
            unsafe_allow_html=True
        )

def section_label(number, title, total=5):
    """Step label like  ── 02 / 05  CLEAN DATA ──"""
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:0.8rem;"
        f"margin:1.8rem 0 1rem;'>"
        f"<div style='font-size:0.7rem;font-weight:700;color:#9ca3af;"
        f"letter-spacing:0.12em;white-space:nowrap;'>{number:02d} / {total:02d}</div>"
        f"<div style='flex:1;height:1px;background:#e5e7eb;'></div>"
        f"<div style='font-size:0.7rem;font-weight:700;color:#111827;"
        f"letter-spacing:0.12em;text-transform:uppercase;'>{title}</div>"
        f"<div style='flex:1;height:1px;background:#e5e7eb;'></div>"
        f"</div>",
        unsafe_allow_html=True
    )


# ── Session State ─────────────────────────────────────────────────────────────
_defaults = {
    'raw_df':             None,
    'cleaned_df':         None,
    'cleaning_applied':   False,
    'cleaning_actions':   [],
    'original_shape':     None,
    'final_shape':        None,
    'missing_strategies': {},
    'outlier_strategies': {},
    'data_source':        None,
    # Phase 2
    'domain':             None,
    'quality_score':      None,
    'col_types':          None,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ── Helpers ───────────────────────────────────────────────────────────────────
def load_df(src, is_url=False):
    name = src if is_url else getattr(src, 'name', str(src))
    return pd.read_csv(src) if str(name).endswith('.csv') else pd.read_excel(src)

def reset_cleaning():
    st.session_state.update({
        'cleaning_applied': False, 'cleaned_df': None,
        'cleaning_actions': [], 'missing_strategies': {},
        'outlier_strategies': {},
    })


# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # Brand block
    st.markdown("""
    <div style='background:#161b22;padding:1.2rem 1rem 1rem;
                border-bottom:1px solid #21262d;margin:-1rem -1rem 0;'>
        <div style='font-size:1rem;font-weight:800;color:#e6edf3;
                    letter-spacing:0.02em;'>◈ DataPulse</div>
        <div style='font-size:0.7rem;color:#484f58;margin-top:0.2rem;
                    letter-spacing:0.04em;text-transform:uppercase;'>
            Analytics Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Pipeline tracker
    raw_loaded   = st.session_state.raw_df is not None
    clean_done   = st.session_state.cleaning_applied
    current_step = 1 + int(raw_loaded) + int(clean_done)

    STEPS = [
        (1, "Load Data"),
        (2, "Clean Data"),
        (3, "Profile & EDA"),
        (4, "Analysis"),
        (5, "Domain Insights"),
    ]

    st.markdown(
        "<div style='font-size:0.65rem;font-weight:700;color:#484f58;"
        "letter-spacing:0.1em;text-transform:uppercase;"
        "margin-bottom:0.6rem;'>Pipeline</div>",
        unsafe_allow_html=True
    )

    for num, label in STEPS:
        if num < current_step:
            dot_bg, dot_color, txt_color = "#1a7f37", "#fff", "#4b5563"
            dot_content, weight = "✓", "400"
        elif num == current_step:
            dot_bg, dot_color, txt_color = "#e6edf3", "#0d1117", "#e6edf3"
            dot_content, weight = str(num), "600"
        else:
            dot_bg, dot_color, txt_color = "#21262d", "#484f58", "#484f58"
            dot_content, weight = str(num), "400"

        st.markdown(
            f"<div style='display:flex;align-items:center;gap:0.6rem;"
            f"padding:0.3rem 0;'>"
            f"<div style='width:20px;height:20px;background:{dot_bg};"
            f"display:flex;align-items:center;justify-content:center;"
            f"font-size:0.6rem;font-weight:700;color:{dot_color};"
            f"flex-shrink:0;'>{dot_content}</div>"
            f"<span style='font-size:0.78rem;font-weight:{weight};"
            f"color:{txt_color};'>{label}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # Dataset info card
    if raw_loaded:
        df_info = st.session_state.raw_df
        st.markdown(
            f"<div style='background:#161b22;border:1px solid #21262d;"
            f"padding:0.8rem;font-size:0.78rem;'>"
            f"<div style='color:#484f58;font-size:0.65rem;font-weight:700;"
            f"letter-spacing:0.08em;text-transform:uppercase;"
            f"margin-bottom:0.5rem;'>Active Dataset</div>"
            f"<div style='color:#e6edf3;font-weight:600;margin-bottom:0.3rem;"
            f"word-break:break-all;'>{st.session_state.data_source}</div>"
            f"<div style='color:#8b949e;'>{df_info.shape[0]:,} rows "
            f"&nbsp;·&nbsp; {df_info.shape[1]} columns</div>"
            f"</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("Load New Dataset"):
            for k, v in _defaults.items():
                st.session_state[k] = v
            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.68rem;color:#484f58;padding:0.4rem 0;'>"
        "Built by <a href='https://linkedin.com/in/salehmdasif' "
        "style='color:#58a6ff;'>Mohammad Asif</a>"
        " &nbsp;·&nbsp; Ravelweb Ltd</div>",
        unsafe_allow_html=True
    )


# ═════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT — PAGE HEADER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style='padding:2rem 0 1.5rem;border-bottom:1px solid #f3f4f6;margin-bottom:0.5rem;'>
    <div style='display:flex;align-items:baseline;gap:0.8rem;'>
        <span style='font-size:1.6rem;font-weight:800;color:#111827;
                     letter-spacing:-0.02em;'>DataPulse</span>
        <span style='font-size:0.7rem;background:#111827;color:#fff;
                     padding:0.15rem 0.5rem;font-weight:600;
                     letter-spacing:0.06em;text-transform:uppercase;'>BETA</span>
    </div>
    <p style='color:#6b7280;font-size:0.88rem;margin:0.3rem 0 0;'>
        Upload any structured dataset — DataPulse cleans it, profiles it, and surfaces insights.
    </p>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# STEP 1 — LOAD DATA
# ═════════════════════════════════════════════════════════════════════════════
section_label(1, "Load Data")

tab_upload, tab_url, tab_sample = st.tabs(["  Upload File  ", "  Paste URL  ", "  Try Sample Data  "])

with tab_upload:
    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "x",
        type=["csv", "xls", "xlsx"],
        label_visibility="collapsed"
    )
    if uploaded_file is not None:
        try:
            df = load_df(uploaded_file)
            st.session_state.update(raw_df=df, data_source=uploaded_file.name)
            reset_cleaning()
            notice(f"Loaded <strong>{uploaded_file.name}</strong> &nbsp;·&nbsp; "
                   f"{df.shape[0]:,} rows × {df.shape[1]} columns", "success")
        except Exception as e:
            notice(f"Could not read file: {e}", "error")

with tab_url:
    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
    url_input = st.text_input(
        "url", placeholder="https://example.com/data.csv",
        label_visibility="collapsed"
    )
    st.caption("Direct link ending in .csv, .xls, or .xlsx")
    if st.button("Fetch from URL"):
        if not url_input.strip():
            notice("Paste a URL first.", "warning")
        else:
            try:
                df = load_df(url_input, is_url=True)
                st.session_state.update(raw_df=df, data_source="URL")
                reset_cleaning()
                notice(f"Loaded from URL &nbsp;·&nbsp; {df.shape[0]:,} rows × "
                       f"{df.shape[1]} columns", "success")
            except Exception as e:
                notice(f"Could not load: {e}", "error")

with tab_sample:
    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
    SAMPLES = {
        "Meta Ads Campaign Data - Marketing": "data/samples/sample_meta_ads.csv",
        "E-commerce Orders - Sales":          "data/samples/sample_sales.csv",
        "Monthly Budget Report - Finance":    "data/samples/sample_finance.csv",
        "Employee Records - HR":              "data/samples/sample_hr.csv",
    }

    # Sample cards
    cols = st.columns(4, gap="small")
    DOMAIN_INFO = [
        ("Marketing", "30 rows", "Currency types, missing ROAS, outlier spend"),
        ("Sales",     "30 rows", "Missing revenue, N/A prices, text columns"),
        ("Finance",   "30 rows", "Missing actuals, mixed types, outlier profit"),
        ("HR",        "35 rows", "Mixed attrition encoding, missing salary"),
    ]
    for col, (domain, size, issues) in zip(cols, DOMAIN_INFO):
        col.markdown(
            f"<div style='border:1px solid #e5e7eb;padding:0.8rem;background:#fafafa;"
            f"font-size:0.75rem;'>"
            f"<div style='font-weight:700;color:#111827;margin-bottom:0.3rem;'>{domain}</div>"
            f"<div style='color:#9ca3af;margin-bottom:0.4rem;'>{size}</div>"
            f"<div style='color:#6b7280;line-height:1.4;'>{issues}</div>"
            f"</div>",
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    selected_sample = st.selectbox(
        "Choose dataset", list(SAMPLES.keys()),
        label_visibility="collapsed"
    )
    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
    if st.button("Load Sample"):
            try:
                df = pd.read_csv(SAMPLES[selected_sample])
                src = selected_sample.split("—")[0].strip()
                st.session_state.update(raw_df=df, data_source=src)
                reset_cleaning()
                notice(f"Loaded <strong>{src}</strong> &nbsp;·&nbsp; "
                       f"{df.shape[0]:,} rows × {df.shape[1]} columns", "success")
            except Exception as e:
                notice(f"Could not load sample: {e}", "error")


# ═════════════════════════════════════════════════════════════════════════════
# STEP 2 — CLEAN DATA
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.raw_df is not None:
    raw_df = st.session_state.raw_df

    section_label(2, "Clean Data")

    # Raw preview
    with st.expander("Preview before cleaning"):
        st.dataframe(raw_df.head(10), use_container_width=True)
        st.caption(
            f"Memory usage: {raw_df.memory_usage(deep=True).sum() / 1024:.1f} KB  "
            f"·  dtypes: {dict(raw_df.dtypes.value_counts())}"
        )

    # Temp cleaner pass to detect issues
    _tmp = DataCleaner(raw_df)
    _tmp.normalize_column_names()
    _tmp.drop_all_null_columns()
    _tmp.drop_duplicates()
    _tmp.fix_data_types()

    missing_summary = _tmp.get_missing_summary()
    outlier_info    = _tmp.detect_outliers()

    # ── Auto-fix summary banner ────────────────────────────────────────────────
    auto_actions = _tmp.report.actions_taken
    if auto_actions:
        bullet_html = "".join(
            f"<div style='padding:0.15rem 0;color:#374151;font-size:0.8rem;'>"
            f"&nbsp;&nbsp;· {a}</div>"
            for a in auto_actions
        )
        st.markdown(
            f"<div style='border:1px solid #d1d5db;border-left:3px solid #374151;"
            f"background:#f9fafb;padding:0.8rem 1rem;margin-bottom:1rem;'>"
            f"<div style='font-size:0.72rem;font-weight:700;color:#374151;"
            f"letter-spacing:0.06em;text-transform:uppercase;margin-bottom:0.4rem;'>"
            f"Auto-fixes applied on load</div>"
            f"{bullet_html}</div>",
            unsafe_allow_html=True
        )

    # ── Missing Values ─────────────────────────────────────────────────────────
    if missing_summary:
        st.markdown(
            f"<div style='font-size:0.78rem;font-weight:700;color:#111827;"
            f"margin:1rem 0 0.4rem;'>Missing Values &nbsp;"
            f"<span style='background:#fef9c3;color:#854d0e;padding:0.1rem 0.5rem;"
            f"font-size:0.7rem;font-weight:600;'>{len(missing_summary)} column(s)</span></div>",
            unsafe_allow_html=True
        )
        st.caption("Choose a fill strategy for each column with missing data.")

        # Build table HTML
        rows_html = ""
        miss_strategies = {}
        for item in missing_summary:
            pct_width = min(item['missing_pct'], 100)
            rows_html += (
                f"<div style='display:grid;grid-template-columns:1fr 80px 100px;"
                f"gap:0.5rem;align-items:center;padding:0.45rem 0;"
                f"border-bottom:1px solid #f3f4f6;'>"
                f"<div style='font-size:0.8rem;font-weight:500;color:#111827;"
                f"font-family:monospace;'>{item['column']}</div>"
                f"<div>"
                f"<div style='height:4px;background:#f3f4f6;'>"
                f"<div style='height:4px;background:#f59e0b;width:{pct_width}%;'></div>"
                f"</div>"
                f"<div style='font-size:0.68rem;color:#9ca3af;margin-top:2px;'>"
                f"{item['missing_count']} ({item['missing_pct']}%)</div>"
                f"</div>"
                f"<div style='font-size:0.7rem;color:#6b7280;'>{item['dtype']}</div>"
                f"</div>"
            )

        st.markdown(
            f"<div style='border:1px solid #e5e7eb;padding:0.6rem 0.8rem;"
            f"background:#fff;margin-bottom:0.6rem;'>"
            f"<div style='display:grid;grid-template-columns:1fr 80px 100px;"
            f"gap:0.5rem;padding-bottom:0.4rem;border-bottom:2px solid #111827;'>"
            f"<div style='font-size:0.68rem;font-weight:700;color:#9ca3af;"
            f"text-transform:uppercase;letter-spacing:0.06em;'>Column</div>"
            f"<div style='font-size:0.68rem;font-weight:700;color:#9ca3af;"
            f"text-transform:uppercase;letter-spacing:0.06em;'>Missing</div>"
            f"<div style='font-size:0.68rem;font-weight:700;color:#9ca3af;"
            f"text-transform:uppercase;letter-spacing:0.06em;'>Type</div>"
            f"</div>{rows_html}</div>",
            unsafe_allow_html=True
        )

        # Strategy selectors
        n = len(missing_summary)
        ncols = min(n, 4)
        g = st.columns(ncols, gap="small")
        for i, item in enumerate(missing_summary):
            col_name = item['column']
            opts = (
                ["mean", "median", "mode", "drop"]
                if item['dtype'] == 'numeric' else ["mode", "drop"]
            )
            with g[i % ncols]:
                st.markdown(
                    f"<div style='font-size:0.72rem;font-weight:600;"
                    f"color:#374151;margin-bottom:0.2rem;"
                    f"font-family:monospace;'>{col_name}</div>",
                    unsafe_allow_html=True
                )
                chosen = st.selectbox(
                    col_name, opts,
                    key=f"miss_{col_name}",
                    label_visibility="collapsed"
                )
                miss_strategies[col_name] = chosen
        st.session_state.missing_strategies = miss_strategies
    else:
        notice("No missing values detected.", "success")

    # ── Outliers ───────────────────────────────────────────────────────────────
    if outlier_info:
        st.markdown(
            f"<div style='font-size:0.78rem;font-weight:700;color:#111827;"
            f"margin:1.2rem 0 0.4rem;'>Outliers Detected &nbsp;"
            f"<span style='background:#fef2f2;color:#991b1b;padding:0.1rem 0.5rem;"
            f"font-size:0.7rem;font-weight:600;'>{len(outlier_info)} column(s)</span></div>",
            unsafe_allow_html=True
        )
        st.caption("IQR method — values outside Q1 - 1.5×IQR or Q3 + 1.5×IQR")

        n = len(outlier_info)
        ncols = min(n, 4)
        g = st.columns(ncols, gap="small")
        out_strategies = {}

        for i, item in enumerate(outlier_info):
            with g[i % ncols]:
                st.markdown(
                    f"<div style='border:1px solid #fee2e2;background:#fef2f2;"
                    f"padding:0.7rem 0.8rem;margin-bottom:0.3rem;'>"
                    f"<div style='font-size:0.78rem;font-weight:700;color:#111827;"
                    f"font-family:monospace;'>{item['column']}</div>"
                    f"<div style='font-size:0.7rem;color:#ef4444;margin-top:0.2rem;'>"
                    f"{item['count']} outlier(s)</div>"
                    f"<div style='font-size:0.65rem;color:#9ca3af;margin-top:0.15rem;'>"
                    f"valid: [{item['lower_bound']}, {item['upper_bound']}]</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                chosen = st.selectbox(
                    "action", ["keep", "cap", "remove", "flag"],
                    key=f"out_{item['column']}",
                    label_visibility="collapsed"
                )
                out_strategies[item['column']] = chosen

        st.session_state.outlier_strategies = out_strategies
    else:
        notice("No significant outliers detected.", "success")

    # ── Apply Button ───────────────────────────────────────────────────────────
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 4])
    with c1:
        apply = st.button("Apply Cleaning")

    if apply:
        fc = DataCleaner(raw_df)
        fc.normalize_column_names()
        fc.drop_all_null_columns()
        fc.drop_duplicates()
        fc.fix_data_types()
        if st.session_state.missing_strategies:
            fc.handle_missing_values(st.session_state.missing_strategies)
        active_out = {k: v for k, v in st.session_state.outlier_strategies.items() if v != "keep"}
        if active_out:
            fc.handle_outliers(active_out)
        cleaned_df, report = fc.finalize()
        st.session_state.update(
            cleaned_df=cleaned_df,
            cleaning_applied=True,
            cleaning_actions=report.actions_taken,
            original_shape=report.original_shape,
            final_shape=report.final_shape,
        )
        st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# CLEANING REPORT
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.cleaning_applied and st.session_state.cleaned_df is not None:
    cleaned_df = st.session_state.cleaned_df
    orig    = st.session_state.original_shape
    final   = st.session_state.final_shape
    actions = st.session_state.cleaning_actions

    st.markdown(
        "<div style='height:1.5rem'></div>"
        "<div style='display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem;'>"
        "<div style='width:8px;height:8px;background:#16a34a;'></div>"
        "<span style='font-size:0.7rem;font-weight:700;color:#16a34a;"
        "letter-spacing:0.1em;text-transform:uppercase;'>Cleaning Complete</span>"
        "</div>",
        unsafe_allow_html=True
    )

    # Metric row
    metric_row([
        ("Original Rows",    f"{orig[0]:,}",    None, True),
        ("Rows After Clean", f"{final[0]:,}",   None, True),
        ("Original Columns", f"{orig[1]}",      None, True),
        ("Columns After",    f"{final[1]}",     None, True),
        ("Actions Taken",    f"{len(actions)}", None, True),
    ])

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Action log
    if actions:
        items_html = "".join(
            f"<div style='display:flex;gap:0.6rem;padding:0.4rem 0;"
            f"border-bottom:1px solid #f3f4f6;align-items:flex-start;'>"
            f"<div style='width:14px;height:14px;background:#16a34a;"
            f"display:flex;align-items:center;justify-content:center;"
            f"flex-shrink:0;margin-top:1px;'>"
            f"<span style='font-size:0.55rem;color:#fff;font-weight:700;'>✓</span></div>"
            f"<span style='font-size:0.81rem;color:#374151;'>{a}</span></div>"
            for a in actions
        )
        st.markdown(
            f"<div style='border:1px solid #e5e7eb;padding:0.8rem 1rem;"
            f"background:#fafafa;'>"
            f"<div style='font-size:0.68rem;font-weight:700;color:#9ca3af;"
            f"letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.5rem;'>"
            f"Action Log</div>"
            f"{items_html}</div>",
            unsafe_allow_html=True
        )
    else:
        notice("Data was already clean — no changes were needed.", "success")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Cleaned data preview
    st.markdown(
        "<div style='font-size:0.78rem;font-weight:700;color:#111827;"
        "margin-bottom:0.5rem;'>Cleaned Dataset</div>",
        unsafe_allow_html=True
    )
    st.dataframe(cleaned_df.head(10), use_container_width=True)
    st.caption(
        f"Shape: {cleaned_df.shape[0]:,} rows × {cleaned_df.shape[1]} columns  "
        f"·  Memory: {cleaned_df.memory_usage(deep=True).sum() / 1024:.1f} KB"
    )

    # Download
    _buf = io.StringIO()
    cleaned_df.to_csv(_buf, index=False)
    st.download_button(
        label="Download Cleaned CSV",
        data=_buf.getvalue(),
        file_name="datapulse_cleaned.csv",
        mime="text/csv"
    )

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 3 — PROFILE & EDA
    # ═══════════════════════════════════════════════════════════════════════
    section_label(3, "Profile & EDA")

    profiler = DataProfiler(cleaned_df)

    # Run profiler
    domain, match_count = profiler.detect_domain()
    q_score             = profiler.quality_score()
    col_types           = profiler.classify_columns()
    col_stats           = profiler.column_stats()

    st.session_state.update(domain=domain, quality_score=q_score, col_types=col_types)

    # ── Domain + Quality row ───────────────────────────────────────────────
    dom_bg, dom_border, dom_tag = DOMAIN_COLORS.get(domain, DOMAIN_COLORS["General"])
    q_color = "#16a34a" if q_score >= 80 else "#d97706" if q_score >= 55 else "#dc2626"

    c_dom, c_score, c_rows, c_cols, c_num, c_cat = st.columns(6, gap="small")

    c_dom.markdown(
        f"<div style='border:1px solid {dom_border};background:{dom_bg};"
        f"padding:0.9rem 1rem;'>"
        f"<div style='font-size:0.65rem;font-weight:700;color:#9ca3af;"
        f"letter-spacing:0.06em;text-transform:uppercase;'>Domain</div>"
        f"<div style='font-size:0.82rem;font-weight:700;color:{dom_border};"
        f"margin-top:0.25rem;'>{domain}</div>"
        f"<div style='font-size:0.65rem;color:#9ca3af;margin-top:0.1rem;'>"
        f"{match_count} keyword match{'es' if match_count != 1 else ''}</div>"
        f"</div>",
        unsafe_allow_html=True
    )
    c_score.markdown(
        f"<div style='border:1px solid #e5e7eb;background:#fafafa;"
        f"padding:0.9rem 1rem;'>"
        f"<div style='font-size:0.65rem;font-weight:700;color:#9ca3af;"
        f"letter-spacing:0.06em;text-transform:uppercase;'>Quality Score</div>"
        f"<div style='font-size:1.3rem;font-weight:800;color:{q_color};"
        f"margin-top:0.25rem;'>{q_score}<span style='font-size:0.7rem;"
        f"font-weight:500;color:#9ca3af;'> / 100</span></div>"
        f"</div>",
        unsafe_allow_html=True
    )

    num_cols = sum(1 for t in col_types.values() if t == 'numeric')
    cat_cols = sum(1 for t in col_types.values() if t == 'categorical')
    dt_cols  = sum(1 for t in col_types.values() if t == 'datetime')
    id_cols  = sum(1 for t in col_types.values() if t == 'id_text')

    for col_widget, label, val in [
        (c_rows, "Rows",       f"{cleaned_df.shape[0]:,}"),
        (c_cols, "Columns",    f"{cleaned_df.shape[1]}"),
        (c_num,  "Numeric",    f"{num_cols}"),
        (c_cat,  "Categorical",f"{cat_cols}"),
    ]:
        col_widget.markdown(
            f"<div style='border:1px solid #e5e7eb;background:#fafafa;"
            f"padding:0.9rem 1rem;'>"
            f"<div style='font-size:0.65rem;font-weight:700;color:#9ca3af;"
            f"letter-spacing:0.06em;text-transform:uppercase;'>{label}</div>"
            f"<div style='font-size:1.3rem;font-weight:800;color:#111827;"
            f"margin-top:0.25rem;'>{val}</div>"
            f"</div>",
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    # ── Column Profile Table ───────────────────────────────────────────────
    TYPE_STYLE = {
        'numeric':     ("#eff6ff", "#2563eb"),
        'categorical': ("#f0fdf4", "#16a34a"),
        'datetime':    ("#fdf4ff", "#9333ea"),
        'boolean':     ("#fefce8", "#ca8a04"),
        'id_text':     ("#f8fafc", "#6b7280"),
        'text':        ("#f8fafc", "#6b7280"),
        'other':       ("#f8fafc", "#6b7280"),
    }

    header_html = (
        "<div style='display:grid;"
        "grid-template-columns:1.8fr 0.9fr 0.7fr 0.7fr 0.7fr 1.5fr;"
        "gap:0.4rem;padding:0.4rem 0.8rem;"
        "border-bottom:2px solid #111827;margin-bottom:0.2rem;'>"
        + "".join(
            f"<div style='font-size:0.65rem;font-weight:700;color:#9ca3af;"
            f"text-transform:uppercase;letter-spacing:0.06em;'>{h}</div>"
            for h in ["Column", "Type", "Missing", "Unique", "Miss %", "Sample"]
        )
        + "</div>"
    )

    rows_html = ""
    for stat in col_stats:
        bg, fg = TYPE_STYLE.get(stat['type'], ("#f8fafc", "#6b7280"))
        rows_html += (
            f"<div style='display:grid;"
            f"grid-template-columns:1.8fr 0.9fr 0.7fr 0.7fr 0.7fr 1.5fr;"
            f"gap:0.4rem;padding:0.35rem 0.8rem;"
            f"border-bottom:1px solid #f3f4f6;align-items:center;'>"
            f"<div style='font-size:0.8rem;font-weight:500;color:#111827;"
            f"font-family:monospace;'>{stat['column']}</div>"
            f"<div><span style='background:{bg};color:{fg};"
            f"font-size:0.65rem;font-weight:600;padding:0.1rem 0.45rem;"
            f"letter-spacing:0.04em;'>{stat['type']}</span></div>"
            f"<div style='font-size:0.78rem;color:#6b7280;'>{stat['missing']}</div>"
            f"<div style='font-size:0.78rem;color:#6b7280;'>{stat['unique']}</div>"
            f"<div style='font-size:0.78rem;color:"
            f"{'#dc2626' if stat['miss_pct'] > 20 else '#6b7280'};'>"
            f"{stat['miss_pct']}%</div>"
            f"<div style='font-size:0.75rem;color:#9ca3af;"
            f"font-family:monospace;overflow:hidden;text-overflow:ellipsis;"
            f"white-space:nowrap;'>{stat['sample']}</div>"
            f"</div>"
        )

    st.markdown(
        f"<div style='border:1px solid #e5e7eb;background:#fff;'>"
        f"{header_html}{rows_html}</div>",
        unsafe_allow_html=True
    )

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── EDA Tabs ───────────────────────────────────────────────────────────
    numeric_cols = [c for c, t in col_types.items() if t == 'numeric']
    cat_cols_list = [c for c, t in col_types.items() if t == 'categorical']

    eda_summary, eda_corr, eda_dist, eda_cat = st.tabs([
        "  Summary Stats  ",
        "  Correlation Heatmap  ",
        "  Distributions  ",
        "  Categories  ",
    ])

    # ── Summary Stats ──────────────────────────────────────────────────────
    with eda_summary:
        stats_df = get_summary_stats(cleaned_df)
        if stats_df.empty:
            notice("No numeric columns found for summary statistics.", "warning")
        else:
            st.dataframe(stats_df, use_container_width=True)
            st.caption(
                "Showing statistics for numeric columns only. "
                "Count = non-null values per column."
            )

    # ── Correlation Heatmap ────────────────────────────────────────────────
    with eda_corr:
        if len(numeric_cols) < 2:
            notice("Need at least 2 numeric columns for correlation analysis.", "warning")
        else:
            fig_corr = plot_correlation_heatmap(cleaned_df)
            if fig_corr:
                st.markdown(
                    "<div style='font-size:0.75rem;color:#6b7280;margin-bottom:0.5rem;'>"
                    "Pearson correlation · Red = positive · Blue = negative · "
                    "Values close to ±1 = strong relationship</div>",
                    unsafe_allow_html=True
                )
                st.plotly_chart(fig_corr, use_container_width=True)

                # Top correlations
                num_df  = cleaned_df[numeric_cols].dropna(axis=1, how="all")
                corr_m  = num_df.corr().abs()
                pairs   = (
                    corr_m.where(
                        pd.DataFrame(
                            np.tril(np.ones(corr_m.shape), k=-1).astype(bool),
                            index=corr_m.index, columns=corr_m.columns
                        )
                    )
                    .stack()
                    .sort_values(ascending=False)
                    .head(5)
                )
                if not pairs.empty:
                    st.markdown(
                        "<div style='font-size:0.72rem;font-weight:700;color:#6b7280;"
                        "text-transform:uppercase;letter-spacing:0.06em;"
                        "margin:0.8rem 0 0.4rem;'>Top 5 Strongest Correlations</div>",
                        unsafe_allow_html=True
                    )
                    for (c1, c2), val in pairs.items():
                        raw_val = num_df[[c1, c2]].dropna()
                        direction = "positive" if raw_val.corr().iloc[0, 1] > 0 else "negative"
                        strength  = "strong" if val > 0.7 else "moderate" if val > 0.4 else "weak"
                        col_a = "#ef4444" if direction == "positive" else "#2563eb"
                        st.markdown(
                            f"<div style='display:flex;align-items:center;gap:0.6rem;"
                            f"padding:0.3rem 0;border-bottom:1px solid #f3f4f6;'>"
                            f"<span style='font-family:monospace;font-size:0.78rem;"
                            f"color:#111827;'>{c1}</span>"
                            f"<span style='color:#9ca3af;'>↔</span>"
                            f"<span style='font-family:monospace;font-size:0.78rem;"
                            f"color:#111827;'>{c2}</span>"
                            f"<span style='margin-left:auto;font-size:0.72rem;"
                            f"color:{col_a};font-weight:600;'>{val:.2f}</span>"
                            f"<span style='font-size:0.68rem;color:#9ca3af;'>"
                            f"{strength} {direction}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

    # ── Distribution Explorer ──────────────────────────────────────────────
    with eda_dist:
        if not numeric_cols:
            notice("No numeric columns found.", "warning")
        else:
            sel_col = st.selectbox(
                "Select numeric column",
                numeric_cols,
                label_visibility="collapsed"
            )
            if sel_col:
                data_series = cleaned_df[sel_col].dropna()

                # Stats strip
                s1, s2, s3, s4, s5 = st.columns(5, gap="small")
                for widget, lbl, val in [
                    (s1, "Mean",   f"{data_series.mean():.2f}"),
                    (s2, "Median", f"{data_series.median():.2f}"),
                    (s3, "Std",    f"{data_series.std():.2f}"),
                    (s4, "Min",    f"{data_series.min():.2f}"),
                    (s5, "Max",    f"{data_series.max():.2f}"),
                ]:
                    widget.markdown(
                        f"<div style='border:1px solid #e5e7eb;padding:0.55rem 0.7rem;"
                        f"background:#fafafa;text-align:center;'>"
                        f"<div style='font-size:0.62rem;font-weight:700;color:#9ca3af;"
                        f"text-transform:uppercase;letter-spacing:0.05em;'>{lbl}</div>"
                        f"<div style='font-size:1rem;font-weight:700;color:#111827;"
                        f"margin-top:0.15rem;'>{val}</div></div>",
                        unsafe_allow_html=True
                    )

                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
                st.plotly_chart(
                    plot_distribution(cleaned_df, sel_col),
                    use_container_width=True
                )
                st.caption(
                    f"{len(data_series):,} non-null values · "
                    f"Skewness: {data_series.skew():.2f} · "
                    f"Kurtosis: {data_series.kurtosis():.2f}"
                )

    # ── Category Explorer ──────────────────────────────────────────────────
    with eda_cat:
        if not cat_cols_list:
            notice("No categorical columns detected in this dataset.", "warning")
        else:
            sel_cat = st.selectbox(
                "Select categorical column",
                cat_cols_list,
                label_visibility="collapsed"
            )
            if sel_cat:
                counts     = cleaned_df[sel_cat].value_counts()
                n_unique   = len(counts)
                top_val    = counts.index[0]
                top_pct    = round(counts.iloc[0] / len(cleaned_df) * 100, 1)

                ca, cb, cc = st.columns(3, gap="small")
                for w, lbl, val in [
                    (ca, "Unique Values", str(n_unique)),
                    (cb, "Top Value",     str(top_val)[:18]),
                    (cc, "Top Value %",   f"{top_pct}%"),
                ]:
                    w.markdown(
                        f"<div style='border:1px solid #e5e7eb;padding:0.55rem 0.7rem;"
                        f"background:#fafafa;'>"
                        f"<div style='font-size:0.62rem;font-weight:700;color:#9ca3af;"
                        f"text-transform:uppercase;letter-spacing:0.05em;'>{lbl}</div>"
                        f"<div style='font-size:1rem;font-weight:700;color:#111827;"
                        f"margin-top:0.15rem;'>{val}</div></div>",
                        unsafe_allow_html=True
                    )

                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
                st.plotly_chart(
                    plot_categorical_bar(cleaned_df, sel_cat),
                    use_container_width=True
                )

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 4 — ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════
    section_label(4, "Analysis")

    datetime_cols = [c for c, t in col_types.items() if t == 'datetime']

    tab_labels = ["  Correlation  ", "  Group Comparison  ", "  Regression  "]
    if datetime_cols:
        tab_labels.insert(2, "  Trend Analysis  ")

    tabs_4 = st.tabs(tab_labels)
    tab_corr = tabs_4[0]
    tab_grp  = tabs_4[1]
    tab_reg  = tabs_4[-1]
    tab_trnd = tabs_4[2] if datetime_cols else None

    # ── Correlation Analysis ───────────────────────────────────────────────
    with tab_corr:
        if len(numeric_cols) < 2:
            notice("Need at least 2 numeric columns.", "warning")
        else:
            c1, c2, c3 = st.columns([1, 1, 2], gap="large")
            with c1:
                x_col = st.selectbox("X Axis", numeric_cols, key="corr_x")
            with c2:
                y_options = [c for c in numeric_cols if c != x_col]
                y_col = st.selectbox("Y Axis", y_options, key="corr_y")
            with c3:
                st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)
                run_corr = st.button("Run Correlation")

            if run_corr or (x_col and y_col):
                result = correlation_analysis(cleaned_df, x_col, y_col)
                if result:
                    # Result cards
                    rc1, rc2, rc3, rc4 = st.columns(4, gap="small")
                    r_color = "#16a34a" if result['r'] > 0 else "#dc2626"
                    sig_color = "#16a34a" if result['significant'] else "#d97706"
                    for w, lbl, val, color in [
                        (rc1, "Pearson r",   f"{result['r']:.4f}",      r_color),
                        (rc2, "R² Score",    f"{result['r_squared']:.4f}", "#111827"),
                        (rc3, "p-Value",     f"{result['p_value']:.4f}", sig_color),
                        (rc4, "Sample Size", f"{result['n']:,}",          "#111827"),
                    ]:
                        w.markdown(
                            f"<div style='border:1px solid #e5e7eb;padding:0.9rem 1rem;"
                            f"background:#fafafa;'>"
                            f"<div style='font-size:0.65rem;font-weight:700;color:#9ca3af;"
                            f"letter-spacing:0.06em;text-transform:uppercase;'>{lbl}</div>"
                            f"<div style='font-size:1.35rem;font-weight:800;color:{color};"
                            f"margin-top:0.2rem;'>{val}</div></div>",
                            unsafe_allow_html=True
                        )

                    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

                    # Interpretation banner
                    sig_txt = "statistically significant (p < 0.05)" if result['significant'] else "not statistically significant (p ≥ 0.05)"
                    banner_color = "#f0fdf4" if result['significant'] else "#fffbeb"
                    border_color = "#16a34a" if result['significant'] else "#d97706"
                    st.markdown(
                        f"<div style='border-left:3px solid {border_color};"
                        f"background:{banner_color};padding:0.7rem 1rem;"
                        f"font-size:0.83rem;color:#374151;'>"
                        f"<strong>{result['strength']} {result['direction'].lower()} correlation</strong> "
                        f"between <code>{x_col}</code> and <code>{y_col}</code>. "
                        f"This relationship is <strong>{sig_txt}</strong>. "
                        f"R² = {result['r_squared']:.4f} means <code>{x_col}</code> explains "
                        f"<strong>{result['r_squared']*100:.1f}%</strong> of the variance in <code>{y_col}</code>."
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
                    st.plotly_chart(
                        plot_scatter(cleaned_df, x_col, y_col),
                        use_container_width=True
                    )

    # ── Group Comparison ───────────────────────────────────────────────────
    with tab_grp:
        if not cat_cols_list or not numeric_cols:
            notice("Need at least 1 categorical and 1 numeric column.", "warning")
        else:
            g1, g2, g3, g4 = st.columns([1, 1, 1, 1], gap="small")
            with g1:
                grp_cat = st.selectbox("Group by (categorical)", cat_cols_list, key="grp_cat")
            with g2:
                grp_num = st.selectbox("Measure (numeric)", numeric_cols, key="grp_num")
            with g3:
                grp_agg = st.selectbox("Aggregation", ["mean", "sum", "median", "count"], key="grp_agg")
            with g4:
                st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)
                run_grp = st.button("Compare Groups")

            if run_grp or grp_cat:
                grp_result = group_comparison(cleaned_df, grp_cat, grp_num, grp_agg)
                if grp_result is not None and len(grp_result) > 0:
                    col_l, col_r = st.columns([2, 1], gap="large")
                    with col_l:
                        st.plotly_chart(
                            plot_group_comparison(grp_result, grp_cat, grp_num, grp_agg),
                            use_container_width=True
                        )
                    with col_r:
                        st.markdown(
                            "<div style='font-size:0.68rem;font-weight:700;color:#9ca3af;"
                            "text-transform:uppercase;letter-spacing:0.06em;"
                            "margin-bottom:0.5rem;'>Values Table</div>",
                            unsafe_allow_html=True
                        )
                        tbl = grp_result.reset_index()
                        tbl.columns = [grp_cat, f"{grp_agg}({grp_num})"]
                        tbl[f"{grp_agg}({grp_num})"] = tbl[f"{grp_agg}({grp_num})"].round(2)
                        st.dataframe(tbl, use_container_width=True, hide_index=True)

    # ── Trend Analysis ─────────────────────────────────────────────────────
    if tab_trnd is not None:
        with tab_trnd:
            t1, t2, t3 = st.columns([1, 1, 1], gap="small")
            with t1:
                trnd_date = st.selectbox("Date column", datetime_cols, key="trnd_date")
            with t2:
                trnd_val = st.selectbox("Metric", numeric_cols, key="trnd_val")
            with t3:
                rolling_w = st.selectbox("Rolling window", [3, 7, 14, 30], index=1, key="trnd_roll")

            if trnd_date and trnd_val:
                trnd_df = trend_analysis(cleaned_df, trnd_date, trnd_val, rolling_w)
                if len(trnd_df) > 0:
                    st.plotly_chart(plot_trend(trnd_df, trnd_date, trnd_val), use_container_width=True)
                    st.caption(f"{len(trnd_df)} data points · {rolling_w}-period rolling average (red dashed)")

    # ── Linear Regression ──────────────────────────────────────────────────
    with tab_reg:
        if len(numeric_cols) < 2:
            notice("Need at least 2 numeric columns for regression.", "warning")
        else:
            r1, r2 = st.columns([1, 2], gap="large")
            with r1:
                reg_target = st.selectbox(
                    "Target variable (Y)", numeric_cols, key="reg_target"
                )
            with r2:
                feat_options = [c for c in numeric_cols if c != reg_target]
                reg_features = st.multiselect(
                    "Feature columns (X) — select one or more",
                    feat_options, key="reg_features"
                )

            st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
            run_reg = st.button("Run Regression")

            if run_reg:
                if not reg_features:
                    notice("Select at least one feature column.", "warning")
                else:
                    reg_result = run_regression(cleaned_df, reg_target, reg_features)
                    if reg_result is None:
                        notice("Not enough data to run regression (need ≥ 5 rows).", "error")
                    else:
                        # Model score cards
                        rs1, rs2, rs3, rs4, rs5 = st.columns(5, gap="small")
                        r2_color = "#16a34a" if reg_result['r2'] >= 0.7 else "#d97706" if reg_result['r2'] >= 0.4 else "#dc2626"
                        fp_color = "#16a34a" if reg_result['f_pvalue'] < 0.05 else "#dc2626"
                        for w, lbl, val, color in [
                            (rs1, "R² Score",    f"{reg_result['r2']:.4f}",     r2_color),
                            (rs2, "Adj. R²",     f"{reg_result['adj_r2']:.4f}", r2_color),
                            (rs3, "F p-Value",   f"{reg_result['f_pvalue']:.4f}", fp_color),
                            (rs4, "Sample Size", f"{reg_result['n']:,}",         "#111827"),
                            (rs5, "AIC",         f"{reg_result['aic']:.1f}",     "#111827"),
                        ]:
                            w.markdown(
                                f"<div style='border:1px solid #e5e7eb;padding:0.9rem 1rem;"
                                f"background:#fafafa;'>"
                                f"<div style='font-size:0.65rem;font-weight:700;color:#9ca3af;"
                                f"letter-spacing:0.06em;text-transform:uppercase;'>{lbl}</div>"
                                f"<div style='font-size:1.35rem;font-weight:800;color:{color};"
                                f"margin-top:0.2rem;'>{val}</div></div>",
                                unsafe_allow_html=True
                            )

                        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

                        col_fi, col_ht = st.columns([1, 1], gap="large")

                        with col_fi:
                            st.markdown(
                                "<div style='font-size:0.72rem;font-weight:700;color:#6b7280;"
                                "text-transform:uppercase;letter-spacing:0.06em;"
                                "margin-bottom:0.5rem;'>Feature Importance</div>",
                                unsafe_allow_html=True
                            )
                            st.plotly_chart(
                                plot_feature_importance(reg_result['coef_df']),
                                use_container_width=True
                            )
                            st.caption("Standardised coefficients — larger absolute value = more influence on target")

                        with col_ht:
                            st.markdown(
                                "<div style='font-size:0.72rem;font-weight:700;color:#6b7280;"
                                "text-transform:uppercase;letter-spacing:0.06em;"
                                "margin-bottom:0.5rem;'>Hypothesis Testing</div>",
                                unsafe_allow_html=True
                            )
                            st.caption("p < 0.05 = statistically significant feature")

                            hyp = reg_result['hyp_df']
                            for _, row in hyp.iterrows():
                                sig   = row['Significant']
                                color = "#16a34a" if sig else "#9ca3af"
                                badge = "significant" if sig else "not significant"
                                st.markdown(
                                    f"<div style='border:1px solid #e5e7eb;"
                                    f"border-left:3px solid {color};"
                                    f"padding:0.5rem 0.8rem;margin-bottom:0.4rem;"
                                    f"background:#fafafa;'>"
                                    f"<div style='display:flex;justify-content:space-between;"
                                    f"align-items:center;'>"
                                    f"<span style='font-family:monospace;font-size:0.78rem;"
                                    f"font-weight:600;color:#111827;'>{row['Feature']}</span>"
                                    f"<span style='font-size:0.65rem;font-weight:700;"
                                    f"color:{color};text-transform:uppercase;"
                                    f"letter-spacing:0.04em;'>{badge}</span></div>"
                                    f"<div style='font-size:0.72rem;color:#6b7280;"
                                    f"margin-top:0.3rem;'>"
                                    f"coef: <b>{row['Coefficient']}</b> &nbsp;·&nbsp; "
                                    f"p: <b>{row['p-Value']}</b> &nbsp;·&nbsp; "
                                    f"t: {row['t-Statistic']} &nbsp;·&nbsp; "
                                    f"CI: [{row['CI Lower']}, {row['CI Upper']}]"
                                    f"</div></div>",
                                    unsafe_allow_html=True
                                )

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 5 — DOMAIN INSIGHTS
    # ═══════════════════════════════════════════════════════════════════════
    section_label(5, "Domain Insights")

    domain = st.session_state.get("domain", "General")
    dom_bg, dom_border, _ = DOMAIN_COLORS.get(domain, DOMAIN_COLORS["General"])

    st.markdown(
        f"<div style='display:inline-flex;align-items:center;gap:0.5rem;"
        f"border:1px solid {dom_border};background:{dom_bg};"
        f"padding:0.35rem 0.8rem;margin-bottom:1rem;'>"
        f"<span style='font-size:0.7rem;font-weight:700;color:{dom_border};"
        f"text-transform:uppercase;letter-spacing:0.06em;'>Detected Domain</span>"
        f"<span style='font-size:0.82rem;font-weight:700;color:{dom_border};'>"
        f"{domain}</span></div>",
        unsafe_allow_html=True
    )

    # ── MARKETING / ADS ────────────────────────────────────────────────────
    if "Marketing" in domain:
        mi = MarketingInsights(cleaned_df)
        kpis = mi.key_metrics_summary()

        # KPI cards
        kpi_items = [
            ("Total Spend",       f"${kpis.get('total_spend', 0):,.2f}"   if kpis.get('total_spend') else "—"),
            ("Avg ROAS",          f"{kpis.get('avg_roas', 0):.2f}x"       if kpis.get('avg_roas') else "—"),
            ("Avg CTR",           f"{kpis.get('avg_ctr', 0):.2f}%"        if kpis.get('avg_ctr') else "—"),
            ("Avg CPC",           f"${kpis.get('avg_cpc', 0):.2f}"        if kpis.get('avg_cpc') else "—"),
            ("Avg CPR",           f"${kpis.get('avg_cpr', 0):.2f}"        if kpis.get('avg_cpr') else "—"),
            ("Avg Result Rate",   f"{kpis.get('avg_result_rate', 0):.1f}%" if kpis.get('avg_result_rate') else "—"),
        ]
        kpi_items = [(l, v) for l, v in kpi_items if v != "—"]

        if kpi_items:
            n = len(kpi_items)
            kpi_cols = st.columns(min(n, 6), gap="small")
            for col_w, (lbl, val) in zip(kpi_cols, kpi_items):
                col_w.markdown(
                    f"<div style='border:1px solid #e5e7eb;padding:0.9rem 1rem;background:#fafafa;'>"
                    f"<div style='font-size:0.65rem;font-weight:700;color:#9ca3af;"
                    f"letter-spacing:0.06em;text-transform:uppercase;'>{lbl}</div>"
                    f"<div style='font-size:1.2rem;font-weight:800;color:#111827;"
                    f"margin-top:0.2rem;'>{val}</div></div>",
                    unsafe_allow_html=True
                )

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        # Winning Ads selector with sliders
        st.markdown(
            "<div style='font-size:0.78rem;font-weight:700;color:#111827;"
            "margin-bottom:0.3rem;'>Winning Ad Selector</div>"
            "<div style='font-size:0.75rem;color:#6b7280;margin-bottom:0.8rem;'>"
            "Adjust thresholds — only ads meeting ALL criteria are shown.</div>",
            unsafe_allow_html=True
        )

        col_s1, col_s2, col_s3 = st.columns(3, gap="large")
        with col_s1:
            min_spend  = st.slider("Min Spend ($)",        0,   1000, 100,  50,  key="w_spend")
            min_roas   = st.slider("Min ROAS",             0.0,  8.0, 2.0, 0.5, key="w_roas")
            min_ctr    = st.slider("Min CTR (%)",          0.0,  5.0, 2.0, 0.5, key="w_ctr")
        with col_s2:
            min_res    = st.slider("Min Result Rate (%)",  0,    50,  20,   5,   key="w_res")
            min_scroll = st.slider("Min Scroll Stop (%)",  0,    60,  25,   5,   key="w_scroll")
            min_hook   = st.slider("Min Hook Rate (%)",    0,    60,  30,   5,   key="w_hook")
        with col_s3:
            min_hold   = st.slider("Min Hold Rate (%)",    0,    30,  10,   2,   key="w_hold")
            max_cpr    = st.slider("Max CPR ($)",          1,   100,  20,   5,   key="w_cpr")
            max_cpc    = st.slider("Max CPC ($)",          0.1,  5.0, 1.5, 0.1, key="w_cpc")

        thresholds = {
            "min_spend": min_spend, "min_roas": min_roas,
            "min_result_rate": min_res, "min_scroll_stop": min_scroll,
            "min_hook_rate": min_hook, "min_hold_rate": min_hold,
            "max_cpr": max_cpr, "min_ctr": min_ctr, "max_cpc": max_cpc,
        }

        winners = mi.get_winning_ads(thresholds=thresholds, top_n=10)

        if winners.empty:
            notice("No ads meet the current criteria. Try relaxing the thresholds.", "warning")
        else:
            st.markdown(
                f"<div style='display:inline-flex;align-items:center;gap:0.5rem;"
                f"background:#f0fdf4;border:1px solid #16a34a;"
                f"padding:0.3rem 0.8rem;margin-bottom:0.6rem;'>"
                f"<span style='font-size:0.78rem;font-weight:700;color:#16a34a;'>"
                f"{len(winners)} winning ad(s) found</span></div>",
                unsafe_allow_html=True
            )
            st.dataframe(winners, use_container_width=True, hide_index=True)

        # Top / Bottom for a selected metric
        avail = mi.available_metrics()
        num_avail = [m for m in avail if m not in ("ad_name", "adset_name", "campaign")]
        if num_avail:
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            st.markdown(
                "<div style='font-size:0.78rem;font-weight:700;color:#111827;"
                "margin-bottom:0.4rem;'>Top 5 vs Bottom 5 Ads</div>",
                unsafe_allow_html=True
            )
            sel_metric = st.selectbox(
                "Metric", num_avail,
                format_func=lambda x: x.replace("_", " ").title(),
                key="tb_metric"
            )
            col_map = mi._col_map
            if col_map.get(sel_metric):
                top5, bot5 = mi.top_bottom(col_map[sel_metric], top_n=5)
                tb_l, tb_r = st.columns(2, gap="large")
                with tb_l:
                    st.markdown(
                        "<div style='font-size:0.7rem;font-weight:700;color:#16a34a;"
                        "text-transform:uppercase;letter-spacing:0.06em;"
                        "margin-bottom:0.3rem;'>Top 5</div>",
                        unsafe_allow_html=True
                    )
                    st.dataframe(top5, use_container_width=True, hide_index=True)
                with tb_r:
                    st.markdown(
                        "<div style='font-size:0.7rem;font-weight:700;color:#dc2626;"
                        "text-transform:uppercase;letter-spacing:0.06em;"
                        "margin-bottom:0.3rem;'>Bottom 5</div>",
                        unsafe_allow_html=True
                    )
                    st.dataframe(bot5, use_container_width=True, hide_index=True)

    # ── SALES ──────────────────────────────────────────────────────────────
    elif "Sales" in domain:
        si   = SalesInsights(cleaned_df)
        kpis = si.kpi_summary()

        kpi_items = [
            ("Total Revenue",    f"${kpis.get('total_revenue', 0):,.2f}"  if kpis.get('total_revenue') else "—"),
            ("Avg Order Value",  f"${kpis.get('avg_order_value', 0):,.2f}" if kpis.get('avg_order_value') else "—"),
            ("Total Units Sold", f"{kpis.get('total_units', 0):,}"         if kpis.get('total_units') else "—"),
            ("Avg Discount",     f"{kpis.get('avg_discount_pct', 0):.1f}%" if kpis.get('avg_discount_pct') else "—"),
        ]
        kpi_items = [(l, v) for l, v in kpi_items if v != "—"]
        if kpi_items:
            k_cols = st.columns(len(kpi_items), gap="small")
            for col_w, (lbl, val) in zip(k_cols, kpi_items):
                col_w.markdown(
                    f"<div style='border:1px solid #e5e7eb;padding:0.9rem 1rem;background:#fafafa;'>"
                    f"<div style='font-size:0.65rem;font-weight:700;color:#9ca3af;"
                    f"letter-spacing:0.06em;text-transform:uppercase;'>{lbl}</div>"
                    f"<div style='font-size:1.2rem;font-weight:800;color:#111827;"
                    f"margin-top:0.2rem;'>{val}</div></div>",
                    unsafe_allow_html=True
                )

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        sl, sr = st.columns(2, gap="large")
        with sl:
            top_prods = si.top_products()
            if top_prods is not None:
                st.markdown(
                    "<div style='font-size:0.72rem;font-weight:700;color:#6b7280;"
                    "text-transform:uppercase;letter-spacing:0.06em;"
                    "margin-bottom:0.4rem;'>Top 10 Products by Revenue</div>",
                    unsafe_allow_html=True
                )
                st.plotly_chart(
                    plot_categorical_bar(
                        top_prods.rename(columns={"Product": "_p", "Revenue": "_r"}),
                        "_p"
                    ) if False else
                    __import__("plotly.graph_objects", fromlist=["Figure"]).Figure(
                        __import__("plotly.graph_objects", fromlist=["Bar"]).Bar(
                            x=top_prods["Revenue"], y=top_prods["Product"],
                            orientation="h",
                            marker=dict(color="#111827"),
                            text=top_prods["Revenue"].apply(lambda v: f"${v:,.0f}"),
                            textposition="outside",
                            textfont=dict(size=9, color="#6b7280"),
                        )
                    ).update_layout(
                        font=dict(family="Inter, sans-serif", size=11),
                        plot_bgcolor="white", paper_bgcolor="white",
                        showlegend=False, margin=dict(l=10, r=40, t=10, b=10),
                        height=max(200, len(top_prods)*32),
                        xaxis=dict(showgrid=True, gridcolor="#f3f4f6"),
                        yaxis=dict(autorange="reversed"),
                        bargap=0.3,
                    ),
                    use_container_width=True
                )
        with sr:
            rev_cat = si.revenue_by_category()
            if rev_cat is not None:
                st.markdown(
                    "<div style='font-size:0.72rem;font-weight:700;color:#6b7280;"
                    "text-transform:uppercase;letter-spacing:0.06em;"
                    "margin-bottom:0.4rem;'>Revenue by Category</div>",
                    unsafe_allow_html=True
                )
                st.dataframe(rev_cat, use_container_width=True, hide_index=True)

    # ── FINANCE ────────────────────────────────────────────────────────────
    elif "Finance" in domain:
        fi   = FinanceInsights(cleaned_df)
        kpis = fi.kpi_summary()

        kpi_items = [
            ("Total Income",     f"${kpis.get('total_income', 0):,.0f}"   if kpis.get('total_income') else "—"),
            ("Total Expense",    f"${kpis.get('total_expense', 0):,.0f}"  if kpis.get('total_expense') else "—"),
            ("Net Profit",       f"${kpis.get('net_profit', 0):,.0f}"     if kpis.get('net_profit') is not None else "—"),
            ("Profit Margin",    f"{kpis.get('profit_margin', 0):.1f}%"   if kpis.get('profit_margin') is not None else "—"),
            ("Budget Variance",  f"${kpis.get('budget_variance', 0):,.0f}" if kpis.get('budget_variance') is not None else "—"),
        ]
        kpi_items = [(l, v) for l, v in kpi_items if v != "—"]
        if kpi_items:
            k_cols = st.columns(len(kpi_items), gap="small")
            for col_w, (lbl, val) in zip(k_cols, kpi_items):
                profit_ok = "net_profit" in lbl.lower() or "margin" in lbl.lower()
                val_color = "#16a34a" if (profit_ok and not val.startswith("-")) else "#111827"
                col_w.markdown(
                    f"<div style='border:1px solid #e5e7eb;padding:0.9rem 1rem;background:#fafafa;'>"
                    f"<div style='font-size:0.65rem;font-weight:700;color:#9ca3af;"
                    f"letter-spacing:0.06em;text-transform:uppercase;'>{lbl}</div>"
                    f"<div style='font-size:1.2rem;font-weight:800;color:{val_color};"
                    f"margin-top:0.2rem;'>{val}</div></div>",
                    unsafe_allow_html=True
                )

        bva = fi.budget_vs_actual()
        if bva is not None:
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            st.markdown(
                "<div style='font-size:0.72rem;font-weight:700;color:#6b7280;"
                "text-transform:uppercase;letter-spacing:0.06em;"
                "margin-bottom:0.4rem;'>Budget vs Actual</div>",
                unsafe_allow_html=True
            )
            st.dataframe(bva, use_container_width=True, hide_index=True)

    # ── HR ─────────────────────────────────────────────────────────────────
    elif "HR" in domain:
        hr   = HRInsights(cleaned_df)
        kpis = hr.kpi_summary()

        kpi_items = [
            ("Headcount",       f"{kpis.get('headcount', 0):,}"),
            ("Attrition Rate",  f"{kpis.get('attrition_rate', 0):.1f}%"  if kpis.get('attrition_rate') is not None else "—"),
            ("Attrition Count", f"{kpis.get('attrition_count', 0)}"      if kpis.get('attrition_count') is not None else "—"),
            ("Avg Salary",      f"${kpis.get('avg_salary', 0):,.0f}"     if kpis.get('avg_salary') else "—"),
            ("Avg Tenure",      f"{kpis.get('avg_tenure', 0):.1f} yrs"   if kpis.get('avg_tenure') else "—"),
        ]
        kpi_items = [(l, v) for l, v in kpi_items if v != "—"]
        if kpi_items:
            k_cols = st.columns(len(kpi_items), gap="small")
            for col_w, (lbl, val) in zip(k_cols, kpi_items):
                col_w.markdown(
                    f"<div style='border:1px solid #e5e7eb;padding:0.9rem 1rem;background:#fafafa;'>"
                    f"<div style='font-size:0.65rem;font-weight:700;color:#9ca3af;"
                    f"letter-spacing:0.06em;text-transform:uppercase;'>{lbl}</div>"
                    f"<div style='font-size:1.2rem;font-weight:800;color:#111827;"
                    f"margin-top:0.2rem;'>{val}</div></div>",
                    unsafe_allow_html=True
                )

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        hr_l, hr_r = st.columns(2, gap="large")
        with hr_l:
            attr_dept = hr.attrition_by_department()
            if attr_dept is not None:
                st.markdown(
                    "<div style='font-size:0.72rem;font-weight:700;color:#6b7280;"
                    "text-transform:uppercase;letter-spacing:0.06em;"
                    "margin-bottom:0.4rem;'>Attrition by Department</div>",
                    unsafe_allow_html=True
                )
                st.dataframe(attr_dept, use_container_width=True, hide_index=True)
        with hr_r:
            sal_dept = hr.salary_by_department()
            if sal_dept is not None:
                st.markdown(
                    "<div style='font-size:0.72rem;font-weight:700;color:#6b7280;"
                    "text-transform:uppercase;letter-spacing:0.06em;"
                    "margin-bottom:0.4rem;'>Salary by Department</div>",
                    unsafe_allow_html=True
                )
                st.dataframe(sal_dept, use_container_width=True, hide_index=True)

    # ── GENERAL (unknown domain) ────────────────────────────────────────────
    else:
        notice(
            "No specific domain detected. Use the Analysis tab above for "
            "correlation, group comparison, regression, and hypothesis testing.",
            "info"
        )
