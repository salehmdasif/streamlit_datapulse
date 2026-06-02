"""
DataPulse — Domain Intelligence Engine
Domain-specific insights for Marketing/Ads, Sales, Finance, HR.
Pure computation — no Streamlit calls.
"""

import pandas as pd
import numpy as np


# ═════════════════════════════════════════════════════════════════════════════
# MARKETING / ADS
# ═════════════════════════════════════════════════════════════════════════════

class MarketingInsights:
    """
    Winning Ad Selector + key metrics for Marketing/Ads datasets.
    Column names are matched flexibly (contains-based).
    """

    # Default thresholds — user can override via sliders
    DEFAULT_THRESHOLDS = {
        "min_spend":       100.0,
        "min_roas":        2.0,
        "min_result_rate": 20.0,
        "min_scroll_stop": 25.0,
        "min_hook_rate":   30.0,
        "min_hold_rate":   10.0,
        "max_cpr":         20.0,
        "min_ctr":         2.0,
        "max_cpc":         1.5,
    }

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._col_map = self._map_columns()

    def _find_col(self, *keywords) -> str | None:
        """Return first column whose name contains any keyword (case-insensitive)."""
        for kw in keywords:
            for col in self.df.columns:
                if kw.lower() in col.lower():
                    return col
        return None

    def _map_columns(self) -> dict:
        return {
            "spend":       self._find_col("amount_spent", "spend", "cost"),
            "roas":        self._find_col("roas", "return_on"),
            "result_rate": self._find_col("result_rate", "conversion_rate"),
            "scroll_stop": self._find_col("scroll_stop"),
            "hook_rate":   self._find_col("hook_rate", "hook"),
            "hold_rate":   self._find_col("hold_rate", "hold"),
            "cpr":         self._find_col("cpr", "cost_per_result"),
            "ctr":         self._find_col("ctr", "click_through"),
            "cpc":         self._find_col("cpc", "cost_per_click"),
            "ad_name":     self._find_col("ad_name", "ad name", "creative"),
            "adset_name":  self._find_col("ad_set", "adset", "audience"),
            "campaign":    self._find_col("campaign"),
            "impressions": self._find_col("impressions"),
            "clicks":      self._find_col("clicks"),
            "results":     self._find_col("results"),
        }

    def available_metrics(self) -> list[str]:
        """Return list of metric keys that have a matching column."""
        return [k for k, v in self._col_map.items() if v is not None]

    def key_metrics_summary(self) -> dict:
        """Aggregate key ad metrics as a summary dict."""
        cm = self._col_map
        summary = {}
        num_df = self.df.select_dtypes(include="number")

        def safe_mean(col):
            if col and col in num_df.columns:
                return round(float(num_df[col].mean()), 2)
            return None

        def safe_sum(col):
            if col and col in num_df.columns:
                return round(float(num_df[col].sum()), 2)
            return None

        summary["total_spend"]     = safe_sum(cm["spend"])
        summary["avg_roas"]        = safe_mean(cm["roas"])
        summary["avg_ctr"]         = safe_mean(cm["ctr"])
        summary["avg_cpc"]         = safe_mean(cm["cpc"])
        summary["avg_cpr"]         = safe_mean(cm["cpr"])
        summary["avg_result_rate"] = safe_mean(cm["result_rate"])
        summary["total_impressions"]= safe_sum(cm["impressions"])
        summary["total_clicks"]    = safe_sum(cm["clicks"])
        summary["total_results"]   = safe_sum(cm["results"])
        return {k: v for k, v in summary.items() if v is not None}

    def get_winning_ads(self, thresholds: dict | None = None, top_n: int = 10) -> pd.DataFrame:
        """
        Filter ads that meet all threshold criteria.
        Returns top_n sorted by result_rate desc.
        """
        t  = {**self.DEFAULT_THRESHOLDS, **(thresholds or {})}
        cm = self._col_map
        df = self.df.copy()

        conditions = []
        if cm["spend"]       and cm["spend"] in df.columns:
            conditions.append(df[cm["spend"]]       >= t["min_spend"])
        if cm["roas"]        and cm["roas"] in df.columns:
            conditions.append(df[cm["roas"]]        >= t["min_roas"])
        if cm["result_rate"] and cm["result_rate"] in df.columns:
            conditions.append(df[cm["result_rate"]] >= t["min_result_rate"])
        if cm["scroll_stop"] and cm["scroll_stop"] in df.columns:
            conditions.append(df[cm["scroll_stop"]] >= t["min_scroll_stop"])
        if cm["hook_rate"]   and cm["hook_rate"] in df.columns:
            conditions.append(df[cm["hook_rate"]]   >= t["min_hook_rate"])
        if cm["hold_rate"]   and cm["hold_rate"] in df.columns:
            conditions.append(df[cm["hold_rate"]]   >= t["min_hold_rate"])
        if cm["cpr"]         and cm["cpr"] in df.columns:
            conditions.append(df[cm["cpr"]]         <= t["max_cpr"])
        if cm["ctr"]         and cm["ctr"] in df.columns:
            conditions.append(df[cm["ctr"]]         >= t["min_ctr"])
        if cm["cpc"]         and cm["cpc"] in df.columns:
            conditions.append(df[cm["cpc"]]         <= t["max_cpc"])

        if not conditions:
            return pd.DataFrame()

        mask    = conditions[0]
        for cond in conditions[1:]:
            mask = mask & cond

        winners = df[mask].copy()

        # Sort by result_rate if available, else roas, else spend
        sort_col = cm["result_rate"] or cm["roas"] or cm["spend"]
        if sort_col and sort_col in winners.columns:
            winners = winners.sort_values(sort_col, ascending=False)

        # Select display columns (only those that exist)
        display_cols = [
            cm["ad_name"], cm["adset_name"], cm["campaign"],
            cm["spend"], cm["roas"], cm["result_rate"],
            cm["scroll_stop"], cm["hook_rate"], cm["hold_rate"],
            cm["ctr"], cm["cpr"], cm["cpc"],
        ]
        display_cols = [c for c in display_cols if c is not None and c in winners.columns]

        return winners[display_cols].head(top_n).round(2)

    def top_bottom(self, metric_col: str, top_n: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Return top-N and bottom-N ads for a given metric column."""
        if metric_col not in self.df.columns:
            return pd.DataFrame(), pd.DataFrame()
        name_col = self._col_map.get("ad_name")
        cols = [c for c in [name_col, metric_col] if c]
        df   = self.df[cols].dropna()
        top  = df.nlargest(top_n, metric_col).round(2)
        bot  = df.nsmallest(top_n, metric_col).round(2)
        return top, bot


# ═════════════════════════════════════════════════════════════════════════════
# SALES
# ═════════════════════════════════════════════════════════════════════════════

class SalesInsights:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def _find_col(self, *kws):
        for kw in kws:
            for col in self.df.columns:
                if kw.lower() in col.lower():
                    return col
        return None

    def kpi_summary(self) -> dict:
        rev_col = self._find_col("revenue", "total", "sales")
        qty_col = self._find_col("quantity", "qty", "units")
        disc_col= self._find_col("discount")
        num_df  = self.df.select_dtypes(include="number")

        out = {}
        if rev_col and rev_col in num_df.columns:
            out["total_revenue"] = round(float(num_df[rev_col].sum()), 2)
            out["avg_order_value"] = round(float(num_df[rev_col].mean()), 2)
        if qty_col and qty_col in num_df.columns:
            out["total_units"] = int(num_df[qty_col].sum())
        if disc_col and disc_col in num_df.columns:
            out["avg_discount_pct"] = round(float(num_df[disc_col].mean()), 2)
        return out

    def top_products(self, top_n: int = 10) -> pd.DataFrame | None:
        prod_col = self._find_col("product", "item", "sku", "name")
        rev_col  = self._find_col("revenue", "total", "sales")
        if not prod_col or not rev_col:
            return None
        return (
            self.df.groupby(prod_col)[rev_col]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
            .round(2)
            .reset_index()
            .rename(columns={prod_col: "Product", rev_col: "Revenue"})
        )

    def revenue_by_category(self) -> pd.DataFrame | None:
        cat_col = self._find_col("category", "type", "segment", "region")
        rev_col = self._find_col("revenue", "total", "sales")
        if not cat_col or not rev_col:
            return None
        return (
            self.df.groupby(cat_col)[rev_col]
            .sum()
            .sort_values(ascending=False)
            .round(2)
            .reset_index()
            .rename(columns={cat_col: "Category", rev_col: "Revenue"})
        )


# ═════════════════════════════════════════════════════════════════════════════
# FINANCE
# ═════════════════════════════════════════════════════════════════════════════

class FinanceInsights:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def _find_col(self, *kws):
        for kw in kws:
            for col in self.df.columns:
                if kw.lower() in col.lower():
                    return col
        return None

    def kpi_summary(self) -> dict:
        inc_col    = self._find_col("income", "revenue", "sales")
        exp_col    = self._find_col("expense", "cost", "spending")
        prof_col   = self._find_col("profit", "net")
        budget_col = self._find_col("budget")
        actual_col = self._find_col("actual")
        num_df     = self.df.select_dtypes(include="number")

        out = {}
        if inc_col and inc_col in num_df.columns:
            out["total_income"]  = round(float(num_df[inc_col].sum()), 2)
        if exp_col and exp_col in num_df.columns:
            out["total_expense"] = round(float(num_df[exp_col].sum()), 2)
        if inc_col and exp_col and inc_col in num_df.columns and exp_col in num_df.columns:
            out["net_profit"]    = round(out["total_income"] - out["total_expense"], 2)
            out["profit_margin"] = round(out["net_profit"] / out["total_income"] * 100, 1) if out["total_income"] else 0
        if budget_col and actual_col and budget_col in num_df.columns and actual_col in num_df.columns:
            variance = num_df[actual_col].sum() - num_df[budget_col].sum()
            out["budget_variance"] = round(float(variance), 2)
        return out

    def budget_vs_actual(self) -> pd.DataFrame | None:
        cat_col    = self._find_col("cost_center", "department", "category", "month")
        budget_col = self._find_col("budget")
        actual_col = self._find_col("actual")
        if not budget_col or not actual_col:
            return None
        cols = [c for c in [cat_col, budget_col, actual_col] if c]
        df   = self.df[cols].dropna(subset=[budget_col, actual_col])
        if cat_col:
            df = df.groupby(cat_col)[[budget_col, actual_col]].sum().reset_index()
        df["variance"] = (df[actual_col] - df[budget_col]).round(2)
        df["var_pct"]  = ((df["variance"] / df[budget_col]) * 100).round(1)
        return df.round(2)


# ═════════════════════════════════════════════════════════════════════════════
# HR / PEOPLE
# ═════════════════════════════════════════════════════════════════════════════

class HRInsights:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._normalise_attrition()

    def _find_col(self, *kws):
        for kw in kws:
            for col in self.df.columns:
                if kw.lower() in col.lower():
                    return col
        return None

    def _normalise_attrition(self):
        """Normalise attrition column to 0/1 integers."""
        col = self._find_col("attrition")
        if col is None:
            return
        s = self.df[col].astype(str).str.strip().str.lower()
        self.df[col] = s.map(
            lambda v: 1 if v in ("yes", "1", "true", "y") else (0 if v in ("no", "0", "false", "n") else np.nan)
        )

    def kpi_summary(self) -> dict:
        attr_col   = self._find_col("attrition")
        sal_col    = self._find_col("salary", "compensation")
        tenure_col = self._find_col("tenure", "years")
        num_df     = self.df.select_dtypes(include="number")

        out = {"headcount": len(self.df)}
        if attr_col and attr_col in self.df.columns:
            valid = self.df[attr_col].dropna()
            out["attrition_rate"] = round(float(valid.mean()) * 100, 1)
            out["attrition_count"] = int(valid.sum())
        if sal_col and sal_col in num_df.columns:
            out["avg_salary"] = round(float(num_df[sal_col].mean()), 0)
            out["median_salary"] = round(float(num_df[sal_col].median()), 0)
        if tenure_col and tenure_col in num_df.columns:
            out["avg_tenure"] = round(float(num_df[tenure_col].mean()), 1)
        return out

    def attrition_by_department(self) -> pd.DataFrame | None:
        dept_col = self._find_col("department", "dept", "team", "division")
        attr_col = self._find_col("attrition")
        if not dept_col or not attr_col:
            return None
        df = self.df[[dept_col, attr_col]].dropna()
        result = (
            df.groupby(dept_col)[attr_col]
            .agg(["sum", "count", "mean"])
            .rename(columns={"sum": "Left", "count": "Total", "mean": "Rate"})
            .reset_index()
        )
        result["Rate"] = (result["Rate"] * 100).round(1)
        result = result.rename(columns={dept_col: "Department"})
        return result.sort_values("Rate", ascending=False)

    def salary_by_department(self) -> pd.DataFrame | None:
        dept_col = self._find_col("department", "dept", "team")
        sal_col  = self._find_col("salary", "compensation")
        if not dept_col or not sal_col:
            return None
        return (
            self.df.groupby(dept_col)[sal_col]
            .agg(["mean", "median", "min", "max"])
            .round(0)
            .reset_index()
            .rename(columns={
                dept_col: "Department",
                "mean": "Avg Salary", "median": "Median",
                "min": "Min", "max": "Max",
            })
        )
