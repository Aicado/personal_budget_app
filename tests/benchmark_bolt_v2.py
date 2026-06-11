import time
import polars as pl
import random
import io
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.transaction_analyzer import TransactionAnalyzer

def benchmark_get_category_totals():
    print("--- Benchmarking get_category_totals ---")
    num_rows = 1_000_000
    num_categories = 1000
    df = pl.DataFrame({
        "category": [f"Cat_{i % num_categories}" for i in range(num_rows)],
        "outflow": [random.random() * 100 for _ in range(num_rows)]
    })

    totals = (
        df.filter(pl.col("outflow") > 0)
        .group_by("category")
        .agg(pl.col("outflow").sum().round(2).alias("outflow"))
        .sort("category")
    )

    # Method 1: to_dicts()
    start = time.perf_counter()
    res1 = {row["category"]: float(row["outflow"]) for row in totals.to_dicts()}
    end = time.perf_counter()
    t1 = end - start
    print(f"to_dicts() took {t1:.6f}s")

    # Method 2: dict(zip(...))
    start = time.perf_counter()
    res2 = dict(zip(totals["category"], totals["outflow"]))
    end = time.perf_counter()
    t2 = end - start
    print(f"dict(zip()) took {t2:.6f}s")

    print(f"Speedup: {t1/t2:.2f}x")

def benchmark_get_summary_stats_extraction():
    print("\n--- Benchmarking get_summary_stats extraction ---")
    df = pl.DataFrame({
        "total_inflow": [1000.0],
        "total_outflow": [500.0],
        "unique_categories": [10],
        "min_date": ["2023-01-01"],
        "max_date": ["2023-12-31"]
    })

    iterations = 10000

    start = time.perf_counter()
    for _ in range(iterations):
        res = df.to_dicts()[0]
    end = time.perf_counter()
    t1 = end - start
    print(f"to_dicts()[0] took {t1:.6f}s for {iterations} iterations")

    start = time.perf_counter()
    for _ in range(iterations):
        res = {
            "total_inflow": df["total_inflow"][0],
            "total_outflow": df["total_outflow"][0],
            "unique_categories": df["unique_categories"][0],
            "min_date": df["min_date"][0],
            "max_date": df["max_date"][0],
        }
    end = time.perf_counter()
    t2 = end - start
    print(f"Manual extraction took {t2:.6f}s for {iterations} iterations")

    print(f"Speedup: {t1/t2:.2f}x")

if __name__ == "__main__":
    benchmark_get_category_totals()
    benchmark_get_summary_stats_extraction()
