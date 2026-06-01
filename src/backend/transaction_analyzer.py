import io
from typing import Any, Dict

import polars as pl


class TransactionAnalyzer:
    """Analyzes Personal Budget App transaction data and generates monthly trends."""

    def __init__(self):
        self.df: pl.DataFrame | None = None

    def _clean_amount_column(self, column: str, schema: pl.Schema) -> pl.Expr:
        """Returns a Polars expression to clean a currency column."""
        if column not in schema:
            return pl.lit(0.0).alias(column)

        # If already numeric, just fill nulls and return to avoid expensive string operations
        if schema[column].is_numeric():
            return pl.col(column).fill_null(0.0).cast(pl.Float64).alias(column)

        # Use literal=True to avoid regex overhead and correctly handle $
        # Use strict=False with fill_null for a single-pass vectorized cleaning
        return (
            pl.col(column)
            .cast(pl.Utf8)
            .str.replace_all("$", "", literal=True)
            .str.replace_all(",", "", literal=True)
            .str.strip_chars()
            .cast(pl.Float64, strict=False)
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
        """Parse and clean transaction data from DataFrame using combined operations for performance."""
        df = df.clone()

        # Standardize column names
        df.columns = [col.strip().lower() for col in df.columns]
        schema = df.schema

        # Step 1: Initial cleaning, date parsing, and amount normalization
        # Combining these into a single with_columns call reduces DataFrame cloning overhead.
        exprs = []

        # Date parsing
        date_col = next(
            (c for c in ["date", "transaction date", "posted date"] if c in df.columns), None
        )
        if date_col:
            if schema[date_col] in [pl.Date, pl.Datetime]:
                exprs.append(pl.col(date_col).cast(pl.Date).alias("date"))
            else:
                exprs.append(
                    pl.col(date_col).cast(pl.Utf8).str.strptime(pl.Date, strict=False).alias("date")
                )
        else:
            raise ValueError(f"CSV must contain a date column. Available columns: {df.columns}")

        # Amount cleaning
        if "outflow" in df.columns and "inflow" in df.columns:
            exprs.append(self._clean_amount_column("outflow", schema))
            exprs.append(self._clean_amount_column("inflow", schema))
        elif "debit" in df.columns and "credit" in df.columns:
            exprs.append(self._clean_amount_column("debit", schema).alias("outflow"))
            exprs.append(self._clean_amount_column("credit", schema).alias("inflow"))
        else:
            exprs.append(pl.lit(0.0).alias("outflow"))
            exprs.append(pl.lit(0.0).alias("inflow"))

        # Category normalization
        if "category group/category" in df.columns:
            exprs.append(
                pl.col("category group/category")
                .fill_null("Uncategorized")
                .cast(pl.Utf8)
                .alias("category")
            )
        elif "category" in df.columns:
            exprs.append(
                pl.col("category").fill_null("Uncategorized").cast(pl.Utf8).alias("category")
            )
        else:
            exprs.append(pl.lit("Uncategorized").alias("category"))
            exprs.append(pl.lit("Uncategorized").alias("category_group"))

        df = df.with_columns(exprs)

        # Step 2: Derived columns and category splitting
        # These depend on columns created or modified in Step 1.
        exprs2 = []

        exprs2.append((pl.col("inflow") - pl.col("outflow")).alias("amount"))

        # Category and category group splitting
        # Splitting once and accessing indices is more efficient than multiple str.split calls.
        if "category_group" not in df.columns:
            category_split = pl.col("category").str.split("|")
            exprs2.append(category_split.list.get(0).str.strip_chars().alias("category_group"))
            exprs2.append(category_split.list.get(-1).str.strip_chars().alias("category"))

        # Final pass for metadata
        exprs2.extend(
            [
                pl.when(pl.col("inflow") > pl.col("outflow"))
                .then(pl.lit("income"))
                .when(pl.col("outflow") > pl.col("inflow"))
                .then(pl.lit("expense"))
                .otherwise(pl.lit("transfer"))
                .alias("transaction_type"),
                pl.col("date").dt.strftime("%Y-%m").alias("month_str"),
            ]
        )

        df = df.with_columns(exprs2)

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
            on="category",
            index="month_str",
            values="outflow",
            aggregate_function="sum",
        ).fill_null(0.0)

        # Use Polars to_dict(as_series=False) for a vectorized conversion to a dictionary of lists.
        # This is significantly faster than a Python-level loop over columns.
        # We use a list comprehension to build the selection expressions to ensure all categories
        # are present in the output, even if they have no transactions in the given period.
        data = pivot.select(
            [
                (
                    pl.col(cat).round(2)
                    if cat in pivot.columns
                    else pl.repeat(0.0, pivot.height).alias(cat)
                )
                for cat in categories
            ]
        ).to_dict(as_series=False)

        return {"months": months, "categories": categories, "data": data}

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

        return dict(zip(totals["category"], totals["outflow"]))

    def get_summary_stats(self, df: pl.DataFrame | None = None) -> Dict[str, Any]:
        """Get summary statistics using a single-pass vectorized aggregation for performance."""
        if df is None:
            df = self.df

        if df is None:
            raise ValueError("No data loaded. Call parse_transactions first.")

        # Single-pass aggregation for most stats to avoid scanning the same columns multiple times.
        # Use .row(0, named=True) instead of .to_dicts()[0] for more efficient single-row extraction.
        stats = df.select(
            [
                pl.col("inflow").sum().alias("total_inflow"),
                pl.col("outflow").sum().alias("total_outflow"),
                pl.col("category").n_unique().alias("unique_categories"),
                pl.col("date").min().alias("min_date"),
                pl.col("date").max().alias("max_date"),
            ]
        ).row(0, named=True)

        total_inflow = float(stats["total_inflow"] or 0.0)
        total_outflow = float(stats["total_outflow"] or 0.0)

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
            "unique_categories": int(stats["unique_categories"]),
            "date_range": {
                "start": str(stats["min_date"]),
                "end": str(stats["max_date"]),
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
