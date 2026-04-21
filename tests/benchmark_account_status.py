import time
import os
import duckdb
import polars as pl
from pathlib import Path
import sys

# Add src to path so we can import the database module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.backend.database import TransactionDatabase

def setup_benchmark_db(db_path, num_accounts=1000, num_transactions=100000):
    if os.path.exists(db_path):
        os.remove(db_path)

    db = TransactionDatabase(db_path)

    # Create mock accounts
    # Half have balances, half don't (actually we want to test the join)
    # We'll put all 1000 in accounts table
    accounts_data = []
    for i in range(num_accounts):
        accounts_data.append({
            "account_id": i,
            "account_name": f"Account {i}",
            "account_type": "Checking" if i % 2 == 0 else "Credit Card",
            "account_path": f"path/to/account_{i}",
            "current_debit": 1000.0,
            "current_credit": 0.0,
            "net_value": 1000.0
        })

    # Bulk insert accounts
    acc_df = pl.DataFrame(accounts_data)
    db.conn.register("temp_acc", acc_df.to_arrow())
    db.conn.execute("INSERT INTO accounts (account_id, account_name, account_type, account_path, current_debit, current_credit, net_value) SELECT account_id, account_name, account_type, account_path, current_debit, current_credit, net_value FROM temp_acc")
    db.conn.unregister("temp_acc")

    # Create mock transactions for half of the accounts (0-499)
    # And some transactions for accounts NOT in the accounts table (1000-1099)
    transactions_data = []

    # Transactions for existing accounts
    for i in range(num_transactions // 2):
        acc_idx = i % (num_accounts // 2)
        transactions_data.append({
            "file_hash": f"hash_{acc_idx}",
            "account": f"Account {acc_idx}",
            "account_type": "Checking" if acc_idx % 2 == 0 else "Credit Card",
            "account_path": f"path/to/account_{acc_idx}",
            "date": "2023-01-01",
            "payee": "Payee",
            "category": "Category",
            "category_group": "Group",
            "description": "Desc",
            "outflow": 10.0,
            "inflow": 0.0,
            "amount": -10.0,
            "transaction_type": "expense",
            "month_year": "2023-01",
            "file_source": "file.csv"
        })

    # Transactions for non-existing accounts
    for i in range(num_transactions // 2):
        acc_idx = 1000 + (i % 100)
        transactions_data.append({
            "file_hash": f"hash_{acc_idx}",
            "account": f"Account {acc_idx}",
            "account_type": "Checking" if acc_idx % 2 == 0 else "Credit Card",
            "account_path": f"path/to/account_{acc_idx}",
            "date": "2023-01-01",
            "payee": "Payee",
            "category": "Category",
            "category_group": "Group",
            "description": "Desc",
            "outflow": 10.0,
            "inflow": 0.0,
            "amount": -10.0,
            "transaction_type": "expense",
            "month_year": "2023-01",
            "file_source": "file.csv"
        })

    # Insert transactions
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
    db_path = "tests/benchmark.duckdb"
    db = setup_benchmark_db(db_path)

    # Warm up
    db.get_account_load_status()

    print("Starting benchmark...")
    start_time = time.perf_counter()
    results = db.get_account_load_status()
    end_time = time.perf_counter()

    execution_time = end_time - start_time
    print(f"Execution time for get_account_load_status: {execution_time:.4f} seconds")
    print(f"Number of accounts returned: {len(results)}")

    db.close()
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    run_benchmark()
