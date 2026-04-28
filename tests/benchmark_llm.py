import asyncio
import time
import polars as pl
import sys
import os
from unittest.mock import AsyncMock

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.database import TransactionDatabase

async def benchmark_llm_ingestion():
    db = TransactionDatabase("tests/benchmark_llm.duckdb")
    db.clear_tables()

    # Mock categorizer with 0.1s delay
    categorizer = AsyncMock()
    async def slow_categorize(*args, **kwargs):
        await asyncio.sleep(0.1)
        return {
            "category": "Groceries",
            "category_group": "Food",
            "confidence": 0.9
        }
    categorizer.categorize_transaction.side_effect = slow_categorize

    # Create 20 unique payees
    num_unique_payees = 20
    df = pl.DataFrame({
        "date": ["2024-01-01"] * num_unique_payees,
        "payee": [f"Payee {i}" for i in range(num_unique_payees)],
        "category": ["Uncategorized"] * num_unique_payees,
        "category_group": ["Uncategorized"] * num_unique_payees,
        "outflow": [10.0] * num_unique_payees,
        "inflow": [0.0] * num_unique_payees,
        "amount": [-10.0] * num_unique_payees,
        "transaction_type": ["expense"] * num_unique_payees,
        "month_str": ["2024-01"] * num_unique_payees
    })

    print(f"Starting serial benchmark with {num_unique_payees} unique payees...")
    start_time = time.perf_counter()
    db.insert_transactions(df, "benchmark.csv", categorizer=categorizer)
    end_time = time.perf_counter()

    duration = end_time - start_time
    print(f"Duration: {duration:.4f} seconds")

    db.close()
    if os.path.exists("tests/benchmark_llm.duckdb"):
        os.remove("tests/benchmark_llm.duckdb")

if __name__ == "__main__":
    asyncio.run(benchmark_llm_ingestion())
