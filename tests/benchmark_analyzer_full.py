import time
import polars as pl
import datetime
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.transaction_analyzer import TransactionAnalyzer

def run_benchmark():
    num_rows = 1000000
    print(f"Generating {num_rows} mock transactions...")

    # Create a dataframe that mimics what load_csv(try_parse_dates=True) might return
    df = pl.DataFrame({
        "Date": [datetime.date(2023, 1, 1)] * num_rows,
        "Payee": [f"Payee {i % 100}" for i in range(num_rows)],
        "Category": [f"Group {i % 5} | Category {i % 50}" for i in range(num_rows)],
        "Outflow": [10.5 if i % 2 == 0 else 0.0 for i in range(num_rows)],
        "Inflow": [0.0 if i % 2 == 0 else 20.0 for i in range(num_rows)],
    })

    analyzer = TransactionAnalyzer()

    print("Benchmarking parse_transactions...")
    start = time.perf_counter()
    analyzer.parse_transactions(df.clone())
    print(f"parse_transactions: {time.perf_counter() - start:.4f}s")

    print("Benchmarking get_monthly_trends...")
    start = time.perf_counter()
    analyzer.get_monthly_trends()
    print(f"get_monthly_trends: {time.perf_counter() - start:.4f}s")

    print("Benchmarking get_category_trends...")
    start = time.perf_counter()
    analyzer.get_category_trends()
    print(f"get_category_trends: {time.perf_counter() - start:.4f}s")

    print("Benchmarking get_category_totals...")
    start = time.perf_counter()
    analyzer.get_category_totals()
    print(f"get_category_totals: {time.perf_counter() - start:.4f}s")

    print("Benchmarking get_summary_stats...")
    start = time.perf_counter()
    analyzer.get_summary_stats()
    print(f"get_summary_stats: {time.perf_counter() - start:.4f}s")

if __name__ == "__main__":
    run_benchmark()
