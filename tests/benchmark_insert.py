import time
import os
import duckdb
import polars as pl
from pathlib import Path
import sys
from datetime import date
from typing import List, Dict, Any, Optional

# Add src to path so we can import the database module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.database import TransactionDatabase

class MockCategorizer:
    async def categorize_transaction(self, payee, amount, date, categories):
        return {
            "category": "Mock",
            "category_group": "MockGroup",
            "confidence": 1.0
        }

def setup_benchmark_db(db_path, num_mappings=1000):
    if os.path.exists(db_path):
        os.remove(db_path)

    db = TransactionDatabase(db_path)

    # Register an account
    db.register_account(
        account_name="Checking",
        account_type="Asset",
        account_path="Assets/Checking",
        current_debit=1000.0,
        current_credit=0.0,
        net_value=1000.0
    )

    # Create mock payee mappings
    # We use a lot of unique payees to test mapping lookup overhead
    print(f"Pre-populating {num_mappings} payee mappings...")
    mappings = []
    for i in range(num_mappings):
        mappings.append((f"Payee {i}", f"Category {i % 10}", f"Group {i % 5}", 0.9))

    db.conn.executemany("""
        INSERT INTO payee_mappings (payee, category, category_group, confidence)
        VALUES (?, ?, ?, ?)
    """, mappings)

    return db

def generate_mock_transactions(num_rows=10000):
    rows = []
    for i in range(num_rows):
        rows.append({
            "date": date(2023, 1, 1),
            "payee": f"Payee {i % 1000}", # Will match our 1000 mappings
            "description": f"Transaction {i}",
            "outflow": 10.0,
            "inflow": 0.0,
            "amount": -10.0,
            "account": "Checking"
        })
    return pl.DataFrame(rows)

def run_benchmark():
    db_path = "tests/benchmark_insert.duckdb"
    db = setup_benchmark_db(db_path)

    df = generate_mock_transactions(10000)
    categorizer = MockCategorizer()

    print(f"Starting benchmark for insert_transactions with {len(df)} rows and N+1 mapping lookups...")

    start_time = time.perf_counter()
    result = db.insert_transactions(df, "benchmark.csv", account_name="Checking", account_type="Asset", account_path="Assets/Checking", categorizer=categorizer)
    end_time = time.perf_counter()

    execution_time = end_time - start_time
    print(f"Execution time for insert_transactions: {execution_time:.4f} seconds")
    print(f"TPS: {len(df) / execution_time:.2f} rows/sec")
    print(f"Result: {result['status']}, message: {result['message']}")

    # Verify some data was inserted
    count = db.conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    print(f"Transactions in DB: {count}")

    # Verify categorization happened
    uncategorized_count = db.conn.execute("SELECT COUNT(*) FROM transactions WHERE category = 'Uncategorized'").fetchone()[0]
    print(f"Uncategorized transactions in DB: {uncategorized_count}")

    # Check a few categorized ones
    sample = db.conn.execute("SELECT payee, category FROM transactions LIMIT 5").fetchall()
    print(f"Samples: {sample}")

    db.close()
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    run_benchmark()
