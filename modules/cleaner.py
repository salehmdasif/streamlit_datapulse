"""
DataPulse — Auto Data Cleaning Engine
Handles: column normalization, duplicates, type fixing,
         missing values, and outlier detection/handling.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field


# ── Report Dataclass ──────────────────────────────────────────────────────────

@dataclass
class CleaningReport:
    original_shape: tuple
    final_shape: tuple = (0, 0)
    actions_taken: list = field(default_factory=list)
    issues_found: list = field(default_factory=list)

    def add_action(self, msg: str):
        self.actions_taken.append(msg)

    def add_issue(self, msg: str):
        self.issues_found.append(msg)


# ── Cleaner Class ─────────────────────────────────────────────────────────────

class DataCleaner:
    def __init__(self, df: pd.DataFrame):
        self.original_df = df.copy()
        self.df = df.copy()
        self.report = CleaningReport(original_shape=df.shape)

    # ── Step 1: Normalize Column Names ────────────────────────────────────────
    def normalize_column_names(self):
        """Strip whitespace, lowercase, replace spaces/dashes with underscores."""
        old_cols = self.df.columns.tolist()
        self.df.columns = [
            col.strip().lower()
               .replace(' ', '_').replace('-', '_')
               .replace('(', '').replace(')', '')
               .replace('%', 'pct').rstrip('_')
            for col in self.df.columns
        ]
        new_cols = self.df.columns.tolist()
        changed = [(o, n) for o, n in zip(old_cols, new_cols) if o != n]
        if changed:
            self.report.add_action(f"Normalized {len(changed)} column name(s)")
        return self

    # ── Step 2: Drop All-Null Columns ─────────────────────────────────────────
    def drop_all_null_columns(self):
        """Drop columns where every value is null."""
        null_cols = [col for col in self.df.columns if self.df[col].isnull().all()]
        if null_cols:
            self.df = self.df.drop(columns=null_cols)
            self.report.add_issue(f"Found {len(null_cols)} fully empty column(s): {null_cols}")
            self.report.add_action(f"Dropped {len(null_cols)} fully empty column(s): {null_cols}")
        return self

    # ── Step 3: Remove Duplicates ─────────────────────────────────────────────
    def drop_duplicates(self):
        """Remove exact duplicate rows."""
        n_before = len(self.df)
        self.df = self.df.drop_duplicates()
        n_removed = n_before - len(self.df)
        if n_removed > 0:
            self.report.add_issue(f"Found {n_removed} duplicate row(s)")
            self.report.add_action(f"Removed {n_removed} duplicate row(s)")
        return self

    # ── Step 4: Fix Data Types ────────────────────────────────────────────────
    def fix_data_types(self):
        """
        For object columns:
        1. Strip common currency/symbol prefixes first.
        2. Try numeric conversion.
        3. Try datetime conversion.
        Only converts if >= 80% of non-null values successfully convert.
        """
        CURRENCY_SYMBOLS = ['$', 'USD', 'EUR', 'GBP', 'BDT', ',']

        for col in self.df.select_dtypes(include='object').columns:
            n_valid = int(self.df[col].notna().sum())
            if n_valid == 0:
                continue

            # Strip currency/whitespace symbols from string values
            stripped = self.df[col].astype(str).str.strip()
            for sym in CURRENCY_SYMBOLS:
                stripped = stripped.str.replace(sym, '', regex=False)
            stripped = stripped.str.strip()

            # Replace 'nan' strings (from astype(str) on NaN) back to NaN
            stripped = stripped.replace('nan', np.nan)

            # Try numeric on stripped values
            converted_num = pd.to_numeric(stripped, errors='coerce')
            n_converted = int(converted_num.notna().sum())
            if n_valid > 0 and n_converted / n_valid >= 0.8:
                converted_num[self.df[col].isna()] = np.nan
                self.df[col] = converted_num
                self.report.add_action(f"Converted '{col}' to numeric")
                continue

            # Try datetime (suppress format inference warnings)
            try:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    converted_dt = pd.to_datetime(self.df[col], errors='coerce')
                n_dt = int(converted_dt.notna().sum())
                if n_valid > 0 and n_dt / n_valid >= 0.8:
                    self.df[col] = converted_dt
                    self.report.add_action(f"Converted '{col}' to datetime")
            except Exception:
                pass

        return self

    # ── Missing Value Summary ─────────────────────────────────────────────────
    def get_missing_summary(self) -> list[dict]:
        """Return list of dicts for columns that have missing values."""
        missing = self.df.isnull().sum()
        missing = missing[missing > 0]
        result = []
        for col, count in missing.items():
            pct = round(count / len(self.df) * 100, 1)
            dtype = "numeric" if pd.api.types.is_numeric_dtype(self.df[col]) else "text"
            result.append({
                'column': col,
                'missing_count': int(count),
                'missing_pct': pct,
                'dtype': dtype
            })
        return result

    # ── Handle Missing Values ─────────────────────────────────────────────────
    def handle_missing_values(self, strategy: dict):
        """
        strategy: { col_name: 'mean' | 'median' | 'mode' | 'drop' | <custom_value> }
        """
        for col, method in strategy.items():
            if col not in self.df.columns:
                continue
            n_missing = int(self.df[col].isnull().sum())
            if n_missing == 0:
                continue

            is_numeric = pd.api.types.is_numeric_dtype(self.df[col])

            if method == 'drop':
                self.df = self.df.dropna(subset=[col])
                self.report.add_action(f"Dropped {n_missing} rows where '{col}' was missing")

            elif method == 'mean' and is_numeric:
                val = round(self.df[col].mean(), 4)
                self.df[col] = self.df[col].fillna(val)
                self.report.add_action(f"Filled {n_missing} missing '{col}' with mean ({val})")

            elif method == 'median' and is_numeric:
                val = round(self.df[col].median(), 4)
                self.df[col] = self.df[col].fillna(val)
                self.report.add_action(f"Filled {n_missing} missing '{col}' with median ({val})")

            elif method == 'mode':
                val = self.df[col].mode()
                if len(val) > 0:
                    self.df[col] = self.df[col].fillna(val[0])
                    self.report.add_action(f"Filled {n_missing} missing '{col}' with mode ('{val[0]}')")

            else:
                # Custom value fallback
                self.df[col] = self.df[col].fillna(method)
                self.report.add_action(f"Filled {n_missing} missing '{col}' with '{method}'")

        return self

    # ── Outlier Detection ─────────────────────────────────────────────────────
    def detect_outliers(self) -> list[dict]:
        """
        IQR-based outlier detection for numeric columns.
        Returns list of dicts with column, count, bounds.
        """
        result = []
        numeric_cols = self.df.select_dtypes(include='number').columns
        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            if IQR == 0:
                continue
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            mask = (self.df[col] < lower) | (self.df[col] > upper)
            count = int(mask.sum())
            if count > 0:
                result.append({
                    'column': col,
                    'count': count,
                    'lower_bound': round(lower, 2),
                    'upper_bound': round(upper, 2)
                })
        return result

    # ── Handle Outliers ───────────────────────────────────────────────────────
    def handle_outliers(self, strategy: dict):
        """
        strategy: { col_name: 'cap' | 'remove' | 'flag' }
        'keep' should be filtered out before passing here.
        """
        numeric_cols = self.df.select_dtypes(include='number').columns.tolist()
        for col, method in strategy.items():
            if col not in self.df.columns or col not in numeric_cols:
                continue
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            if IQR == 0:
                continue
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            mask = (self.df[col] < lower) | (self.df[col] > upper)
            n = int(mask.sum())
            if n == 0:
                continue

            if method == 'cap':
                self.df[col] = self.df[col].clip(lower=lower, upper=upper)
                self.report.add_action(f"Capped {n} outliers in '{col}' → [{lower:.2f}, {upper:.2f}]")

            elif method == 'remove':
                self.df = self.df[~mask]
                self.report.add_action(f"Removed {n} outlier rows from '{col}'")

            elif method == 'flag':
                flag_col = f"{col}_outlier"
                self.df[flag_col] = mask.astype(int)
                self.report.add_action(f"Flagged {n} outliers in '{col}' → new column '{flag_col}'")

        return self

    # ── Finalize ──────────────────────────────────────────────────────────────
    def finalize(self):
        """Update final shape and return (cleaned_df, report)."""
        self.report.final_shape = self.df.shape
        return self.df.reset_index(drop=True), self.report
