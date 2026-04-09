"""DuckDB database service for storing and managing transaction data."""

import duckdb
import io
import polars as pl
from pathlib import Path
from typing import Dict, List, Any
import hashlib


class TransactionDatabase:
    """Manages DuckDB database for transaction storage and retrieval."""

    def __init__(self, db_path: str = "db/ynab_analyzer.duckdb"):
        """Initialize DuckDB connection."""
        # Ensure db directory exists
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        """Initialize database and create tables if they don't exist."""
        self.conn = duckdb.connect(self.db_path)
        
        # Create transactions table with basic metadata and account/category references
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                file_hash VARCHAR,
                account VARCHAR,
                account_type VARCHAR,
                account_path VARCHAR,
                date DATE,
                payee VARCHAR,
                category VARCHAR,
                category_group VARCHAR,
                description VARCHAR,
                outflow DOUBLE,
                inflow DOUBLE,
                amount DOUBLE,
                transaction_type VARCHAR,
                month_year VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_source VARCHAR
            )
        """)

        # Create accounts table for current balances and account metadata
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id INTEGER,
                account_name VARCHAR,
                account_type VARCHAR,
                account_path VARCHAR UNIQUE,
                current_debit DOUBLE DEFAULT 0.0,
                current_credit DOUBLE DEFAULT 0.0,
                net_value DOUBLE DEFAULT 0.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create categories table for transaction categories
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER,
                category_name VARCHAR UNIQUE,
                category_group VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index on file_hash for duplicate detection
        try:
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_hash ON transactions(file_hash)
            """)
        except:
            pass  # Index already exists
        
        # Create index on date for range queries
        try:
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_date ON transactions(date)
            """)
        except:
            pass  # Index already exists

    def clear_tables(self):
        """Clear all data from tables."""
        self.conn.execute("DELETE FROM transactions")
        self.conn.execute("DELETE FROM accounts")
        self.conn.execute("DELETE FROM categories")

    def _compute_file_hash(self, df: pl.DataFrame) -> str:
        """Compute hash of dataframe for duplicate detection."""
        buffer = io.StringIO()
        df.head(100).write_csv(buffer)
        return hashlib.md5(buffer.getvalue().encode("utf-8")).hexdigest()

    def register_categories(self, categories: List[Dict[str, Any]]) -> None:
        """Register unique categories in the categories table."""
        if not categories:
            return

        category_df = pl.DataFrame(categories)
        if category_df.is_empty():
            return

        category_df = category_df.unique(subset=["category_name"])
        self.conn.register("new_categories", category_df.to_arrow())
        self.conn.execute("""
            INSERT INTO categories (category_name, category_group)
            SELECT DISTINCT category_name, category_group
            FROM new_categories
            WHERE category_name NOT IN (SELECT category_name FROM categories)
        """)
        self.conn.unregister("new_categories")

    def register_account(self, account_name: str, account_type: str, account_path: str, current_debit: float = 0.0, current_credit: float = 0.0, net_value: float = 0.0) -> None:
        """Upsert an account record with current balance metadata."""
        self.conn.execute("""
            MERGE INTO accounts AS target
            USING (SELECT ? AS account_name, ? AS account_type, ? AS account_path, ? AS current_debit, ? AS current_credit, ? AS net_value) AS source
            ON target.account_path = source.account_path
            WHEN MATCHED THEN UPDATE SET
                account_name = source.account_name,
                account_type = source.account_type,
                current_debit = source.current_debit,
                current_credit = source.current_credit,
                net_value = source.net_value,
                updated_at = CURRENT_TIMESTAMP
            WHEN NOT MATCHED THEN INSERT (account_name, account_type, account_path, current_debit, current_credit, net_value)
            VALUES (source.account_name, source.account_type, source.account_path, source.current_debit, source.current_credit, source.net_value)
        """, [account_name, account_type, account_path, current_debit, current_credit, net_value])

    def get_account_summaries(self) -> List[Dict[str, Any]]:
        """Get a transaction-based summary for each account."""
        rows = self.conn.execute("""
            SELECT 
                COALESCE(account, 'Unknown') as account_name,
                COALESCE(account_type, 'Unknown') as account_type,
                COALESCE(account_path, '') as account_path,
                COUNT(*) as transaction_count,
                MIN(date) as start_date,
                MAX(date) as end_date,
                SUM(inflow) as total_inflow,
                SUM(outflow) as total_outflow,
                SUM(amount) as net_total
            FROM transactions
            GROUP BY account_name, account_type, account_path
            ORDER BY total_inflow DESC
        """).fetchall()

        return [
            {
                "name": row[0],
                "type": row[1],
                "path": row[2],
                "transaction_count": int(row[3]),
                "date_range": {"start": str(row[4]), "end": str(row[5])},
                "totals": {
                    "inflow": float(row[6] or 0.0),
                    "outflow": float(row[7] or 0.0),
                    "net": float(row[8] or 0.0)
                }
            }
            for row in rows
        ]

    def get_category_summary(self) -> Dict[str, float]:
        """Get total amount by category."""
        rows = self.conn.execute("""
            SELECT category, SUM(amount) as total
            FROM transactions
            GROUP BY category
            ORDER BY total DESC
        """).fetchall()

        return {row[0]: float(row[1] or 0.0) for row in rows}

    def get_monthly_trends(self) -> Dict[str, Any]:
        """Get monthly inflow/outflow/net trends."""
        rows = self.conn.execute("""
            SELECT month_year, SUM(amount) as net_amount, SUM(inflow) as inflow, SUM(outflow) as outflow
            FROM transactions
            GROUP BY month_year
            ORDER BY month_year
        """).fetchall()

        months = [row[0] for row in rows]
        return {
            "months": months,
            "net_amounts": [float(row[1] or 0.0) for row in rows],
            "outflows": [float(row[3] or 0.0) for row in rows],
            "inflows": [float(row[2] or 0.0) for row in rows],
        }

    def get_account_balances(self) -> List[Dict[str, Any]]:
        """Get current account balances stored in the accounts table."""
        rows = self.conn.execute("""
            SELECT account_name, account_type, account_path, current_debit, current_credit, net_value
            FROM accounts
            ORDER BY account_type, account_name
        """).fetchall()

        if rows:
            return [
                {
                    "name": row[0],
                    "type": row[1],
                    "path": row[2],
                    "debit": float(row[3] or 0.0),
                    "credit": float(row[4] or 0.0),
                    "net_value": float(row[5] or 0.0)
                }
                for row in rows
            ]

        # Fallback to account totals from transactions if no account records exist
        rows = self.conn.execute("""
            SELECT account, SUM(inflow) as inflow, SUM(outflow) as outflow, SUM(amount) as net_value
            FROM transactions
            GROUP BY account
            ORDER BY account
        """).fetchall()

        return [
            {
                "name": row[0] or 'Unknown',
                "type": 'Unknown',
                "path": '',
                "debit": float(row[1] or 0.0),
                "credit": float(row[2] or 0.0),
                "net_value": float(row[3] or 0.0)
            }
            for row in rows
        ]

    def get_account_load_status(self) -> List[Dict[str, Any]]:
        """Get load status for each account, including latest transaction date and current balance availability."""
        account_rows = self.conn.execute("""
            SELECT account_name, account_type, account_path, current_debit, current_credit, net_value, updated_at
            FROM accounts
        """).fetchall()

        account_info = {}
        for row in account_rows:
            key = (row[0] or '', row[1] or '', row[2] or '')
            account_info[key] = {
                "name": row[0],
                "type": row[1],
                "path": row[2],
                "current_debit": float(row[3] or 0.0),
                "current_credit": float(row[4] or 0.0),
                "net_value": float(row[5] or 0.0),
                "current_balance_updated_at": str(row[6]) if row[6] else None,
                "current_balance_present": True,
                "transaction_count": 0,
                "first_transaction_date": None,
                "last_transaction_date": None
            }

        transaction_rows = self.conn.execute("""
            SELECT account, account_type, account_path, COUNT(*) as transaction_count, MIN(date) as first_transaction_date, MAX(date) as last_transaction_date
            FROM transactions
            GROUP BY account, account_type, account_path
        """).fetchall()

        results = []
        seen_keys = set()

        for row in transaction_rows:
            key = (row[0] or '', row[1] or '', row[2] or '')
            seen_keys.add(key)
            account = account_info.get(key, {
                "name": row[0] or 'Unknown',
                "type": row[1] or 'Unknown',
                "path": row[2] or '',
                "current_debit": 0.0,
                "current_credit": 0.0,
                "net_value": 0.0,
                "current_balance_updated_at": None,
                "current_balance_present": False
            })

            merged = {
                "name": account["name"],
                "type": account["type"],
                "path": account["path"],
                "transaction_count": int(row[3] or 0),
                "first_transaction_date": str(row[4]) if row[4] else None,
                "last_transaction_date": str(row[5]) if row[5] else None,
                "current_balance_present": account["current_balance_present"],
                "current_balance_updated_at": account["current_balance_updated_at"],
                "current_debit": account["current_debit"],
                "current_credit": account["current_credit"],
                "net_value": account["net_value"],
                "needs_current_balance": not account["current_balance_present"],
                "needs_transactions": int(row[3] or 0) == 0
            }
            results.append(merged)

        for key, account in account_info.items():
            if key in seen_keys:
                continue
            results.append({
                "name": account["name"],
                "type": account["type"],
                "path": account["path"],
                "transaction_count": 0,
                "first_transaction_date": None,
                "last_transaction_date": None,
                "current_balance_present": True,
                "current_balance_updated_at": account["current_balance_updated_at"],
                "current_debit": account["current_debit"],
                "current_credit": account["current_credit"],
                "net_value": account["net_value"],
                "needs_current_balance": False,
                "needs_transactions": True
            })

        return sorted(results, key=lambda a: (a["name"].lower(), a["type"].lower(), a["path"]))

    def file_exists(self, df: pl.DataFrame) -> bool:
        """Check if this file's data already exists in the database."""
        file_hash = self._compute_file_hash(df)

        result = self.conn.execute("""
            SELECT COUNT(*) as count FROM transactions WHERE file_hash = ?
        """, [file_hash]).fetchall()

        return result[0][0] > 0

    def insert_transactions(self, df: pl.DataFrame, filename: str, account_name: str = None, account_type: str = None, account_path: str = None) -> Dict[str, Any]:
        """Insert transactions into database and return summary."""
        file_hash = self._compute_file_hash(df)
        
        # Check if file already exists
        if self.file_exists(df):
            existing = self.conn.execute("""
                SELECT COUNT(*) as count, MIN(date) as start_date, MAX(date) as end_date
                FROM transactions WHERE file_hash = ?
            """, [file_hash]).fetchall()
            
            return {
                "status": "duplicate",
                "message": f"File data already exists in database",
                "existing_records": existing[0][0],
                "date_range": {
                    "start": str(existing[0][1]),
                    "end": str(existing[0][2])
                }
            }

        df = df.clone()

        # Attach account metadata to transactions when available
        if account_name and ("account" not in df.columns or df["account"].null_count() == df.height):
            df = df.with_columns(pl.lit(account_name).alias("account"))
        if account_type and ("account_type" not in df.columns or df["account_type"].null_count() == df.height):
            df = df.with_columns(pl.lit(account_type).alias("account_type"))
        if account_path and ("account_path" not in df.columns or df["account_path"].null_count() == df.height):
            df = df.with_columns(pl.lit(account_path).alias("account_path"))

        if "category" not in df.columns:
            df = df.with_columns(pl.lit("Uncategorized").alias("category"))
        if "category_group" not in df.columns:
            df = df.with_columns(
                pl.col("category").cast(pl.Utf8).str.split("/").arr.get(0).str.strip().alias("category_group")
            )
        if "transaction_type" not in df.columns:
            df = df.with_columns(
                pl.when(pl.col("inflow") > pl.col("outflow"))
                .then("income")
                .when(pl.col("outflow") > pl.col("inflow"))
                .then("expense")
                .otherwise("transfer")
                .alias("transaction_type")
            )

        categories = df.select(["category", "category_group"]).unique().to_dicts()
        self.register_categories(categories)

        # Prepare data for insertion
        records = []
        for _, row in df.iterrows():
            records.append({
                "file_hash": file_hash,
                "account": row.get("account", "Unknown"),
                "account_type": row.get("account_type", "Unknown"),
                "account_path": row.get("account_path", ""),
                "date": row.get("date"),
                "payee": row.get("payee", ""),
                "category": row.get("category", "Uncategorized"),
                "category_group": row.get("category_group", "Uncategorized"),
                "description": row.get("description", ""),
                "outflow": float(row.get("outflow", 0)),
                "inflow": float(row.get("inflow", 0)),
                "amount": float(row.get("amount", 0)),
                "transaction_type": row.get("transaction_type", "transfer"),
                "month_year": row.get("month_str", ""),
                "file_source": filename
            })
        
        insert_df = pl.DataFrame(records)
        self.conn.register("temp_insert", insert_df.to_arrow())
        self.conn.execute("""
            INSERT INTO transactions 
            (file_hash, account, account_type, account_path, date, payee, category, category_group, description, outflow, inflow, amount, transaction_type, month_year, file_source)
            SELECT file_hash, account, account_type, account_path, date, payee, category, category_group, description, outflow, inflow, amount, transaction_type, month_year, file_source
            FROM temp_insert
        """
        )
        self.conn.unregister("temp_insert")
        
        return {
            "status": "inserted",
            "message": f"Successfully inserted {len(records)} transactions",
            "records_count": len(records),
            "file_hash": file_hash,
            "filename": filename
        }

    def get_transactions_by_date_range(self, start_date: str, end_date: str) -> pl.DataFrame:
        """Retrieve transactions within a date range."""
        return pl.from_arrow(
            self.conn.execute("""
                SELECT * FROM transactions 
                WHERE date >= ? AND date <= ?
                ORDER BY date DESC
            """, [start_date, end_date]).fetch_arrow_table()
        )

    def get_transactions_by_category(self, category: str) -> pl.DataFrame:
        """Retrieve transactions for a specific category."""
        return pl.from_arrow(
            self.conn.execute("""
                SELECT * FROM transactions 
                WHERE category = ?
                ORDER BY date DESC
            """, [category]).fetch_arrow_table()
        )

    def get_all_transactions(self) -> pl.DataFrame:
        """Retrieve all transactions from database."""
        return pl.from_arrow(
            self.conn.execute("""
                SELECT * FROM transactions ORDER BY date DESC
            """).fetch_arrow_table()
        )

    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the database."""
        stats = self.conn.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                COUNT(DISTINCT file_source) as unique_files,
                COUNT(DISTINCT category) as unique_categories,
                MIN(date) as earliest_date,
                MAX(date) as latest_date,
                SUM(inflow) as total_inflow,
                SUM(outflow) as total_outflow
            FROM transactions
        """).fetchall()[0]

        category_summary = self.get_category_summary()
        monthly_trends = self.get_monthly_trends()
        
        return {
            "total_transactions": stats[0],
            "unique_files": stats[1],
            "unique_categories": stats[2],
            "date_range": {
                "start": str(stats[3]) if stats[3] else None,
                "end": str(stats[4]) if stats[4] else None
            },
            "totals": {
                "inflow": float(stats[5]) if stats[5] else 0.0,
                "outflow": float(stats[6]) if stats[6] else 0.0
            },
            "category_summary": category_summary,
            "monthly_trends": monthly_trends
        }

    def get_files_info(self) -> List[Dict[str, Any]]:
        """Get information about all uploaded files."""
        files = self.conn.execute("""
            SELECT DISTINCT 
                file_source,
                file_hash,
                MIN(date) as start_date,
                MAX(date) as end_date,
                COUNT(*) as transaction_count,
                MIN(created_at) as uploaded_at
            FROM transactions
            GROUP BY file_source, file_hash
            ORDER BY uploaded_at DESC
        """).fetchall()
        
        return [
            {
                "filename": f[0],
                "file_hash": f[1],
                "date_range": {"start": str(f[2]), "end": str(f[3])},
                "transaction_count": f[4],
                "uploaded_at": str(f[5])
            }
            for f in files
        ]

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Cleanup on object deletion."""
        self.close()
