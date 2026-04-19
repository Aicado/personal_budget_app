import pytest
import polars as pl
import os
import tempfile
from pathlib import Path
from src.backend.database import TransactionDatabase
from src.backend.transaction_analyzer import TransactionAnalyzer

@pytest.fixture
def mock_db():
    """Provides a TransactionDatabase instance using an in-memory DuckDB."""
    # Using :memory: for DuckDB
    db = TransactionDatabase(db_path=":memory:")
    yield db
    db.close()

@pytest.fixture
def sample_transaction_csv():
    """Provides sample transaction CSV content."""
    return """Date,Payee,Category,Outflow,Inflow
2024-01-01,Starbucks,Food & Drink | Coffee,5.50,0.00
2024-01-02,Landlord,Housing | Rent,1500.00,0.00
2024-01-03,Employer,Income | Salary,0.00,5000.00
2024-01-04,Transfer,Transfer | Savings,100.00,100.00
"""

@pytest.fixture
def sample_transaction_df(sample_transaction_csv):
    """Provides a parsed Polars DataFrame from sample CSV."""
    analyzer = TransactionAnalyzer()
    df = analyzer.load_csv(sample_transaction_csv)
    return analyzer.parse_transactions(df)

@pytest.fixture
def temp_data_dir():
    """Sets up a temporary directory structure mimicking the app's data layout."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)

        # Create Assets/Checking structure
        checking_dir = base_path / "Assets" / "Checking"
        checking_dir.mkdir(parents=True)

        # Create current.csv
        current_csv = checking_dir / "current.csv"
        current_csv.write_text("date,debit,credit\n2024-01-01,1000.0,0.0")

        # Create transaction_data directory
        trans_dir = base_path / "transaction_data"
        trans_dir.mkdir()

        yield base_path
