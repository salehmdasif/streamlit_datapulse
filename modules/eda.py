"""
DataPulse — EDA (Exploratory Data Analysis) Charts
All chart functions return Plotly figures.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ── Shared style ──────────────────────────────────────────────────────────────
_FONT   = dict(family="Inter, sans-serif", size=11, color="#374151")
_GRID   = "#f3f4f6"
_LINE   = "#e5e7eb"
_BLACK  = "#111827"
_GRAY   = "#6b7280"

def _base_layout(**kwargs):
    base = dict(
        font=_FONT,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    base.update(kwargs)
    return base

def _style_axes(fig):
    fig.update_xaxes(
        showgrid=False, zeroline=False,
        linecolor=_LINE, tickfont=dict(size=9, color=_GRAY)
    )
    fig.update_yaxes(
        showgrid=True, gridcolor=_GRID, zeroline=False,
        linecolor=_LINE, tickfont=dict(size=9, color=_GRAY)
    )
    return fig


# ── Correlation Heatmap ───────────────────────────────────────────────────────

def plot_correlation_heatmap(df: pd.DataFrame) -> go.Figure | None:
    """Full numeric correlation matrix as an annotated heatmap."""
    num_df = df.select_dtypes(include="number").dropna(axis=1, how="all")
    if num_df.shape[1] < 2:
        return None

    corr = num_df.corr().round(2)
    labels = corr.columns.tolist()

    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=labels,
        y=labels,
        colorscale=[
            [0.0,  "#1e40af"],
            [0.25, "#93c5fd"],
            [0.5,  "#ffffff"],
            [0.75, "#fca5a5"],
            [1.0,  "#991b1b"],
        ],
        zmid=0,
        zmin=-1, zmax=1,
        text=corr.values,
        texttemplate="%{text:.2f}",
        textfont=dict(size=9),
        hoverongaps=False,
        showscale=True,
        colorbar=dict(
            thickness=10,
            tickfont=dict(size=9, color=_GRAY),
            outlinewidth=0,
        )
    ))

    n = len(labels)
    height = max(320, min(n * 38, 600))

    fig.update_layout(
        **_base_layout(height=height),
        xaxis=dict(tickfont=dict(size=9, color=_GRAY), tickangle=-30),
        yaxis=dict(tickfont=dict(size=9, color=_GRAY), autorange="reversed"),
    )
    return fig


# ── Distribution (Histogram + Box) ───────────────────────────────────────────

def plot_distribution(df: pd.DataFrame, column: str) -> go.Figure:
    """Side-by-side histogram and box plot for one numeric column."""
    data = df[column].dropna()

    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.72, 0.28],
        horizontal_spacing=0.04,
        subplot_titles=("Distribution", "Box Plot"),
    )

    # Histogram
    fig.add_trace(
        go.Histogram(
            x=data, nbinsx=25,
            marker=dict(color=_BLACK, line=dict(color="white", width=0.5)),
            hovertemplate="Value: %{x}<br>Count: %{y}<extra></extra>",
        ),
        row=1, col=1,
    )

    # Box
    fig.add_trace(
        go.Box(
            y=data,
            marker=dict(color=_BLACK, size=4),
            line=dict(color=_BLACK, width=1.2),
            fillcolor="#f3f4f6",
            boxmean=True,
            hovertemplate="Value: %{y}<extra></extra>",
        ),
        row=1, col=2,
    )

    fig.update_layout(
        **_base_layout(height=270),
        bargap=0.04,
        annotations=[
            dict(font=dict(size=10, color=_GRAY)),
            dict(font=dict(size=10, color=_GRAY)),
        ]
    )
    _style_axes(fig)
    return fig


# ── Categorical Bar Chart ─────────────────────────────────────────────────────

def plot_categorical_bar(df: pd.DataFrame, column: str, top_n: int = 15) -> go.Figure:
    """Horizontal bar chart of value counts for a categorical column."""
    counts = df[column].value_counts().head(top_n)

    fig = go.Figure(go.Bar(
        x=counts.values,
        y=counts.index.astype(str),
        orientation="h",
        marker=dict(color=_BLACK, line=dict(color="white", width=0.4)),
        text=counts.values,
        textposition="outside",
        textfont=dict(size=9, color=_GRAY),
        hovertemplate="%{y}: %{x}<extra></extra>",
    ))

    height = max(220, min(len(counts) * 32, 480))
    fig.update_layout(
        **_base_layout(height=height),
        xaxis=dict(showgrid=True, gridcolor=_GRID, linecolor=_LINE,
                   tickfont=dict(size=9, color=_GRAY)),
        yaxis=dict(showgrid=False, linecolor=_LINE,
                   tickfont=dict(size=9, color=_GRAY),
                   autorange="reversed"),
        bargap=0.25,
    )
    return fig


# ── Group Comparison Bar ──────────────────────────────────────────────────────

def plot_group_comparison(series: pd.Series, cat_col: str, num_col: str, agg: str) -> go.Figure:
    """Horizontal bar chart for group comparison results."""
    fig = go.Figure(go.Bar(
        x=series.values,
        y=series.index.astype(str),
        orientation="h",
        marker=dict(
            color=[_BLACK if i == 0 else "#d1d5db" for i in range(len(series))],
            line=dict(color="white", width=0.4),
        ),
        text=[f"{v:,.2f}" for v in series.values],
        textposition="outside",
        textfont=dict(size=9, color=_GRAY),
        hovertemplate="%{y}: %{x:,.2f}<extra></extra>",
    ))

    height = max(240, min(len(series) * 36, 520))
    fig.update_layout(
        **_base_layout(height=height),
        title=dict(
            text=f"{agg.capitalize()} of <b>{num_col}</b> by <b>{cat_col}</b>",
            font=dict(size=11, color=_GRAY), x=0,
        ),
        xaxis=dict(showgrid=True, gridcolor=_GRID, linecolor=_LINE,
                   tickfont=dict(size=9, color=_GRAY)),
        yaxis=dict(showgrid=False, linecolor=_LINE,
                   tickfont=dict(size=9, color=_GRAY),
                   autorange="reversed"),
        bargap=0.3,
    )
    return fig


# ── Trend Line Chart ──────────────────────────────────────────────────────────

def plot_trend(df: pd.DataFrame, date_col: str, value_col: str) -> go.Figure:
    """Line chart with optional rolling average overlay."""
    fig = go.Figure()

    # Actual values
    fig.add_trace(go.Scatter(
        x=df[date_col], y=df[value_col],
        mode="lines+markers",
        name=value_col,
        line=dict(color=_BLACK, width=1.5),
        marker=dict(size=4, color=_BLACK),
        hovertemplate="%{x|%Y-%m-%d}: %{y:,.2f}<extra></extra>",
    ))

    # Rolling average
    if "rolling_avg" in df.columns:
        fig.add_trace(go.Scatter(
            x=df[date_col], y=df["rolling_avg"],
            mode="lines",
            name="Rolling Avg",
            line=dict(color="#ef4444", width=1.5, dash="dot"),
            hovertemplate="Rolling: %{y:,.2f}<extra></extra>",
        ))

    fig.update_layout(
        **_base_layout(height=300, showlegend=True),
        legend=dict(
            font=dict(size=9, color=_GRAY),
            bgcolor="white",
            bordercolor=_LINE,
            borderwidth=1,
            x=0.01, y=0.99,
        ),
        xaxis=dict(showgrid=False, linecolor=_LINE,
                   tickfont=dict(size=9, color=_GRAY)),
        yaxis=dict(showgrid=True, gridcolor=_GRID, linecolor=_LINE,
                   tickfont=dict(size=9, color=_GRAY)),
    )
    return fig


# ── Feature Importance Bar ────────────────────────────────────────────────────

def plot_feature_importance(coef_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart for regression coefficients."""
    colors = ["#111827" if v >= 0 else "#ef4444" for v in coef_df["Coefficient"]]

    fig = go.Figure(go.Bar(
        x=coef_df["Coefficient"],
        y=coef_df["Feature"],
        orientation="h",
        marker=dict(color=colors, line=dict(color="white", width=0.4)),
        text=coef_df["Coefficient"].round(3),
        textposition="outside",
        textfont=dict(size=9, color=_GRAY),
        hovertemplate="%{y}: %{x:.4f}<extra></extra>",
    ))

    height = max(220, min(len(coef_df) * 38, 480))
    fig.update_layout(
        **_base_layout(height=height),
        xaxis=dict(showgrid=True, gridcolor=_GRID, linecolor=_LINE,
                   zeroline=True, zerolinecolor=_LINE,
                   tickfont=dict(size=9, color=_GRAY)),
        yaxis=dict(showgrid=False, linecolor=_LINE,
                   tickfont=dict(size=9, color=_GRAY),
                   autorange="reversed"),
        bargap=0.3,
    )
    return fig


