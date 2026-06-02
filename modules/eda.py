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
    return dict(
        font=_FONT,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
        **kwargs
    )

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
