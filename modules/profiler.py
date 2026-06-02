"""
DataPulse — Data Profiler & Domain Detection
Classifies columns, scores data quality, detects business domain.
"""

import pandas as pd
import numpy as np


# ── Domain Keyword Map ────────────────────────────────────────────────────────

DOMAIN_KEYWORDS = {
    "Marketing / Ads": [
        'roas', 'ctr', 'cpc', 'cpm', 'impressions', 'clicks', 'spend',
        'amount_spent', 'ad_name', 'campaign', 'hook_rate', 'scroll_stop',
        'hold_rate', 'result_rate', 'adset', 'ad_set',
    ],
    "Sales": [
        'revenue', 'sales', 'order', 'product', 'quantity', 'price',
        'discount', 'order_id', 'unit_price', 'total',
    ],
    "Finance": [
        'profit', 'loss', 'expense', 'budget', 'balance', 'income',
        'cost', 'actual', 'forecast', 'variance', 'ebitda',
    ],
    "HR / People": [
        'employee', 'salary', 'attrition', 'department', 'tenure',
        'gender', 'performance', 'hire', 'termination', 'headcount',
    ],
    "E-commerce": [
        'sku', 'cart', 'checkout', 'conversion', 'return_rate',
        'aov', 'session', 'bounce', 'funnel',
    ],
}

DOMAIN_COLORS = {
    "Marketing / Ads": ("#fff7ed", "#ea580c", "#fdba74"),
    "Sales":           ("#f0fdf4", "#16a34a", "#86efac"),
    "Finance":         ("#eff6ff", "#2563eb", "#93c5fd"),
    "HR / People":     ("#fdf4ff", "#9333ea", "#d8b4fe"),
    "E-commerce":      ("#fefce8", "#ca8a04", "#fde047"),
    "General":         ("#f8fafc", "#374151", "#d1d5db"),
}


# ── Profiler Class ────────────────────────────────────────────────────────────

class DataProfiler:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    # ── Column Classification ─────────────────────────────────────────────────
    def classify_columns(self) -> dict:
        """
        Returns {col_name: type_label} where type_label is one of:
        'numeric', 'categorical', 'datetime', 'boolean', 'id_text', 'text'
        """
        result = {}
        n_rows = max(len(self.df), 1)

        for col in self.df.columns:
            series = self.df[col]
            dtype  = series.dtype
            n_unique = series.nunique()

            if pd.api.types.is_datetime64_any_dtype(dtype):
                result[col] = 'datetime'

            elif pd.api.types.is_bool_dtype(dtype):
                result[col] = 'boolean'

            elif pd.api.types.is_numeric_dtype(dtype):
                result[col] = 'numeric'

            elif (pd.api.types.is_object_dtype(dtype)
                  or pd.api.types.is_string_dtype(dtype)):
                unique_ratio = n_unique / n_rows
                if n_unique <= 2:
                    result[col] = 'boolean'
                elif n_unique <= 20 or unique_ratio < 0.15:
                    result[col] = 'categorical'
                elif unique_ratio > 0.8 and n_unique > 20:
                    result[col] = 'id_text'
                else:
                    result[col] = 'text'

            else:
                result[col] = 'other'

        return result

    # ── Quality Score ─────────────────────────────────────────────────────────
    def quality_score(self) -> float:
        """
        Score 0–100 based on:
        - Completeness  (50%): % non-null values across all cells
        - Uniqueness    (30%): % unique rows
        - Column health (20%): penalise all-null columns
        """
        n_rows = len(self.df)
        if n_rows == 0:
            return 0.0

        completeness = float(self.df.notna().mean().mean())

        unique_rows  = len(self.df.drop_duplicates())
        uniqueness   = unique_rows / n_rows

        null_cols    = sum(1 for c in self.df.columns if self.df[c].isnull().all())
        col_health   = 1.0 - (null_cols / max(len(self.df.columns), 1))

        score = (completeness * 0.5 + uniqueness * 0.3 + col_health * 0.2) * 100
        return round(score, 1)

    # ── Domain Detection ──────────────────────────────────────────────────────
    def detect_domain(self) -> tuple[str, int]:
        """
        Returns (domain_name, match_count).
        Matches keywords against column names.
        """
        cols_text = ' '.join(self.df.columns.str.lower().tolist())

        scores: dict[str, int] = {}
        for domain, keywords in DOMAIN_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in cols_text)
            if count > 0:
                scores[domain] = count

        if not scores:
            return "General", 0

        best = max(scores, key=scores.get)
        return best, scores[best]

    # ── Column Stats Table ────────────────────────────────────────────────────
    def column_stats(self) -> list[dict]:
        """Per-column summary for display in the profile table."""
        col_types = self.classify_columns()
        rows = []
        for col in self.df.columns:
            series   = self.df[col]
            n_null   = int(series.isnull().sum())
            n_unique = int(series.nunique())
            pct_null = round(n_null / max(len(self.df), 1) * 100, 1)

            # Sample value
            non_null = series.dropna()
            sample   = str(non_null.iloc[0])[:28] if len(non_null) > 0 else '—'

            rows.append({
                'column':   col,
                'type':     col_types[col],
                'missing':  n_null,
                'miss_pct': pct_null,
                'unique':   n_unique,
                'sample':   sample,
            })
        return rows
