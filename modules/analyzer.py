"""
DataPulse — Statistical Analysis Engine
Correlation, Group Comparison, Trend Analysis,
Linear Regression + Hypothesis Testing.
Pure computation — no Streamlit calls.
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
import statsmodels.api as sm
import warnings


# ── Correlation ───────────────────────────────────────────────────────────────

def correlation_analysis(df: pd.DataFrame, x_col: str, y_col: str) -> dict | None:
    """
    Pearson correlation between two numeric columns.
    Returns dict with r, r², p-value, strength label, significance.
    """
    clean = df[[x_col, y_col]].dropna()
    if len(clean) < 3:
        return None

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        r, p_val = stats.pearsonr(clean[x_col].astype(float),
                                   clean[y_col].astype(float))

    abs_r = abs(r)
    strength = (
        "Very Strong"  if abs_r >= 0.8 else
        "Strong"       if abs_r >= 0.6 else
        "Moderate"     if abs_r >= 0.4 else
        "Weak"         if abs_r >= 0.2 else
        "Negligible"
    )
    direction   = "Positive" if r > 0 else "Negative"
    significant = p_val < 0.05

    return {
        "r":           round(float(r), 4),
        "r_squared":   round(float(r) ** 2, 4),
        "p_value":     round(float(p_val), 6),
        "n":           int(len(clean)),
        "strength":    strength,
        "direction":   direction,
        "significant": significant,
    }


# ── Group Comparison ──────────────────────────────────────────────────────────

def group_comparison(
    df: pd.DataFrame,
    cat_col: str,
    num_col: str,
    agg: str = "mean",
) -> pd.Series:
    """
    Aggregate a numeric column by a categorical column.
    agg: 'mean' | 'sum' | 'median' | 'count'
    Returns a sorted Series (group → value).
    """
    clean = df[[cat_col, num_col]].dropna()
    result = (
        clean.groupby(cat_col)[num_col]
        .agg(agg)
        .sort_values(ascending=False)
    )
    return result


# ── Trend Analysis ────────────────────────────────────────────────────────────

def trend_analysis(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    rolling: int = 7,
) -> pd.DataFrame:
    """
    Aggregate value_col by date and compute optional rolling average.
    Returns DataFrame with columns: [date_col, value_col, 'rolling_avg'].
    """
    clean = df[[date_col, value_col]].dropna().copy()
    clean[date_col] = pd.to_datetime(clean[date_col], errors="coerce")
    clean = clean.dropna(subset=[date_col])
    clean = (
        clean.groupby(date_col)[value_col]
        .sum()
        .reset_index()
        .sort_values(date_col)
    )
    if len(clean) >= rolling:
        clean["rolling_avg"] = (
            clean[value_col].rolling(rolling, min_periods=1).mean().round(2)
        )
    else:
        clean["rolling_avg"] = clean[value_col]
    return clean


# ── Linear Regression + Hypothesis Testing ───────────────────────────────────

def run_regression(
    df: pd.DataFrame,
    target_col: str,
    feature_cols: list[str],
) -> dict | None:
    """
    Standardised linear regression via scikit-learn.
    Hypothesis testing via statsmodels OLS.

    Returns dict with:
      r2, adj_r2, n, f_pvalue, intercept,
      coef_df (feature importance),
      hyp_df  (p-values, t-stats, CIs)
    """
    if not feature_cols:
        return None

    cols   = [target_col] + feature_cols
    clean  = df[cols].dropna()

    if len(clean) < max(len(feature_cols) + 2, 5):
        return None

    X_raw = clean[feature_cols].values.astype(float)
    y     = clean[target_col].values.astype(float)

    # Standardise features
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    # sklearn regression
    model  = LinearRegression()
    model.fit(X_scaled, y)
    y_pred = model.predict(X_scaled)
    r2     = r2_score(y, y_pred)

    # Statsmodels OLS (for p-values, CIs)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        X_sm     = sm.add_constant(X_scaled)
        model_sm = sm.OLS(y, X_sm).fit()

    # Coefficient table (sorted by |coef|)
    coef_df = (
        pd.DataFrame({
            "Feature":     feature_cols,
            "Coefficient": model.coef_.round(4),
            "Abs":         np.abs(model.coef_),
        })
        .sort_values("Abs", ascending=False)
        .drop(columns="Abs")
        .reset_index(drop=True)
    )

    # Convert statsmodels results to plain arrays (works across versions)
    params  = np.array(model_sm.params).flatten()
    bse     = np.array(model_sm.bse).flatten()
    tvalues = np.array(model_sm.tvalues).flatten()
    pvalues = np.array(model_sm.pvalues).flatten()
    conf    = np.array(model_sm.conf_int())   # shape (k+1, 2)

    # Hypothesis testing table
    hyp_data = []
    for i, feat in enumerate(feature_cols):
        pv = float(pvalues[i + 1])
        hyp_data.append({
            "Feature":     feat,
            "Coefficient": round(float(params[i + 1]),  4),
            "Std Error":   round(float(bse[i + 1]),     4),
            "t-Statistic": round(float(tvalues[i + 1]), 4),
            "p-Value":     round(pv, 6),
            "CI Lower":    round(float(conf[i + 1, 0]), 4),
            "CI Upper":    round(float(conf[i + 1, 1]), 4),
            "Significant": pv < 0.05,
        })

    hyp_df = pd.DataFrame(hyp_data)

    return {
        "r2":        round(float(r2), 4),
        "adj_r2":    round(float(model_sm.rsquared_adj), 4),
        "n":         int(len(clean)),
        "intercept": round(float(model.intercept_), 4),
        "f_pvalue":  round(float(model_sm.f_pvalue), 6),
        "aic":       round(float(model_sm.aic), 2),
        "coef_df":   coef_df,
        "hyp_df":    hyp_df,
    }
