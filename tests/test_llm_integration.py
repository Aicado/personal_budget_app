import pytest
import polars as pl
from src.backend.database import TransactionDatabase
from unittest.mock import AsyncMock

@pytest.fixture
def mock_categorizer():
    categorizer = AsyncMock()
    categorizer.categorize_transaction.return_value = {
        "category": "Groceries",
        "category_group": "Food",
        "confidence": 0.9
    }
    return categorizer

def test_insert_with_llm_categorization(mock_db, mock_categorizer):
    # Data with "Uncategorized"
    df = pl.DataFrame({
        "date": ["2024-01-01"],
        "payee": ["Costco"],
        "category": ["Uncategorized"],
        "category_group": ["Uncategorized"],
        "outflow": [100.0],
        "inflow": [0.0],
        "amount": [-100.0],
        "transaction_type": ["expense"],
        "month_str": ["2024-01"]
    })

    # Mock get_all_categories
    mock_db.register_categories([{"category": "Groceries", "category_group": "Food"}])

    result = mock_db.insert_transactions(df, "test.csv", categorizer=mock_categorizer)

    assert result["status"] == "inserted"

    # Check if LLM was called
    mock_categorizer.categorize_transaction.assert_called_once()

    # Check if transaction in DB has the LLM-suggested category
    row = mock_db.conn.execute("SELECT category, category_group FROM transactions WHERE payee = 'Costco'").fetchone()
    assert row[0] == "Groceries"
    assert row[1] == "Food"

    # Check if mapping was saved
    mapping = mock_db.get_payee_mapping("Costco")
    assert mapping is not None
    assert mapping["category"] == "Groceries"

def test_mapping_table_takes_precedence(mock_db, mock_categorizer):
    # Save a mapping manually
    mock_db.save_payee_mapping("Costco", "Shopping", "Personal", 1.0)

    df = pl.DataFrame({
        "date": ["2024-01-01"],
        "payee": ["Costco"],
        "category": ["Uncategorized"],
        "category_group": ["Uncategorized"],
        "outflow": [100.0],
        "inflow": [0.0],
        "amount": [-100.0],
        "transaction_type": ["expense"],
        "month_str": ["2024-01"]
    })

    mock_db.insert_transactions(df, "test.csv", categorizer=mock_categorizer)

    # LLM should NOT be called because mapping exists
    mock_categorizer.categorize_transaction.assert_not_called()

    row = mock_db.conn.execute("SELECT category FROM transactions WHERE payee = 'Costco'").fetchone()
    assert row[0] == "Shopping"
