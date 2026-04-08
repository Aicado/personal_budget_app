"""DuckDB database service for storing and managing transaction data."""

import duckdb
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
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
        
        # Create transactions table with ROWID as primary key (DuckDB native)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                file_hash VARCHAR,
                account VARCHAR,
                date DATE,
                payee VARCHAR,
                category VARCHAR,
                description VARCHAR,
                outflow DECIMAL(10, 2),
                inflow DECIMAL(10, 2),
                amount DECIMAL(10, 2),
                month_year VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_source VARCHAR
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

    def _compute_file_hash(self, df: pd.DataFrame) -> str:
        """Compute hash of dataframe for duplicate detection."""
        # Use first few rows and columns to create a fingerprint
        content = df.head(100).to_csv()
        return hashlib.md5(content.encode()).hexdigest()

    def file_exists(self, df: pd.DataFrame) -> bool:
        """Check if this file's data already exists in the database."""
        file_hash = self._compute_file_hash(df)
        
        result = self.conn.execute("""
            SELECT COUNT(*) as count FROM transactions WHERE file_hash = ?
        """, [file_hash]).fetchall()
        
        return result[0][0] > 0

    def insert_transactions(self, df: pd.DataFrame, filename: str) -> Dict[str, Any]:
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
        
        # Prepare data for insertion
        records = []
        for _, row in df.iterrows():
            records.append({
                "file_hash": file_hash,
                "account": row.get("account", "Unknown"),
                "date": row.get("date"),
                "payee": row.get("payee", ""),
                "category": row.get("category", "Uncategorized"),
                "description": row.get("description", ""),
                "outflow": float(row.get("outflow", 0)),
                "inflow": float(row.get("inflow", 0)),
                "amount": float(row.get("amount", 0)),
                "month_year": row.get("month_str", ""),
                "file_source": filename
            })
        
        # Insert records
        insert_df = pd.DataFrame(records)
        self.conn.register("temp_insert", insert_df)
        self.conn.execute("""
            INSERT INTO transactions 
            (file_hash, account, date, payee, category, description, outflow, inflow, amount, month_year, file_source)
            SELECT file_hash, account, date, payee, category, description, outflow, inflow, amount, month_year, file_source
            FROM temp_insert
        """)
        self.conn.unregister("temp_insert")
        
        return {
            "status": "inserted",
            "message": f"Successfully inserted {len(records)} transactions",
            "records_count": len(records),
            "file_hash": file_hash,
            "filename": filename
        }

    def get_transactions_by_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Retrieve transactions within a date range."""
        return self.conn.execute("""
            SELECT * FROM transactions 
            WHERE date >= ? AND date <= ?
            ORDER BY date DESC
        """, [start_date, end_date]).df()

    def get_transactions_by_category(self, category: str) -> pd.DataFrame:
        """Retrieve transactions for a specific category."""
        return self.conn.execute("""
            SELECT * FROM transactions 
            WHERE category = ?
            ORDER BY date DESC
        """, [category]).df()

    def get_all_transactions(self) -> pd.DataFrame:
        """Retrieve all transactions from database."""
        return self.conn.execute("""
            SELECT * FROM transactions ORDER BY date DESC
        """).df()

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
            }
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
