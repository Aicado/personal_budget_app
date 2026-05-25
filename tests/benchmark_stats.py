import time
import os
import polars as pl
import sys
from pathlib import Path

# Add src to path so we can import the database module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.database import TransactionDatabase

def setup_benchmark_db(db_path, num_transactions=1000000):
    if os.path.exists(db_path):
        os.remove(db_path)

    db = TransactionDatabase(db_path)

    # Create mock transactions
    transactions_data = []
    categories = [f"Category {i}" for i in range(50)]
    groups = [f"Group {i // 5}" for i in range(50)]
    months = [f"2023-{m:02d}" for m in range(1, 13)]

    for i in range(num_transactions):
        cat_idx = i % 50
        month = months[(i // 100) % 12]
        transactions_data.append({
            "file_hash": f"hash_{i // 1000}",
            "account": f"Account {i % 5}",
            "account_type": "Checking",
            "account_path": f"path/to/account_{i % 5}",
            "date": f"{month}-01",
            "payee": f"Payee {i % 100}",
            "category": categories[cat_idx],
            "category_group": groups[cat_idx],
            "description": "Desc",
            "outflow": 10.0 if i % 2 == 0 else 0.0,
            "inflow": 0.0 if i % 2 == 0 else 15.0,
            "amount": -10.0 if i % 2 == 0 else 15.0,
            "transaction_type": "expense" if i % 2 == 0 else "income",
            "month_year": month,
            "file_source": "file.csv"
        })

    # Bulk insert transactions
    df = pl.DataFrame(transactions_data)
    db.conn.register("temp_insert", df.to_arrow())
    db.conn.execute("""
        INSERT INTO transactions
        (file_hash, account, account_type, account_path, date, payee, category, category_group, description, outflow, inflow, amount, transaction_type, month_year, file_source)
        SELECT file_hash, account, account_type, account_path, date, payee, category, category_group, description, outflow, inflow, amount, transaction_type, month_year, file_source
        FROM temp_insert
    """)
    db.conn.unregister("temp_insert")

    return db

def run_benchmark():
    db_path = "tests/benchmark_stats.duckdb"
    print(f"Setting up benchmark database with 1,000,000 transactions...")
    db = setup_benchmark_db(db_path)

    # Warm up
    db.get_database_stats()

    print("Starting benchmark for get_database_stats...")
    iterations = 5
    times = []
    for i in range(iterations):
        start_time = time.perf_counter()
        results = db.get_database_stats()
        end_time = time.perf_counter()
        times.append(end_time - start_time)
        print(f"Iteration {i+1}: {times[-1]:.4f} seconds")

    avg_time = sum(times) / iterations
    print(f"\nAverage execution time for get_database_stats: {avg_time:.4f} seconds")

    db.close()
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    run_benchmark()
