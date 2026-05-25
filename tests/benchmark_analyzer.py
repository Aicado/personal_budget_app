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
    # if it correctly identifies dates and numbers.
    df = pl.DataFrame({
        "Date": [datetime.date(2023, 1, 1)] * num_rows,
        "Payee": ["Test Payee"] * num_rows,
        "Category": ["Food | Groceries"] * num_rows,
        "Outflow": [10.5] * num_rows,
        "Inflow": [0.0] * num_rows,
    })

    analyzer = TransactionAnalyzer()

    print("Starting benchmark for parse_transactions...")
    iterations = 5
    times = []
    for i in range(iterations):
        start_time = time.perf_counter()
        # We need to clone df because parse_transactions modifies it (or at least clones it internally)
        analyzer.parse_transactions(df.clone())
        end_time = time.perf_counter()
        times.append(end_time - start_time)
        print(f"Iteration {i+1}: {times[-1]:.4f} seconds")

    avg_time = sum(times) / iterations
    print(f"\nAverage execution time for parse_transactions: {avg_time:.4f} seconds")

if __name__ == "__main__":
    run_benchmark()
