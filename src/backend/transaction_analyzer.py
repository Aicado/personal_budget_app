import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import io


class TransactionAnalyzer:
    """Analyzes YNAB transaction data and generates monthly trends."""

    def __init__(self):
        self.df = None
        self.monthly_trends = None

    def load_csv(self, csv_content: str) -> pd.DataFrame:
        """Load CSV file content into a DataFrame."""
        return pd.read_csv(io.StringIO(csv_content))

    def load_file(self, file_path: str) -> pd.DataFrame:
        """Load CSV file from path into a DataFrame."""
        return pd.read_csv(file_path)

    def parse_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse and clean transaction data from DataFrame."""
        # Make a copy to avoid modifying original
        df = df.copy()

        print(f"DEBUG: Original columns: {df.columns.tolist()}")

        # Standardize column names
        df.columns = df.columns.str.strip().str.lower()
        
        print(f"DEBUG: Standardized columns: {df.columns.tolist()}")

        # Parse date column - handle multiple date column names
        date_col = None
        for potential_date in ["date", "transaction date", "posted date"]:
            if potential_date in df.columns:
                date_col = potential_date
                break
        
        if date_col:
            df["date"] = pd.to_datetime(df[date_col])
        else:
            raise ValueError(f"CSV must contain a date column. Available columns: {df.columns.tolist()}")

        # Handle outflow/inflow vs debit/credit formats
        if "outflow" in df.columns and "inflow" in df.columns:
            # YNAB format
            for col in ["outflow", "inflow"]:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace("$", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.strip()
                    .replace("", "0")
                    .astype(float)
                    .fillna(0)
                )
            df["outflow"] = df["outflow"].fillna(0)
            df["inflow"] = df["inflow"].fillna(0)
        elif "debit" in df.columns and "credit" in df.columns:
            # Bank statement format - debit is outflow, credit is inflow
            for col in ["debit", "credit"]:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace("$", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.strip()
                    .replace("", "0")
                    .astype(float)
                    .fillna(0)
                )
            df["outflow"] = df["debit"].fillna(0)
            df["inflow"] = df["credit"].fillna(0)
        else:
            # Default to zeros if no amount columns exist
            df["outflow"] = 0.0
            df["inflow"] = 0.0

        # Create net amount column
        df["amount"] = df["inflow"] - df["outflow"]

        # Extract category - handle hierarchical categories
        # YNAB format has "Category Group/Category" or just "Category"
        if "category group/category" in df.columns:
            df["category"] = df["category group/category"].fillna("Uncategorized")
            df["category_group"] = df["category"].str.split("|").str[0].str.strip()
            df["category"] = df["category"].str.split("|").str[-1].str.strip()
        elif "category" in df.columns:
            df["category"] = df["category"].fillna("Uncategorized")
            df["category_group"] = df["category"].str.split("|").str[0].str.strip()
            df["category"] = df["category"].str.split("|").str[-1].str.strip()
        else:
            df["category"] = "Uncategorized"
            df["category_group"] = "Uncategorized"

        # Determine transaction type for income/expense tracking
        df["transaction_type"] = np.where(
            df["inflow"] > df["outflow"],
            "income",
            np.where(df["outflow"] > df["inflow"], "expense", "transfer")
        )

        # Extract month-year for grouping
        df["month"] = df["date"].dt.to_period("M")
        df["month_str"] = df["date"].dt.strftime("%Y-%m")

        self.df = df
        return df

    def get_monthly_trends(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """Calculate monthly spending/income trends."""
        if df is None:
            df = self.df

        if df is None:
            raise ValueError("No data loaded. Call parse_transactions first.")

        # Group by month and sum amounts
        monthly = df.groupby("month_str").agg(
            {
                "amount": "sum",
                "outflow": "sum",
                "inflow": "sum",
            }
        ).reset_index()

        monthly = monthly.sort_values("month_str")

        return {
            "months": monthly["month_str"].tolist(),
            "net_amounts": monthly["amount"].round(2).tolist(),
            "outflows": monthly["outflow"].round(2).tolist(),
            "inflows": monthly["inflow"].round(2).tolist(),
        }

    def get_category_trends(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """Get spending trends by category over time."""
        if df is None:
            df = self.df

        if df is None:
            raise ValueError("No data loaded. Call parse_transactions first.")

        # Group by month and category, sum outflows
        category_monthly = (
            df[df["outflow"] > 0]
            .groupby(["month_str", "category"])["outflow"]
            .sum()
            .reset_index()
        )

        # Get unique months and categories
        months = sorted(category_monthly["month_str"].unique())
        categories = sorted(category_monthly["category"].unique())

        # Create a pivot table
        pivot = category_monthly.pivot(
            index="month_str", columns="category", values="outflow"
        ).fillna(0)

        result = {
            "months": months,
            "categories": categories,
            "data": {},
        }

        for category in categories:
            if category in pivot.columns:
                result["data"][category] = pivot[category].round(2).tolist()
            else:
                result["data"][category] = [0] * len(months)

        return result

    def get_category_totals(self, df: pd.DataFrame = None) -> Dict[str, float]:
        """Get total spending by category."""
        if df is None:
            df = self.df

        if df is None:
            raise ValueError("No data loaded. Call parse_transactions first.")

        # Sum outflows by category
        totals = (
            df[df["outflow"] > 0].groupby("category")["outflow"].sum().round(2)
        )

        return totals.to_dict()

    def get_summary_stats(self, df: pd.DataFrame = None) -> Dict[str, float]:
        """Get summary statistics."""
        if df is None:
            df = self.df

        if df is None:
            raise ValueError("No data loaded. Call parse_transactions first.")

        return {
            "total_inflow": float(df["inflow"].sum().round(2)),
            "total_outflow": float(df["outflow"].sum().round(2)),
            "net_total": float((df["inflow"].sum() - df["outflow"].sum()).round(2)),
            "avg_monthly_inflow": float(df.groupby("month_str")["inflow"].sum().mean().round(2)),
            "avg_monthly_outflow": float(df.groupby("month_str")["outflow"].sum().mean().round(2)),
            "transaction_count": len(df),
            "unique_categories": df["category"].nunique(),
            "date_range": {
                "start": str(df["date"].min().date()),
                "end": str(df["date"].max().date()),
            },
        }


def analyze_file(file_path: str) -> Dict[str, Any]:
    """Convenience function to analyze a single file."""
    analyzer = TransactionAnalyzer()
    df = analyzer.load_file(file_path)
    analyzer.parse_transactions(df)

    return {
        "monthly_trends": analyzer.get_monthly_trends(),
        "category_trends": analyzer.get_category_trends(),
        "category_totals": analyzer.get_category_totals(),
        "summary_stats": analyzer.get_summary_stats(),
    }
