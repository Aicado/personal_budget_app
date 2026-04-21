import pytest
import polars as pl
from src.backend.database import TransactionDatabase

def test_db_initialization(mock_db):
    # Verify tables exist by attempting a select
    try:
        mock_db.conn.execute("SELECT * FROM transactions").fetchall()
        mock_db.conn.execute("SELECT * FROM accounts").fetchall()
        mock_db.conn.execute("SELECT * FROM categories").fetchall()
    except Exception as e:
        pytest.fail(f"Database tables not correctly initialized: {e}")

def test_insert_transactions(mock_db, sample_transaction_df):
    result = mock_db.insert_transactions(sample_transaction_df, "test.csv")
    assert result["status"] == "inserted"
    assert result["records_count"] == 4

    # Verify data in DB
    count = mock_db.conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    assert count == 4

def test_duplicate_prevention(mock_db, sample_transaction_df):
    mock_db.insert_transactions(sample_transaction_df, "test.csv")

    # Try inserting same data again
    result = mock_db.insert_transactions(sample_transaction_df, "test_again.csv")
    assert result["status"] == "duplicate"

    # Verify count hasn't increased
    count = mock_db.conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    assert count == 4

def test_register_account(mock_db):
    mock_db.register_account(
        account_name="Checking",
        account_type="Asset",
        account_path="Assets/Checking",
        current_debit=100.0,
        current_credit=0.0,
        net_value=100.0
    )

    status = mock_db.get_account_load_status()
    assert len(status) == 1
    assert status[0]["name"] == "Checking"
    assert status[0]["net_value"] == 100.0

def test_category_registration(mock_db):
    categories = [
        {"category": "Groceries", "category_group": "Food"},
        {"category": "Rent", "category_group": "Housing"}
    ]
    mock_db.register_categories(categories)

    # Verify categories exist
    rows = mock_db.conn.execute("SELECT category_name FROM categories ORDER BY category_name").fetchall()
    assert len(rows) == 2
    assert rows[0][0] == "Groceries"
    assert rows[1][0] == "Rent"
