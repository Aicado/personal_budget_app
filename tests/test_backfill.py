import pytest
import os
from pathlib import Path
import polars as pl
from src.backend.backfill import find_transaction_files, find_current_balance_files, get_account_metadata, backfill_database

def test_find_files(temp_data_dir):
    trans_files = find_transaction_files(str(temp_data_dir / "transaction_data"))
    # No files yet in transaction_data in temp_data_dir
    assert len(trans_files) == 0

    # Add a file
    (temp_data_dir / "transaction_data" / "2024.csv").write_text("Date,Account,Amount\n2024-01-01,Checking,10.0")
    trans_files = find_transaction_files(str(temp_data_dir / "transaction_data"))
    assert len(trans_files) == 1

def test_find_current_balance_files(temp_data_dir):
    balance_files = find_current_balance_files(str(temp_data_dir))
    assert len(balance_files) == 1
    assert balance_files[0].name == "current.csv"

def test_get_account_metadata(temp_data_dir):
    csv_path = temp_data_dir / "Assets" / "Checking" / "current.csv"
    metadata = get_account_metadata(csv_path, temp_data_dir)
    assert metadata["account_name"] == "Checking"
    assert metadata["account_type"] == "Assets"
