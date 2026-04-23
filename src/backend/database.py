import asyncio
"""DuckDB database service for storing and managing transaction data."""

import duckdb
import io
import polars as pl
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib


class TransactionDatabase:
    """Manages DuckDB database for transaction storage and retrieval."""

    def __init__(self, db_path: str = "db/personal_budget_app.duckdb"):
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
        # Create payee_mappings table for LLM-based categorization
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS payee_mappings (
                payee VARCHAR,
                category VARCHAR,
                category_group VARCHAR,
                confidence DOUBLE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (payee, category)
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
        self.conn.execute("DELETE FROM payee_mappings")

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

        category_df = category_df.unique(subset=["category"])
        self.conn.register("new_categories", category_df.to_arrow())
        self.conn.execute("""
            INSERT INTO categories (category_name, category_group)
            SELECT DISTINCT category as category_name, category_group
            FROM new_categories
            WHERE category_name NOT IN (SELECT category_name FROM categories)
        """)
        self.conn.unregister("new_categories")

    def register_account(self, account_name: str, account_type: str, account_path: str, current_debit: float = 0.0, current_credit: float = 0.0, net_value: float = 0.0) -> None:
        """Register or update an account with its current balance."""
        self.conn.execute("""
            INSERT INTO accounts (account_name, account_type, account_path, current_debit, current_credit, net_value, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT (account_path) DO UPDATE SET
                account_name = EXCLUDED.account_name,
                account_type = EXCLUDED.account_type,
                current_debit = EXCLUDED.current_debit,
                current_credit = EXCLUDED.current_credit,
                net_value = EXCLUDED.net_value,
                updated_at = EXCLUDED.updated_at
        """, [account_name, account_type, account_path, current_debit, current_credit, net_value])

    def get_account_balances(self) -> List[Dict[str, Any]]:
        """Get all current account balances."""
        rows = self.conn.execute("""
            SELECT account_name, account_type, current_debit, current_credit, net_value, updated_at
            FROM accounts
            ORDER BY account_name
        """).fetchall()

        return [
            {
                "name": row[0],
                "type": row[1],
                "debit": row[2],
                "credit": row[3],
                "net_value": row[4],
                "updated_at": str(row[5])
            }
            for row in rows
        ]

    def get_account_load_status(self) -> List[Dict[str, Any]]:
        """Check status of all accounts using a single SQL JOIN for performance."""
        # Use a FULL OUTER JOIN to combine transaction data and account snapshots in one go.
        # This replaces multiple queries and manual Python-level dictionary merging.
        query = """
            WITH tx_summary AS (
                SELECT
                    account,
                    account_type,
                    account_path,
                    COUNT(*) as tx_count,
                    MIN(date) as first_tx,
                    MAX(date) as last_tx
                FROM transactions
                GROUP BY account, account_type, account_path
            )
            SELECT
                COALESCE(t.account, a.account_name) as name,
                COALESCE(t.account_type, a.account_type) as type,
                COALESCE(t.account_path, a.account_path) as path,
                COALESCE(t.tx_count, 0) as transaction_count,
                t.first_tx as first_transaction_date,
                t.last_tx as last_transaction_date,
                (a.account_path IS NOT NULL) as current_balance_present,
                a.updated_at as current_balance_updated_at,
                COALESCE(a.current_debit, 0.0) as current_debit,
                COALESCE(a.current_credit, 0.0) as current_credit,
                COALESCE(a.net_value, 0.0) as net_value
            FROM tx_summary t
            FULL OUTER JOIN accounts a ON
                t.account IS NOT DISTINCT FROM a.account_name AND
                t.account_type IS NOT DISTINCT FROM a.account_type AND
                t.account_path IS NOT DISTINCT FROM a.account_path
            ORDER BY LOWER(name), LOWER(type), path
        """

        rows = self.conn.execute(query).fetchall()

        return [
            {
                "name": row[0],
                "type": row[1],
                "path": row[2],
                "transaction_count": int(row[3]),
                "first_transaction_date": str(row[4]) if row[4] else None,
                "last_transaction_date": str(row[5]) if row[5] else None,
                "current_balance_present": bool(row[6]),
                "current_balance_updated_at": str(row[7]) if row[7] else None,
                "current_debit": row[8],
                "current_credit": row[9],
                "net_value": row[10],
                "needs_current_balance": not bool(row[6]),
                "needs_transactions": int(row[3]) == 0
            }
            for row in rows
        ]

    def file_exists(self, df: pl.DataFrame) -> bool:
        """Check if this file's data already exists in the database."""
        file_hash = self._compute_file_hash(df)

        result = self.conn.execute("""
            SELECT COUNT(*) as count FROM transactions WHERE file_hash = ?
        """, [file_hash]).fetchall()

        return result[0][0] > 0

    def insert_transactions(self, df: pl.DataFrame, filename: str, account_name: str = None, account_type: str = None, account_path: str = None, categorizer=None) -> Dict[str, Any]:
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
                pl.col("category").cast(pl.Utf8).str.split("/").list.get(0).str.strip_chars().alias("category_group")
            )
        if "transaction_type" not in df.columns:
            df = df.with_columns(
                pl.when(pl.col("inflow") > pl.col("outflow"))
                .then(pl.lit("income"))
                .when(pl.col("outflow") > pl.col("inflow"))
                .then(pl.lit("expense"))
                .otherwise(pl.lit("transfer"))
                .alias("transaction_type")
            )

        # 1. Fetch all relevant payee mappings in bulk to avoid N+1 queries
        uncat_mask = pl.col("category") == "Uncategorized"
        if df.filter(uncat_mask).height > 0:
            unique_payees = df.filter(uncat_mask)["payee"].unique().to_list()

            # Query latest mapping for each payee
            payee_ser = pl.Series("payee", unique_payees)
            self.conn.register("temp_payees", pl.DataFrame({"payee": payee_ser}).to_arrow())
            mapping_df = pl.from_arrow(self.conn.execute("""
                SELECT payee, category as mapped_category, category_group as mapped_group
                FROM payee_mappings
                WHERE payee IN (SELECT payee FROM temp_payees)
                QUALIFY ROW_NUMBER() OVER(PARTITION BY payee ORDER BY created_at DESC) = 1
            """).fetch_arrow_table())
            self.conn.unregister("temp_payees")

            if not mapping_df.is_empty():
                df = df.join(mapping_df, on="payee", how="left")
                df = df.with_columns([
                    pl.when(uncat_mask & pl.col("mapped_category").is_not_null())
                    .then(pl.col("mapped_category"))
                    .otherwise(pl.col("category"))
                    .alias("category"),
                    pl.when(uncat_mask & pl.col("mapped_group").is_not_null())
                    .then(pl.col("mapped_group"))
                    .otherwise(pl.col("category_group"))
                    .alias("category_group")
                ]).drop(["mapped_category", "mapped_group"])

        # 2. For remaining Uncategorized, call LLM (once per unique payee)
        remaining_uncat_mask = pl.col("category") == "Uncategorized"
        if categorizer and df.filter(remaining_uncat_mask).height > 0:
            all_categories = self.get_all_categories()
            # Group by payee to only call LLM once per unique unknown payee
            unique_uncat = df.filter(remaining_uncat_mask).group_by("payee").agg([
                pl.col("amount").first(),
                pl.col("date").first()
            ])

            new_mappings = []
            for row in unique_uncat.iter_rows(named=True):
                payee = row["payee"]
                if not payee: continue

                try:
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    if loop.is_running():
                        import nest_asyncio
                        nest_asyncio.apply()

                    llm_result = loop.run_until_complete(
                        categorizer.categorize_transaction(
                            payee, row["amount"], str(row["date"]), all_categories
                        )
                    )

                    if llm_result:
                        new_mappings.append({
                            "payee": payee,
                            "llm_category": llm_result["category"],
                            "llm_group": llm_result["category_group"]
                        })
                        self.save_payee_mapping(payee, llm_result["category"], llm_result["category_group"], llm_result["confidence"])
                        if llm_result["category"] not in all_categories:
                            all_categories.append(llm_result["category"])
                except Exception as e:
                    print(f"LLM Categorization failed for {payee}: {e}")

            if new_mappings:
                new_map_df = pl.DataFrame(new_mappings)
                df = df.join(new_map_df, on="payee", how="left")
                df = df.with_columns([
                    pl.when(remaining_uncat_mask & pl.col("llm_category").is_not_null())
                    .then(pl.col("llm_category"))
                    .otherwise(pl.col("category"))
                    .alias("category"),
                    pl.when(remaining_uncat_mask & pl.col("llm_group").is_not_null())
                    .then(pl.col("llm_group"))
                    .otherwise(pl.col("category_group"))
                    .alias("category_group")
                ]).drop(["llm_category", "llm_group"])

        # Register any new categories discovered
        categories = df.select(["category", "category_group"]).unique().to_dicts()
        self.register_categories(categories)

        # 3. Finalize dataframe for bulk insertion
        # Ensure all required columns exist and are in the right order/type
        # We use select() with aliases to handle missing columns gracefully

        # Ensure date is pl.Date (it might be string in some tests)
        if df["date"].dtype == pl.Utf8:
            df = df.with_columns(
                pl.col("date").str.strptime(pl.Date, strict=False, format="%Y-%m-%d")
            )

        # Define default values for missing columns
        defaults = {
            "account": pl.lit("Unknown"),
            "account_type": pl.lit("Unknown"),
            "account_path": pl.lit(""),
            "description": pl.lit(""),
            "outflow": pl.lit(0.0).cast(pl.Float64),
            "inflow": pl.lit(0.0).cast(pl.Float64),
            "amount": pl.lit(0.0).cast(pl.Float64),
            "transaction_type": pl.lit("transfer")
        }

        final_df = df.with_columns([
            pl.lit(file_hash).alias("file_hash"),
            pl.col("date").dt.strftime("%Y-%m").alias("month_year"),
            pl.lit(filename).alias("file_source")
        ])
        
        # Add missing columns with defaults
        for col, expr in defaults.items():
            if col not in final_df.columns:
                final_df = final_df.with_columns(expr.alias(col))
            else:
                # If column exists, fill nulls and ensure type
                if col in ["outflow", "inflow", "amount"]:
                    final_df = final_df.with_columns(pl.col(col).cast(pl.Float64).fill_null(0.0))
                else:
                    final_df = final_df.with_columns(pl.col(col).fill_null(defaults[col]))

        final_df = final_df.select([
            "file_hash", "account", "account_type", "account_path", "date", "payee",
            "category", "category_group", "description", "outflow", "inflow",
            "amount", "transaction_type", "month_year", "file_source"
        ])

        # Bulk insert using DuckDB's native Polars support
        self.conn.register("temp_insert", final_df.to_arrow())
        self.conn.execute("""
            INSERT INTO transactions 
            (file_hash, account, account_type, account_path, date, payee, category, category_group, description, outflow, inflow, amount, transaction_type, month_year, file_source)
            SELECT * FROM temp_insert
        """)
        self.conn.unregister("temp_insert")
        
        return {
            "status": "inserted",
            "message": f"Successfully inserted {final_df.height} transactions",
            "records_count": final_df.height,
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

        return {
            "months": [row[0] for row in rows],
            "net_amounts": [float(row[1] or 0.0) for row in rows],
            "inflows": [float(row[2] or 0.0) for row in rows],
            "outflows": [float(row[3] or 0.0) for row in rows]
        }

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

    def get_payee_mapping(self, payee: str) -> Optional[Dict[str, Any]]:
        """Get existing category mapping for a payee."""
        row = self.conn.execute("""
            SELECT category, category_group, confidence
            FROM payee_mappings
            WHERE payee = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, [payee]).fetchone()

        if row:
            return {
                "category": row[0],
                "category_group": row[1],
                "confidence": row[2]
            }
        return None

    def save_payee_mapping(self, payee: str, category: str, category_group: str, confidence: float):
        """Save a new payee to category mapping."""
        self.conn.execute("""
            INSERT INTO payee_mappings (payee, category, category_group, confidence, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT (payee, category) DO UPDATE SET
                category_group = EXCLUDED.category_group,
                confidence = EXCLUDED.confidence,
                created_at = EXCLUDED.created_at
        """, [payee, category, category_group, confidence])


    def get_all_categories(self) -> List[str]:
        """Get list of all unique category names."""
        rows = self.conn.execute("SELECT DISTINCT category_name FROM categories").fetchall()
        return [row[0] for row in rows]

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Cleanup on object deletion."""
        self.close()
