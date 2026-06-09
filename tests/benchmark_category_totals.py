import time
import polars as pl
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.transaction_analyzer import TransactionAnalyzer

def run_benchmark():
    num_rows = 1000000
    num_categories = 1000
    print(f"Generating {num_rows} transactions with {num_categories} categories...")

    df = pl.DataFrame({
        "category": [f"Category {i % num_categories}" for i in range(num_rows)],
        "outflow": [10.5] * num_rows,
        "inflow": [0.0] * num_rows,
    })

    analyzer = TransactionAnalyzer()
    analyzer.df = df

    print("Starting benchmark for get_category_totals...")
    iterations = 10
    times = []
    for i in range(iterations):
        start_time = time.perf_counter()
        result = analyzer.get_category_totals()
        end_time = time.perf_counter()
        times.append(end_time - start_time)
        print(f"Iteration {i+1}: {times[-1]:.4f} seconds")

    avg_time = sum(times) / iterations
    print(f"\nAverage execution time for get_category_totals: {avg_time:.4f} seconds")
    print(f"Result size: {len(result)} categories")

if __name__ == "__main__":
    run_benchmark()