# ── Scatter Plot (Correlation) ────────────────────────────────────────────────

def plot_scatter(df: pd.DataFrame, x_col: str, y_col: str) -> go.Figure:
    """Scatter plot with linear trend line."""
    clean = df[[x_col, y_col]].dropna()
    x = clean[x_col].values
    y = clean[y_col].values

    fig = go.Figure()

    # Scatter points
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode="markers",
        marker=dict(color=_BLACK, size=5, opacity=0.6,
                    line=dict(color="white", width=0.5)),
        hovertemplate=f"{x_col}: %{{x}}<br>{y_col}: %{{y}}<extra></extra>",
    ))

    # Trend line
    if len(x) >= 2:
        try:
            m, b = np.polyfit(x, y, 1)
            x_line = np.linspace(x.min(), x.max(), 100)
            fig.add_trace(go.Scatter(
                x=x_line, y=m * x_line + b,
                mode="lines",
                line=dict(color="#ef4444", width=1.5, dash="dash"),
                hoverinfo="skip",
            ))
        except Exception:
            pass

    fig.update_layout(
        **_base_layout(height=300),
        xaxis_title=dict(text=x_col, font=dict(size=10, color=_GRAY)),
        yaxis_title=dict(text=y_col, font=dict(size=10, color=_GRAY)),
    )
    _style_axes(fig)
    return fig


# ── Summary Stats Table ───────────────────────────────────────────────────────

def get_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Clean summary statistics for numeric columns."""
    num_df = df.select_dtypes(include="number")
    if num_df.empty:
        return pd.DataFrame()

    stats = num_df.describe().T
    stats = stats.rename(columns={
        "count": "Count", "mean": "Mean", "std": "Std Dev",
        "min": "Min", "25%": "Q1", "50%": "Median",
        "75%": "Q3", "max": "Max",
    })
    stats = stats.round(3)
    return stats
