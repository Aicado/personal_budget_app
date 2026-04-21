import pytest
import polars as pl
from src.backend.transaction_analyzer import TransactionAnalyzer

def test_load_csv(sample_transaction_csv):
    analyzer = TransactionAnalyzer()
    df = analyzer.load_csv(sample_transaction_csv)
    assert isinstance(df, pl.DataFrame)
    assert df.height == 4

def test_parse_transactions(sample_transaction_df):
    df = sample_transaction_df
    assert "date" in df.columns
    assert "amount" in df.columns
    assert "category" in df.columns
    assert "category_group" in df.columns

    # Check amount calculation: inflow - outflow
    # Starbucks: 0.0 - 5.5 = -5.5
    assert df.filter(pl.col("payee") == "Starbucks")["amount"][0] == -5.5
    # Employer: 5000.0 - 0.0 = 5000.0
    assert df.filter(pl.col("payee") == "Employer")["amount"][0] == 5000.0

def test_category_parsing():
    csv_content = "Date,Payee,Category,Outflow,Inflow\n01/01/2024,Shop,Food | Groceries,10.0,0.0"
    analyzer = TransactionAnalyzer()
    df = analyzer.load_csv(csv_content)
    df = analyzer.parse_transactions(df)

    assert df["category"][0] == "Groceries"
    assert df["category_group"][0] == "Food"

def test_uncategorized_fallback():
    csv_content = "Date,Payee,Outflow,Inflow\n01/01/2024,Mystery,10.0,0.0"
    analyzer = TransactionAnalyzer()
    df = analyzer.load_csv(csv_content)
    df = analyzer.parse_transactions(df)

    assert df["category"][0] == "Uncategorized"
    assert df["category_group"][0] == "Uncategorized"

def test_monthly_trends(sample_transaction_df):
    analyzer = TransactionAnalyzer()
    analyzer.df = sample_transaction_df
    trends = analyzer.get_monthly_trends()

    assert "months" in trends
    assert "2024-01" in trends["months"]
    assert len(trends["net_amounts"]) == 1

def test_summary_stats(sample_transaction_df):
    analyzer = TransactionAnalyzer()
    analyzer.df = sample_transaction_df
    stats = analyzer.get_summary_stats()

    assert stats["total_inflow"] == 5100.0
    assert stats["total_outflow"] == 1605.5
    assert stats["transaction_count"] == 4
