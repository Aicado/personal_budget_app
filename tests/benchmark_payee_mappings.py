
import time
import polars as pl
import os
import sys
from pathlib import Path
from datetime import date

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.database import TransactionDatabase

def benchmark_mappings():
    db_path = "tests/test_mappings.duckdb"
    if os.path.exists(db_path):
        os.remove(db_path)

    db = TransactionDatabase(db_path)

    # 1. Populating payee_mappings with many rows
    num_mappings = 500000
    print(f"Populating payee_mappings with {num_mappings} rows...")

    # Create mock mappings in chunks to avoid memory issues
    chunk_size = 100000
    for i in range(0, num_mappings, chunk_size):
        mappings = []
        for j in range(i, min(i + chunk_size, num_mappings)):
            mappings.append({
                "payee": f"Payee {j}",
                "category": f"Category {j % 100}",
                "category_group": f"Group {j % 10}",
                "confidence": 0.9
            })
        df_mappings = pl.DataFrame(mappings)
        db.conn.register("temp_mappings", df_mappings.to_arrow())
        db.conn.execute("INSERT INTO payee_mappings (payee, category, category_group, confidence) SELECT * FROM temp_mappings")
        db.conn.unregister("temp_mappings")

    # 2. Benchmark insert_transactions with a small number of transactions
    num_tx = 10
    print(f"Benchmarking insert_transactions with {num_tx} transactions...")

    df_tx = pl.DataFrame({
        "date": [date(2023, 1, 1)] * num_tx,
        "payee": [f"Payee {i}" for i in range(num_tx)],
        "category": ["Uncategorized"] * num_tx,
        "outflow": [10.0] * num_tx,
        "inflow": [0.0] * num_tx,
        "amount": [-10.0] * num_tx
    })

    # Measure time
    start_time = time.perf_counter()
    db.insert_transactions(df_tx, "test.csv")
    end_time = time.perf_counter()

    print(f"Time taken with {num_mappings} mappings: {end_time - start_time:.4f} seconds")

    # Cleanup
    db.close()
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    benchmark_mappings()
