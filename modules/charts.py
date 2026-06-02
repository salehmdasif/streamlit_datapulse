"""
DataPulse — Analytics Charts
Colorful Pie, Bar, Line, Bubble charts with PNG export.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go

PALETTE = [
    "#6366f1", "#f59e0b", "#10b981", "#f43f5e",
    "#3b82f6", "#8b5cf6", "#14b8a6", "#fb923c",
    "#ec4899", "#84cc16", "#06b6d4", "#a855f7",
]

_FONT = dict(family="Inter, sans-serif", size=11, color="#374151")
_GRAY = "#6b7280"
_GRID = "#f3f4f6"
_LINE = "#e5e7eb"


def _hex_rgba(hex_color: str, alpha: float = 0.10) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _base(height: int = 360, legend: bool = False, **kw) -> dict:
    return dict(
        font=_FONT,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=legend,
        margin=dict(l=10, r=10, t=40, b=10),
        height=height,
        **kw,
    )


# ── Pie ───────────────────────────────────────────────────────────────────────

def plot_pie(df: pd.DataFrame, column: str, top_n: int = 10) -> go.Figure:
    counts = df[column].value_counts()
    main   = counts.head(top_n)
    rest   = counts.iloc[top_n:].sum()
    if rest > 0:
        import pandas as _pd
        main = _pd.concat([main, _pd.Series({"Other": rest})])

    colors = (PALETTE * 4)[: len(main)]

    fig = go.Figure(go.Pie(
        labels=main.index.astype(str),
        values=main.values,
        hole=0.4,
        marker=dict(colors=colors, line=dict(color="white", width=2)),
        textinfo="label+percent",
        textfont=dict(size=10, family="Inter, sans-serif"),
        hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>",
        sort=True,
    ))
    fig.update_layout(
        **_base(height=400, legend=True),
        legend=dict(
            font=dict(size=9, color=_GRAY),
            x=1.0, y=0.5,
            bgcolor="white",
        ),
    )
    return fig


# ── Bar ───────────────────────────────────────────────────────────────────────

def plot_bar(
    df: pd.DataFrame,
    cat_col: str,
    num_col: str,
    agg: str = "sum",
    top_n: int = 15,
) -> go.Figure:
    clean   = df[[cat_col, num_col]].dropna().copy()
    clean[num_col] = pd.to_numeric(clean[num_col], errors="coerce")
    clean   = clean.dropna(subset=[num_col])
    grouped = clean.groupby(cat_col)[num_col].agg(agg).sort_values(ascending=False).head(top_n)
    colors  = (PALETTE * 4)[: len(grouped)]
    vals    = grouped.values.astype(float)

    fig = go.Figure(go.Bar(
        x=grouped.index.astype(str),
        y=vals,
        marker=dict(color=colors, line=dict(color="white", width=1)),
        text=[f"{v:,.1f}" for v in vals],
        textposition="outside",
        textfont=dict(size=9, color=_GRAY),
        hovertemplate="%{x}: %{y:,.2f}<extra></extra>",
        customdata=vals,
    ))

    height = max(320, min(len(grouped) * 28 + 120, 500))
    fig.update_layout(
        **_base(height=height),
        title=dict(
            text=f"{agg.capitalize()} of <b>{num_col}</b> by <b>{cat_col}</b>",
            font=dict(size=11, color=_GRAY), x=0,
        ),
        xaxis=dict(
            showgrid=False, linecolor=_LINE,
            tickfont=dict(size=9, color=_GRAY),
            tickangle=-30 if len(grouped) > 6 else 0,
        ),
        yaxis=dict(
            showgrid=True, gridcolor=_GRID, linecolor=_LINE,
            tickfont=dict(size=9, color=_GRAY),
        ),
        bargap=0.3,
    )
    return fig


# ── Line ──────────────────────────────────────────────────────────────────────

def plot_line(
    df: pd.DataFrame,
    x_col: str,
    y_cols: list,
) -> go.Figure:
    fig    = go.Figure()
    single = len(y_cols) == 1

    for i, y_col in enumerate(y_cols):
        color = PALETTE[i % len(PALETTE)]
        clean = df[[x_col, y_col]].dropna().sort_values(x_col)

        fig.add_trace(go.Scatter(
            x=clean[x_col],
            y=clean[y_col],
            mode="lines+markers",
            name=y_col,
            line=dict(color=color, width=2.2),
            marker=dict(size=5, color=color, line=dict(color="white", width=1)),
            fill="tozeroy" if single else "none",
            fillcolor=_hex_rgba(color, 0.08) if single else None,
            hovertemplate=f"{y_col}: %{{y:,.2f}}<extra></extra>",
        ))

    fig.update_layout(
        **_base(height=340, legend=not single),
        legend=dict(
            font=dict(size=9, color=_GRAY), bgcolor="white",
            bordercolor=_LINE, borderwidth=1, x=0.01, y=0.99,
        ),
        xaxis=dict(showgrid=False, linecolor=_LINE, tickfont=dict(size=9, color=_GRAY)),
        yaxis=dict(showgrid=True, gridcolor=_GRID, linecolor=_LINE, tickfont=dict(size=9, color=_GRAY)),
    )
    return fig


# ── Bubble ────────────────────────────────────────────────────────────────────

def plot_bubble(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    size_col: str,
    color_col: str | None = None,
) -> go.Figure:
    # Use internal names to avoid duplicate-column crashes when user picks
    # the same column for X / Y / Size
    def _to_num(series):
        # strip common currency / percent symbols before parsing
        s = series.astype(str).str.replace(r"[$€£¥%,\s]", "", regex=True)
        return pd.to_numeric(s, errors="coerce")

    x_s = _to_num(df[x_col])
    y_s = _to_num(df[y_col])
    z_s = _to_num(df[size_col])

    clean = pd.DataFrame({"_x": x_s, "_y": y_s, "_z": z_s}).dropna()

    if color_col and color_col in df.columns:
        clean["_c"] = df[color_col].reindex(clean.index).values
        clean = clean.dropna(subset=["_c"])
        has_color = True
    else:
        has_color = False

    # return a blank figure if no valid rows remain
    if len(clean) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No valid numeric data for the selected columns.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=12, color=_GRAY),
        )
        fig.update_layout(**_base(height=300))
        return fig

    raw   = clean["_z"].abs()
    s_min, s_max = float(raw.min()), float(raw.max())
    bubble = (
        (8 + (raw - s_min) / (s_max - s_min) * 34).astype(float)
        if s_max > s_min
        else pd.Series([20.0] * len(clean), index=clean.index, dtype=float)
    )

    fig = go.Figure()

    if has_color:
        for i, cat in enumerate(clean["_c"].unique()):
            m = clean["_c"] == cat
            fig.add_trace(go.Scatter(
                x=clean.loc[m, "_x"],
                y=clean.loc[m, "_y"],
                mode="markers",
                name=str(cat)[:22],
                marker=dict(
                    size=bubble[m],
                    color=PALETTE[i % len(PALETTE)],
                    opacity=0.78,
                    line=dict(color="white", width=1),
                ),
                customdata=clean.loc[m, "_z"],
                hovertemplate=(
                    f"<b>{cat}</b><br>{x_col}: %{{x:,.2f}}<br>"
                    f"{y_col}: %{{y:,.2f}}<br>{size_col}: %{{customdata:,.2f}}<extra></extra>"
                ),
            ))
        show_legend = True
    else:
        fig.add_trace(go.Scatter(
            x=clean["_x"],
            y=clean["_y"],
            mode="markers",
            marker=dict(
                size=bubble,
                color=clean["_z"],
                colorscale=[[0, "#6366f1"], [0.5, "#10b981"], [1, "#f43f5e"]],
                opacity=0.78,
                line=dict(color="white", width=1),
                showscale=True,
                colorbar=dict(
                    title=dict(text=size_col, font=dict(size=9, color=_GRAY)),
                    thickness=10,
                    tickfont=dict(size=8, color=_GRAY),
                    outlinewidth=0,
                ),
            ),
            customdata=clean["_z"],
            hovertemplate=(
                f"{x_col}: %{{x:,.2f}}<br>{y_col}: %{{y:,.2f}}<br>"
                f"{size_col}: %{{customdata:,.2f}}<extra></extra>"
            ),
        ))
        show_legend = False

    fig.update_layout(
        **_base(height=400, legend=show_legend),
        xaxis=dict(
            title=dict(text=x_col, font=dict(size=10, color=_GRAY)),
            showgrid=True, gridcolor=_GRID, linecolor=_LINE,
            tickfont=dict(size=9, color=_GRAY),
        ),
        yaxis=dict(
            title=dict(text=y_col, font=dict(size=10, color=_GRAY)),
            showgrid=True, gridcolor=_GRID, linecolor=_LINE,
            tickfont=dict(size=9, color=_GRAY),
        ),
        legend=dict(
            font=dict(size=9, color=_GRAY), bgcolor="white",
            bordercolor=_LINE, borderwidth=1,
        ),
    )
    return fig


# ── Funnel Chart ─────────────────────────────────────────────────────────────

def plot_funnel(
    df: pd.DataFrame,
    cat_col: str,
    num_col: str,
    agg: str = "sum",
    sort: bool = True,
) -> go.Figure:
    clean = df[[cat_col, num_col]].dropna().copy()
    clean[num_col] = pd.to_numeric(clean[num_col], errors="coerce")
    clean = clean.dropna(subset=[num_col])
    grouped = clean.groupby(cat_col)[num_col].agg(agg)
    if sort:
        grouped = grouped.sort_values(ascending=False)

    colors = (PALETTE * 4)[: len(grouped)]

    fig = go.Figure(go.Funnel(
        y=grouped.index.astype(str),
        x=grouped.values.astype(float),
        textinfo="value+percent initial",
        textfont=dict(size=10, family="Inter, sans-serif"),
        marker=dict(color=colors, line=dict(color="white", width=2)),
        connector=dict(line=dict(color=_LINE, width=1, dash="dot")),
        hovertemplate="%{y}: %{x:,.2f} (%{percentInitial})<extra></extra>",
    ))

    height = max(300, min(len(grouped) * 52 + 60, 560))
    fig.update_layout(**_base(height=height))
    return fig


# ── Waterfall Chart ───────────────────────────────────────────────────────────

def plot_waterfall(
    df: pd.DataFrame,
    cat_col: str,
    num_col: str,
    agg: str = "sum",
    sort_vals: bool = True,
) -> go.Figure:
    clean = df[[cat_col, num_col]].dropna().copy()
    clean[num_col] = pd.to_numeric(clean[num_col], errors="coerce")
    clean = clean.dropna(subset=[num_col])
    grouped = clean.groupby(cat_col)[num_col].agg(agg)
    if sort_vals:
        grouped = grouped.sort_values(ascending=False)

    vals   = grouped.values.astype(float).tolist()
    labels = grouped.index.astype(str).tolist() + ["Total"]
    vals  += [sum(vals)]

    fig = go.Figure(go.Waterfall(
        x=labels,
        y=vals[:-1] + [None],           # relatives
        measure=["relative"] * (len(vals) - 1) + ["total"],
        base=0,
        text=[f"{v:,.1f}" for v in vals],
        textposition="outside",
        textfont=dict(size=9, color=_GRAY),
        connector=dict(line=dict(color=_LINE, width=1)),
        increasing=dict(marker=dict(color="#10b981", line=dict(color="white", width=0.5))),
        decreasing=dict(marker=dict(color="#f43f5e", line=dict(color="white", width=0.5))),
        totals=dict(marker=dict(color="#6366f1", line=dict(color="white", width=0.5))),
        hovertemplate="%{x}: %{y:,.2f}<extra></extra>",
    ))

    height = max(340, min(len(labels) * 38 + 80, 540))
    fig.update_layout(
        **_base(height=height),
        xaxis=dict(
            showgrid=False, linecolor=_LINE, tickfont=dict(size=9, color=_GRAY),
            tickangle=-25 if len(labels) > 7 else 0,
        ),
        yaxis=dict(showgrid=True, gridcolor=_GRID, linecolor=_LINE, tickfont=dict(size=9, color=_GRAY)),
        bargap=0.3,
    )
    return fig


# ── Treemap ───────────────────────────────────────────────────────────────────

def plot_treemap(
    df: pd.DataFrame,
    cat_col: str,
    num_col: str,
    sub_col: str | None = None,
) -> go.Figure:
    clean = df[[cat_col, num_col]].dropna().copy()
    if sub_col and sub_col in df.columns:
        clean[sub_col] = df[sub_col].reindex(clean.index)
        clean = clean.dropna(subset=[sub_col])
    clean[num_col] = pd.to_numeric(clean[num_col], errors="coerce")
    clean = clean.dropna(subset=[num_col])

    if sub_col and sub_col in clean.columns:
        grp     = clean.groupby([cat_col, sub_col])[num_col].sum().reset_index()
        labels  = grp[sub_col].astype(str).tolist()
        parents = grp[cat_col].astype(str).tolist()
        values  = grp[num_col].values.astype(float).tolist()
        # parent nodes
        for p, v in clean.groupby(cat_col)[num_col].sum().items():
            labels.append(str(p)); parents.append(""); values.append(float(v))
    else:
        grp    = clean.groupby(cat_col)[num_col].sum().sort_values(ascending=False)
        labels  = grp.index.astype(str).tolist()
        parents = [""] * len(labels)
        values  = grp.values.astype(float).tolist()

    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        textfont=dict(size=11, family="Inter, sans-serif"),
        marker=dict(
            colorscale=[[0, "#6366f1"], [0.33, "#10b981"], [0.66, "#f59e0b"], [1, "#f43f5e"]],
            showscale=False,
            line=dict(color="white", width=2),
        ),
        hovertemplate="%{label}: %{value:,.2f}<extra></extra>",
        tiling=dict(pad=3),
    ))
    fig.update_layout(**_base(height=420))
    return fig


# ── Stacked Bar ───────────────────────────────────────────────────────────────

def plot_stacked_bar(
    df: pd.DataFrame,
    x_col: str,
    stack_col: str,
    num_col: str,
    agg: str = "sum",
    normalized: bool = False,
) -> go.Figure:
    clean = df[[x_col, stack_col, num_col]].dropna().copy()
    clean[num_col] = pd.to_numeric(clean[num_col], errors="coerce")
    clean = clean.dropna(subset=[num_col])

    pivot = clean.groupby([x_col, stack_col])[num_col].agg(agg).unstack(fill_value=0)

    if normalized:
        totals = pivot.sum(axis=1)
        totals = totals.replace(0, 1)
        pivot  = (pivot.div(totals, axis=0) * 100).round(2)

    fig = go.Figure()
    for i, col in enumerate(pivot.columns):
        color = PALETTE[i % len(PALETTE)]
        fig.add_trace(go.Bar(
            name=str(col)[:22],
            x=pivot.index.astype(str),
            y=pivot[col].values,
            marker=dict(color=color, line=dict(color="white", width=0.6)),
            hovertemplate=f"{col}: %{{y:,.2f}}{'%' if normalized else ''}<extra></extra>",
        ))

    height = max(340, min(len(pivot) * 28 + 140, 520))
    fig.update_layout(
        **_base(height=height, legend=True),
        barmode="stack",
        legend=dict(
            font=dict(size=9, color=_GRAY), bgcolor="white",
            bordercolor=_LINE, borderwidth=1,
            orientation="h", y=-0.2, x=0,
        ),
        xaxis=dict(
            showgrid=False, linecolor=_LINE, tickfont=dict(size=9, color=_GRAY),
            tickangle=-30 if len(pivot) > 6 else 0,
        ),
        yaxis=dict(
            showgrid=True, gridcolor=_GRID, linecolor=_LINE,
            tickfont=dict(size=9, color=_GRAY),
            ticksuffix="%" if normalized else "",
        ),
        bargap=0.25,
    )
    return fig


# ── Gauge / KPI Meter ─────────────────────────────────────────────────────────

def plot_gauges(items: list) -> go.Figure:
    """
    items: list of (label, value, min_val, max_val)  — max 4 items.
    Renders all gauges in one figure using domain positioning.
    """
    n = min(len(items), 4)

    # (x0, x1, y0, y1) per gauge
    _pos = {
        1: [(0.05, 0.95, 0.0, 1.0)],
        2: [(0.02, 0.48, 0.0, 1.0), (0.52, 0.98, 0.0, 1.0)],
        3: [(0.02, 0.32, 0.0, 1.0), (0.35, 0.65, 0.0, 1.0), (0.68, 0.98, 0.0, 1.0)],
        4: [(0.02, 0.48, 0.52, 1.0), (0.52, 0.98, 0.52, 1.0),
            (0.02, 0.48, 0.0,  0.48), (0.52, 0.98, 0.0,  0.48)],
    }

    fig = go.Figure()
    for i, (label, value, min_v, max_v) in enumerate(items[:4]):
        x0, x1, y0, y1 = _pos[n][i]
        color  = PALETTE[i % len(PALETTE)]
        span   = max(max_v - min_v, 1e-9)
        t1     = min_v + span * 0.50
        t2     = min_v + span * 0.75

        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=float(value),
            number=dict(font=dict(size=22, color="#111827", family="Inter, sans-serif")),
            title=dict(text=label, font=dict(size=12, color=_GRAY, family="Inter, sans-serif")),
            domain=dict(x=[x0, x1], y=[y0, y1]),
            gauge=dict(
                axis=dict(
                    range=[min_v, max_v],
                    tickfont=dict(size=8, color=_GRAY),
                    tickcolor=_LINE,
                ),
                bar=dict(color=color, thickness=0.55),
                bgcolor="white",
                borderwidth=0,
                steps=[
                    dict(range=[min_v, t1], color="#f3f4f6"),
                    dict(range=[t1, t2],    color=_hex_rgba(color, 0.15)),
                    dict(range=[t2, max_v], color=_hex_rgba(color, 0.30)),
                ],
                threshold=dict(
                    line=dict(color="#f43f5e", width=2),
                    thickness=0.78,
                    value=t2,
                ),
            ),
        ))

    height = 260 if n <= 2 else 520
    fig.update_layout(**_base(height=height))
    return fig


# ── PNG Export ────────────────────────────────────────────────────────────────

def fig_to_png(fig: go.Figure, width: int = 1100) -> bytes | None:
    """Return PNG bytes via kaleido. Returns None if kaleido is not installed."""
    try:
        h = fig.layout.height or 400
        return fig.to_image(format="png", width=width, height=h, scale=2)
    except Exception:
        return None
