import asyncio
import time
import os
import sys
import polars as pl
from datetime import date

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.database import TransactionDatabase

class MockCategorizer:
    def __init__(self, delay=0.1):
        self.delay = delay
        self.call_count = 0

    async def categorize_transaction(self, payee, amount, date, categories):
        self.call_count += 1
        await asyncio.sleep(self.delay)
        return {
            "category": "Mock Category",
            "category_group": "Mock Group",
            "confidence": 0.9
        }

def run_benchmark():
    db_path = "tests/benchmark_llm.duckdb"
    if os.path.exists(db_path):
        os.remove(db_path)

    db = TransactionDatabase(db_path)

    # Create a dataframe with multiple unique payees that need categorization
    num_unique_payees = 10
    payees = [f"Payee {i}" for i in range(num_unique_payees)]

    df = pl.DataFrame({
        "date": [date(2024, 1, 1)] * num_unique_payees,
        "payee": payees,
        "category": ["Uncategorized"] * num_unique_payees,
        "outflow": [10.0] * num_unique_payees,
        "inflow": [0.0] * num_unique_payees,
        "amount": [-10.0] * num_unique_payees,
    })

    # Ensure proper types for Polars
    df = df.with_columns(pl.col("date").cast(pl.Date))

    categorizer = MockCategorizer(delay=0.1) # 100ms per call

    print(f"Running parallel categorization for {num_unique_payees} payees...")
    start_time = time.perf_counter()
    # This will use the NEW parallel implementation
    db.insert_transactions(df, "benchmark.csv", categorizer=categorizer)
    end_time = time.perf_counter()

    parallel_time = end_time - start_time
    print(f"Parallel execution time: {parallel_time:.4f} seconds")
    print(f"Total LLM calls: {categorizer.call_count}")

    # Expected time should be slightly more than 0.1s (one delay) instead of 1.0s (10 * delay)
    if parallel_time < 0.5: # Generous margin for overhead
        print("✅ Performance gain verified! Execution is concurrent.")
    else:
        print("❌ Performance gain not significant. Check implementation.")

    db.close()
    if os.path.exists(db_path):
        os.remove(db_path)

    return parallel_time

if __name__ == "__main__":
    run_benchmark()
