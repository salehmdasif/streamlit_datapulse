"""
DataPulse — Universal Data Analytics Dashboard
Phase 1: Data Ingestion + Auto Cleaning Engine
Author: Abu Salah Mohammad Asif | Ravelweb Ltd
"""

import io
import streamlit as st
import pandas as pd
from modules.cleaner import DataCleaner

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
section[data-testid="stSidebar"] {
    background-color: #0d1117 !important;
    border-right: 1px solid #21262d !important;
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] small {
    color: #8b949e !important;
}
section[data-testid="stSidebar"] strong,
section[data-testid="stSidebar"] b {
    color: #e6edf3 !important;
}
section[data-testid="stSidebar"] a {
    color: #58a6ff !important;
    text-decoration: none !important;
}
section[data-testid="stSidebar"] hr {
    border: none !important;
    border-top: 1px solid #21262d !important;
    margin: 0.6rem 0 !important;
}
/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton > button {
    background-color: #21262d !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    width: 100% !important;
    font-size: 0.78rem !important;
    padding: 0.4rem 0.8rem !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #30363d !important;
    border-color: #58a6ff !important;
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
    current_step = 1 + raw_loaded + clean_done

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
    st.markdown(
        "<div style='position:fixed;bottom:0;left:0;width:260px;"
        "padding:0.8rem 1rem;border-top:1px solid #21262d;"
        "background:#0d1117;font-size:0.68rem;color:#484f58;'>"
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
        "Accepts CSV, XLS, XLSX",
        type=["csv", "xls", "xlsx"],
        label_visibility="collapsed"
    )
    st.caption("Accepts CSV, XLS, XLSX — clean or dirty data welcome")
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
        "Meta Ads Campaign Data   —   Marketing": "data/samples/sample_meta_ads.csv",
        "E-commerce Orders   —   Sales":          "data/samples/sample_sales.csv",
        "Monthly Budget Report   —   Finance":    "data/samples/sample_finance.csv",
        "Employee Records   —   HR":              "data/samples/sample_hr.csv",
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
    c1, c2 = st.columns([2, 1])
    with c1:
        selected_sample = st.selectbox(
            "Choose dataset", list(SAMPLES.keys()),
            label_visibility="collapsed"
        )
    with c2:
        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
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
    with st.expander(f"Raw Data Preview  ·  {raw_df.shape[0]:,} rows × {raw_df.shape[1]} columns"):
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
    row_delta = final[0] - orig[0]
    col_delta = final[1] - orig[1]
    metric_row([
        ("Original Rows",    f"{orig[0]:,}",    None,                    True),
        ("Rows After Clean", f"{final[0]:,}",   f"{row_delta:+,} rows" if row_delta != 0 else None, row_delta >= 0),
        ("Original Columns", f"{orig[1]}",      None,                    True),
        ("Columns After",    f"{final[1]}",     f"{col_delta:+} cols" if col_delta != 0 else None, col_delta >= 0),
        ("Actions Taken",    f"{len(actions)}", None,                    True),
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
    st.dataframe(cleaned_df.head(15), use_container_width=True)
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

    # Phase 2 teaser
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='border:1px dashed #d1d5db;padding:1rem 1.2rem;"
        "background:#fafafa;'>"
        "<div style='font-size:0.72rem;font-weight:700;color:#9ca3af;"
        "letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.3rem;'>"
        "Next — Phase 2</div>"
        "<div style='font-size:0.85rem;color:#374151;'>"
        "Data Profiling · Column Type Classification · Domain Auto-Detection · "
        "EDA with Correlation Heatmap &amp; Distribution Plots"
        "</div></div>",
        unsafe_allow_html=True
    )
