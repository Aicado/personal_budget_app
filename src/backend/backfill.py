"""Backfill script to populate DuckDB with existing YNAB CSV data."""

import os
from pathlib import Path
import pandas as pd
from typing import List, Dict, Any
from .transaction_analyzer import TransactionAnalyzer
from .database import TransactionDatabase


def find_csv_files(directory: str) -> List[Path]:
    """Find all CSV files in directory recursively, excluding summary files."""
    csv_files = []
    base_path = Path(directory)
    
    # Pattern to exclude summary files
    exclude_patterns = ["income-expense", "net-worth", "breakdown.csv"]
    
    for csv_file in base_path.rglob("*.csv"):
        # Check if file should be excluded
        filename = csv_file.name.lower()
        if any(pattern.lower() in filename for pattern in exclude_patterns):
            continue
        csv_files.append(csv_file)
    
    return sorted(csv_files)


def backfill_database(data_dir: str = "data") -> Dict[str, Any]:
    """Backfill DuckDB with all YNAB CSV files.
    
    Args:
        data_dir: Directory containing YNAB CSV files
        
    Returns:
        Dictionary with backfill report
    """
    # Initialize database
    db = TransactionDatabase()
    
    # Find all CSV files
    csv_files = find_csv_files(data_dir)
    
    if not csv_files:
        return {
            "status": "error",
            "message": "No CSV files found in data directory",
            "files_processed": 0
        }
    
    # Track results
    results = {
        "status": "success",
        "message": f"Backfill completed",
        "total_files_found": len(csv_files),
        "files_processed": 0,
        "files_skipped": 0,
        "total_transactions_added": 0,
        "file_reports": []
    }
    
    # Try to load current account balances if available
    current_csv = Path(data_dir) / "current.csv"
    current_balances = {}
    if current_csv.exists():
        try:
            balance_df = pd.read_csv(current_csv)
            for _, row in balance_df.iterrows():
                account_name = row.get('account') or row.get('Account')
                balance = row.get('balance') or row.get('Balance') or row.get('current_balance') or row.get('Current Balance')
                if account_name and balance:
                    current_balances[str(account_name).strip()] = float(balance)
        except Exception as e:
            print(f"Warning: Could not load current balances: {e}")
    
    # Process each CSV file
    for csv_file in csv_files:
        try:
            # Read and parse CSV
            analyzer = TransactionAnalyzer()
            df = analyzer.load_file(str(csv_file))
            analyzer.parse_transactions(df)
            
            # Check if file already exists
            if db.file_exists(analyzer.df):
                results["files_skipped"] += 1
                results["file_reports"].append({
                    "filename": csv_file.name,
                    "status": "skipped",
                    "reason": "Data already exists in database",
                    "transactions_count": len(analyzer.df),
                    "path": str(csv_file)
                })
                continue
            
            # Insert into database
            db_result = db.insert_transactions(analyzer.df, csv_file.name)
            
            results["files_processed"] += 1
            results["total_transactions_added"] += len(analyzer.df)
            results["file_reports"].append({
                "filename": csv_file.name,
                "status": "inserted",
                "transactions_count": len(analyzer.df),
                "date_range": {
                    "start": str(analyzer.df["date"].min().date()),
                    "end": str(analyzer.df["date"].max().date())
                },
                "unique_categories": analyzer.df["category"].nunique(),
                "path": str(csv_file),
                "db_result": db_result
            })
            
        except Exception as e:
            results["file_reports"].append({
                "filename": csv_file.name,
                "status": "error",
                "error": str(e),
                "path": str(csv_file)
            })
    
    # Get final database stats
    db_stats = db.get_database_stats()
    results["database_summary"] = db_stats
    
    db.close()
    return results


if __name__ == "__main__":
    import json
    
    # Run backfill
    result = backfill_database()
    
    # Print report
    print("\n" + "="*80)
    print("BACKFILL REPORT")
    print("="*80)
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Total files found: {result['total_files_found']}")
    print(f"Files processed: {result['files_processed']}")
    print(f"Files skipped: {result['files_skipped']}")
    print(f"Total transactions added: {result['total_transactions_added']}")
    
    print("\n" + "-"*80)
    print("FILE-BY-FILE DETAILS")
    print("-"*80)
    
    for report in result["file_reports"]:
        print(f"\n📄 {report['filename']}")
        print(f"   Status: {report['status']}")
        if report['status'] == 'error':
            print(f"   Error: {report['error']}")
        else:
            print(f"   Transactions: {report.get('transactions_count', 'N/A')}")
            if 'date_range' in report:
                print(f"   Date Range: {report['date_range']['start']} to {report['date_range']['end']}")
                print(f"   Categories: {report.get('unique_categories', 'N/A')}")
    
    print("\n" + "-"*80)
    print("DATABASE SUMMARY")
    print("-"*80)
    db_summary = result.get("database_summary", {})
    print(f"Total transactions in database: {db_summary.get('total_transactions', 0)}")
    print(f"Unique files in database: {db_summary.get('unique_files', 0)}")
    print(f"Unique categories: {db_summary.get('unique_categories', 0)}")
    date_range = db_summary.get('date_range', {})
    if date_range.get('start'):
        print(f"Date range: {date_range['start']} to {date_range['end']}")
    
    print("\n" + "="*80 + "\n")
