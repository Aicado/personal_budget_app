"""Backfill script to populate DuckDB with existing YNAB CSV data."""

import os
from pathlib import Path
import pandas as pd
from typing import List, Dict, Any
from .transaction_analyzer import TransactionAnalyzer
from .database import TransactionDatabase


def find_transaction_files(directory: str) -> List[Path]:
    """Find all transaction CSV files in the directory recursively."""
    csv_files = []
    base_path = Path(directory)
    
    exclude_patterns = ["income-expense", "net-worth", "breakdown.csv"]
    
    for csv_file in base_path.rglob("*.csv"):
        filename = csv_file.name.lower()
        if filename == "current.csv":
            continue
        if any(pattern.lower() in filename for pattern in exclude_patterns):
            continue
        csv_files.append(csv_file)
    
    return sorted(csv_files)


def find_current_balance_files(directory: str) -> List[Path]:
    """Find all current.csv files in account subdirectories."""
    return sorted(Path(directory).rglob("current.csv"))


def get_account_metadata(csv_path: Path, base_dir: Path) -> Dict[str, str]:
    """Extract account metadata from a CSV file path."""
    relative = csv_path.relative_to(base_dir)
    parts = relative.parts
    metadata = {
        "account_name": None,
        "account_type": None,
        "account_path": None,
    }

    if len(parts) >= 3 and parts[0].lower() != "ynab_data":
        metadata["account_type"] = parts[0]
        metadata["account_name"] = parts[1]
        metadata["account_path"] = "/".join(parts[:-1])
    elif len(parts) >= 2 and parts[0].lower() != "ynab_data":
        metadata["account_type"] = parts[0]
        metadata["account_name"] = parts[1]
        metadata["account_path"] = "/".join(parts[:-1])

    return metadata


def backfill_database(accounts_dir: str = "data", transactions_dir: str = "ynab_data") -> Dict[str, Any]:
    """Backfill DuckDB with account definitions from accounts_dir and transactions from transactions_dir."""
    db = TransactionDatabase()
    db.clear_tables()
    
    # Load account definitions from accounts_dir
    accounts_path = Path(accounts_dir)
    balance_files = find_current_balance_files(accounts_dir)
    
    # Load transactions from transactions_dir
    transactions_path = Path(transactions_dir)
    transaction_files = find_transaction_files(transactions_dir)
    
    if not transaction_files and not balance_files:
        return {
            "status": "error",
            "message": "No CSV files found in accounts or transactions directories",
            "files_processed": 0,
            "accounts_loaded": 0
        }
    
    results = {
        "status": "success",
        "message": "Data load completed",
        "total_files_found": len(transaction_files),
        "files_processed": 0,
        "files_skipped": 0,
        "total_transactions_added": 0,
        "accounts_loaded": 0,
        "file_reports": []
    }

    # Load current account balances from account-specific current.csv files in accounts_dir
    account_map = {}  # account_name -> metadata
    for balance_file in balance_files:
        try:
            metadata = get_account_metadata(balance_file, accounts_path)
            if not metadata["account_name"] or not metadata["account_type"]:
                continue

            df = pd.read_csv(balance_file)
            if df.empty:
                continue

            latest = df.iloc[-1]
            debit = float(latest.get("debit", 0) or 0)
            credit = float(latest.get("credit", 0) or 0)
            net_value = debit - credit

            account_name = metadata["account_name"].replace('_', ' ').title()
            account_map[account_name] = metadata

            db.register_account(
                account_name=account_name,
                account_type=metadata["account_type"].replace('_', ' ').title(),
                account_path=metadata["account_path"],
                current_debit=debit,
                current_credit=credit,
                net_value=net_value,
            )
            results["accounts_loaded"] += 1
        except Exception as e:
            results["file_reports"].append({
                "filename": balance_file.name,
                "status": "account-error",
                "error": str(e),
                "path": str(balance_file)
            })

    # Process transaction files from transactions_dir
    for csv_file in transaction_files:
        try:
            analyzer = TransactionAnalyzer()
            df = analyzer.load_file(str(csv_file))
            analyzer.parse_transactions(df)

            # For each transaction, assign to account based on Account column
            if "account" not in analyzer.df.columns:
                results["file_reports"].append({
                    "filename": csv_file.name,
                    "status": "skipped",
                    "reason": "No 'account' column found",
                    "transactions_count": len(analyzer.df),
                    "path": str(csv_file)
                })
                continue

            # Filter transactions to only those with accounts in our account_map
            valid_accounts = set(account_map.keys())
            df_filtered = analyzer.df[analyzer.df["account"].isin(valid_accounts)].copy()
            
            if df_filtered.empty:
                results["file_reports"].append({
                    "filename": csv_file.name,
                    "status": "skipped",
                    "reason": "No transactions match defined accounts",
                    "transactions_count": len(analyzer.df),
                    "path": str(csv_file)
                })
                continue

            # Update analyzer.df to filtered version
            analyzer.df = df_filtered

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

            # For each account in the filtered data, insert with metadata
            accounts_in_file = df_filtered["account"].unique()
            for account_name in accounts_in_file:
                account_df = df_filtered[df_filtered["account"] == account_name].copy()
                metadata = account_map.get(account_name)
                if metadata:
                    db_result = db.insert_transactions(
                        account_df,
                        csv_file.name,
                        account_name=account_name,
                        account_type=metadata["account_type"],
                        account_path=metadata["account_path"]
                    )

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
            })
        except Exception as e:
            results["file_reports"].append({
                "filename": csv_file.name,
                "status": "error",
                "error": str(e),
                "path": str(csv_file)
            })

    results["database_summary"] = db.get_database_stats()
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
