import time
import polars as pl
import os
import sys
import datetime

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.transaction_analyzer import TransactionAnalyzer

def benchmark_to_dicts(totals):
    start_time = time.perf_counter()
    res = {row["category"]: float(row["outflow"]) for row in totals.to_dicts()}
    end_time = time.perf_counter()
    return end_time - start_time

def benchmark_dict_zip(totals):
    start_time = time.perf_counter()
    res = dict(zip(totals["category"], totals["outflow"]))
    end_time = time.perf_counter()
    return end_time - start_time

def benchmark_to_dicts_0(df):
    start_time = time.perf_counter()
    res = df.to_dicts()[0]
    end_time = time.perf_counter()
    return end_time - start_time

def benchmark_row_0_named(df):
    start_time = time.perf_counter()
    res = df.row(0, named=True)
    end_time = time.perf_counter()
    return end_time - start_time

def run_comparison():
    num_rows = 1000000
    num_categories = 1000
    print(f"Generating {num_rows} transactions with {num_categories} categories...")

    df = pl.DataFrame({
        "category": [f"Category {i % num_categories}" for i in range(num_rows)],
        "outflow": [10.5] * num_rows,
        "inflow": [0.0] * num_rows,
        "date": [datetime.date(2023, 1, 1)] * num_rows,
    })

    analyzer = TransactionAnalyzer()
    analyzer.df = df

    totals = (
        df.filter(pl.col("outflow") > 0)
        .group_by("category")
        .agg(pl.col("outflow").sum().round(2).alias("outflow"))
        .sort("category")
    )

    iterations = 100
    to_dicts_times = []
    dict_zip_times = []

    # Warmup
    benchmark_to_dicts(totals)
    benchmark_dict_zip(totals)

    for i in range(iterations):
        to_dicts_times.append(benchmark_to_dicts(totals))
        dict_zip_times.append(benchmark_dict_zip(totals))

    avg_to_dicts = sum(to_dicts_times) / iterations
    avg_dict_zip = sum(dict_zip_times) / iterations

    print(f"\n[get_category_totals] Result size: {len(totals)} categories")
    print(f"Average execution time for to_dicts: {avg_to_dicts:.6f} seconds")
    print(f"Average execution time for dict(zip(...)): {avg_dict_zip:.6f} seconds")
    print(f"Speedup: {avg_to_dicts / avg_dict_zip:.2f}x")

    stats_df = df.select(
        [
            pl.col("inflow").sum().alias("total_inflow"),
            pl.col("outflow").sum().alias("total_outflow"),
            pl.col("category").n_unique().alias("unique_categories"),
            pl.col("date").min().alias("min_date"),
            pl.col("date").max().alias("max_date"),
        ]
    )

    to_dicts_0_times = []
    row_0_named_times = []

    # Warmup
    benchmark_to_dicts_0(stats_df)
    benchmark_row_0_named(stats_df)

    for i in range(iterations):
        to_dicts_0_times.append(benchmark_to_dicts_0(stats_df))
        row_0_named_times.append(benchmark_row_0_named(stats_df))

    avg_to_dicts_0 = sum(to_dicts_0_times) / iterations
    avg_row_0_named = sum(row_0_named_times) / iterations

    print(f"\n[get_summary_stats] Result size: 1 row, {len(stats_df.columns)} columns")
    print(f"Average execution time for to_dicts()[0]: {avg_to_dicts_0:.6f} seconds")
    print(f"Average execution time for row(0, named=True): {avg_row_0_named:.6f} seconds")
    if avg_row_0_named > 0:
        print(f"Speedup: {avg_to_dicts_0 / avg_row_0_named:.2f}x")

if __name__ == "__main__":
    run_comparison()
