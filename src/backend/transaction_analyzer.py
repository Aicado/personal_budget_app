import io
from typing import Any, Dict

import polars as pl


class TransactionAnalyzer:
    """Analyzes Personal Budget App transaction data and generates monthly trends."""

    def __init__(self):
        self.df: pl.DataFrame | None = None

    def _clean_amount_column(self, df: pl.DataFrame, column: str) -> pl.DataFrame:
        if column not in df.columns:
            return df.with_columns(pl.lit(0.0).alias(column))

        cleaned = (
            pl.col(column)
            .cast(pl.Utf8)
            .str.replace_all("$", "", literal=True)
            .str.replace_all(",", "", literal=True)
            .str.strip_chars()
        )

        return df.with_columns(
            pl.when((cleaned == "") | (cleaned.is_null()))
            .then(0.0)
            .otherwise(cleaned.cast(pl.Float64, strict=False))
            .fill_null(0.0)
            .alias(column)
        )

    def load_csv(self, csv_content: str) -> pl.DataFrame:
        """Load CSV file content into a DataFrame."""
        return pl.read_csv(io.StringIO(csv_content), try_parse_dates=True)

    def load_file(self, file_path: str) -> pl.DataFrame:
        """Load CSV file from path into a DataFrame."""
        return pl.read_csv(file_path, try_parse_dates=True)

    def parse_transactions(self, df: pl.DataFrame) -> pl.DataFrame:
        """Parse and clean transaction data from DataFrame."""
        df = df.clone()

        # Standardize column names
        df.columns = [col.strip().lower() for col in df.columns]

        # Parse date column - handle multiple date column names
        date_col = None
        for potential_date in ["date", "transaction date", "posted date"]:
            if potential_date in df.columns:
                date_col = potential_date
                break

        if date_col:
            df = df.with_columns(
                pl.col(date_col).cast(pl.Utf8).str.strptime(pl.Date, strict=False).alias("date")
            )
        else:
            raise ValueError(f"CSV must contain a date column. Available columns: {df.columns}")

        # Handle outflow/inflow vs debit/credit formats
        if "outflow" in df.columns and "inflow" in df.columns:
            df = self._clean_amount_column(df, "outflow")
            df = self._clean_amount_column(df, "inflow")
        elif "debit" in df.columns and "credit" in df.columns:
            df = self._clean_amount_column(df, "debit")
            df = self._clean_amount_column(df, "credit")
            df = df.with_columns(
                pl.col("debit").alias("outflow"),
                pl.col("credit").alias("inflow"),
            )
        else:
            df = df.with_columns(
                pl.lit(0.0).alias("outflow"),
                pl.lit(0.0).alias("inflow"),
            )

        df = df.with_columns((pl.col("inflow") - pl.col("outflow")).alias("amount"))

        if "category group/category" in df.columns:
            df = df.with_columns(
                pl.col("category group/category")
                .fill_null("Uncategorized")
                .cast(pl.Utf8)
                .alias("category")
            )
        elif "category" in df.columns:
            df = df.with_columns(
                pl.col("category").fill_null("Uncategorized").cast(pl.Utf8).alias("category")
            )
        else:
            df = df.with_columns(
                pl.lit("Uncategorized").alias("category"),
                pl.lit("Uncategorized").alias("category_group"),
            )

        if "category" in df.columns and "category_group" not in df.columns:
            df = df.with_columns(
                pl.col("category")
                .str.split("|")
                .list.get(0)
                .str.strip_chars()
                .alias("category_group"),
                pl.col("category").str.split("|").list.get(-1).str.strip_chars().alias("category"),
            )
        elif "category group/category" in df.columns:
            df = df.with_columns(
                pl.col("category")
                .str.split("|")
                .list.get(0)
                .str.strip_chars()
                .alias("category_group"),
                pl.col("category").str.split("|").list.get(-1).str.strip_chars().alias("category"),
            )

        df = df.with_columns(
            pl.when(pl.col("inflow") > pl.col("outflow"))
            .then(pl.lit("income"))
            .when(pl.col("outflow") > pl.col("inflow"))
            .then(pl.lit("expense"))
            .otherwise(pl.lit("transfer"))
            .alias("transaction_type"),
            pl.col("date").dt.strftime("%Y-%m").alias("month_str"),
        )

        self.df = df
        return df

    def get_monthly_trends(self, df: pl.DataFrame | None = None) -> Dict[str, Any]:
        """Calculate monthly spending/income trends."""
        if df is None:
            df = self.df

        if df is None:
            raise ValueError("No data loaded. Call parse_transactions first.")

        monthly = (
            df.group_by("month_str")
            .agg(
                [
                    pl.col("amount").sum().round(2).alias("amount"),
                    pl.col("outflow").sum().round(2).alias("outflow"),
                    pl.col("inflow").sum().round(2).alias("inflow"),
                ]
            )
            .sort("month_str")
        )

        return {
            "months": monthly["month_str"].to_list(),
            "net_amounts": monthly["amount"].to_list(),
            "outflows": monthly["outflow"].to_list(),
            "inflows": monthly["inflow"].to_list(),
        }

    def get_category_trends(self, df: pl.DataFrame | None = None) -> Dict[str, Any]:
        """Get spending trends by category over time."""
        if df is None:
            df = self.df

        if df is None:
            raise ValueError("No data loaded. Call parse_transactions first.")

        category_monthly = (
            df.filter(pl.col("outflow") > 0)
            .group_by(["month_str", "category"])
            .agg(pl.col("outflow").sum().alias("outflow"))
            .sort(["month_str", "category"])
        )

        months = sorted(category_monthly["month_str"].unique().to_list())
        categories = sorted(category_monthly["category"].unique().to_list())

        pivot = category_monthly.pivot(
            values="outflow",
            index="month_str",
            columns="category",
            aggregate_function="sum",
        ).fill_null(0.0)

        result = {"months": months, "categories": categories, "data": {}}
        for category in categories:
            result["data"][category] = (
                pivot[category].round(2).to_list()
                if category in pivot.columns
                else [0.0] * len(months)
            )

        return result

    def get_category_totals(self, df: pl.DataFrame | None = None) -> Dict[str, float]:
        """Get total spending by category."""
        if df is None:
            df = self.df

        if df is None:
            raise ValueError("No data loaded. Call parse_transactions first.")

        totals = (
            df.filter(pl.col("outflow") > 0)
            .group_by("category")
            .agg(pl.col("outflow").sum().round(2).alias("outflow"))
            .sort("category")
        )

        return {row["category"]: float(row["outflow"]) for row in totals.to_dicts()}

    def get_summary_stats(self, df: pl.DataFrame | None = None) -> Dict[str, float]:
        """Get summary statistics."""
        if df is None:
            df = self.df

        if df is None:
            raise ValueError("No data loaded. Call parse_transactions first.")

        total_inflow = float(df["inflow"].sum() or 0.0)
        total_outflow = float(df["outflow"].sum() or 0.0)
        monthly = df.group_by("month_str").agg(
            [
                pl.col("inflow").sum().alias("monthly_inflow"),
                pl.col("outflow").sum().alias("monthly_outflow"),
            ]
        )

        avg_monthly_inflow = float(monthly["monthly_inflow"].mean() or 0.0)
        avg_monthly_outflow = float(monthly["monthly_outflow"].mean() or 0.0)

        return {
            "total_inflow": round(total_inflow, 2),
            "total_outflow": round(total_outflow, 2),
            "net_total": round(total_inflow - total_outflow, 2),
            "avg_monthly_inflow": round(avg_monthly_inflow, 2),
            "avg_monthly_outflow": round(avg_monthly_outflow, 2),
            "transaction_count": df.height,
            "unique_categories": int(df["category"].n_unique()),
            "date_range": {
                "start": str(df["date"].min()),
                "end": str(df["date"].max()),
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
