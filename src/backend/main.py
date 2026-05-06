from .llm_service import LLMCategorizer
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import polars as pl
from pathlib import Path

from .transaction_analyzer import TransactionAnalyzer
from .database import TransactionDatabase
from .backfill import backfill_database

app = FastAPI(title="Personal Budget App API", version="0.1.0")

# Initialize database
db = TransactionDatabase()
categorizer = LLMCategorizer()


@app.on_event("startup")
def load_data_on_startup():
    """Automatically load data from the data directory when the app starts."""
    project_root = Path(__file__).parent.parent.parent
    accounts_dir = project_root / "data"
    transactions_dir = project_root / "data" / "transaction_data"
    if accounts_dir.exists() or transactions_dir.exists():
        try:
            backfill_database(str(accounts_dir), str(transactions_dir), categorizer=categorizer)
        except Exception as e:
            print(f"Warning: failed to load data on startup: {e}")


# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    """Analyze uploaded CSV file and return trends, storing to DuckDB."""
    try:
        # Read the file content
        content = await file.read()

        # Decode CSV content
        csv_content = content.decode("utf-8")

        # Analyze
        analyzer = TransactionAnalyzer()
        df = analyzer.load_csv(csv_content)
        analyzer.parse_transactions(df)

        # Check for duplicates and store in database
        duplicate_check = db.file_exists(analyzer.df)

        if duplicate_check:
            db_report = {
                "status": "duplicate",
                "message": "This file's data already exists in the database. Skipping insertion.",
                "transactions_in_file": len(analyzer.df),
                "transactions_added": 0,
            }
        else:
            db_result = db.insert_transactions(analyzer.df, file.filename, categorizer=categorizer)
            db_report = {
                "status": "inserted",
                "message": f"Successfully inserted {len(analyzer.df)} transactions",
                "transactions_in_file": len(analyzer.df),
                "transactions_added": len(analyzer.df),
                "file_hash": db_result.get("file_hash"),
            }

        return {
            "filename": file.filename,
            "monthly_trends": analyzer.get_monthly_trends(),
            "category_trends": analyzer.get_category_trends(),
            "category_totals": analyzer.get_category_totals(),
            "summary_stats": analyzer.get_summary_stats(),
            "database": db_report,
        }
    except Exception as e:
        import traceback

        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error analyzing file: {error_msg}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze-multiple")
async def analyze_multiple_files(files: list[UploadFile] = File(...)):
    """Analyze multiple CSV files and aggregate results, storing each to DuckDB."""
    try:
        all_dfs = []
        db_results = []

        for file in files:
            content = await file.read()
            csv_content = content.decode("utf-8")
            analyzer = TransactionAnalyzer()
            df = analyzer.load_csv(csv_content)
            analyzer.parse_transactions(df)
            all_dfs.append(analyzer.df)

            # Store each file in database
            duplicate_check = db.file_exists(analyzer.df)
            if not duplicate_check:
                db_result = db.insert_transactions(
                    analyzer.df, file.filename, categorizer=categorizer
                )
                db_results.append(
                    {
                        "filename": file.filename,
                        "status": "inserted",
                        "transactions_in_file": len(analyzer.df),
                        "transactions_added": len(analyzer.df),
                        "file_hash": db_result.get("file_hash"),
                    }
                )
            else:
                db_results.append(
                    {
                        "filename": file.filename,
                        "status": "duplicate",
                        "message": "File already exists in database",
                        "transactions_in_file": len(analyzer.df),
                        "transactions_added": 0,
                    }
                )

        # Combine all dataframes
        combined_df = pl.concat(all_dfs, rechunk=True)

        # Analyze combined data
        analyzer = TransactionAnalyzer()
        analyzer.df = combined_df

        return {
            "num_files": len(files),
            "filenames": [f.filename for f in files],
            "monthly_trends": analyzer.get_monthly_trends(),
            "category_trends": analyzer.get_category_trends(),
            "category_totals": analyzer.get_category_totals(),
            "summary_stats": analyzer.get_summary_stats(),
            "database_results": db_results,
        }
    except Exception as e:
        import traceback

        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error analyzing files: {error_msg}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/database/stats")
def get_database_stats():
    """Get statistics about stored transactions."""
    try:
        return db.get_database_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/database/files")
def get_uploaded_files():
    """Get account summary data from the database."""
    try:
        return {"files": db.get_account_summaries()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/accounts/status")
def get_account_status():
    """Get account load status for transactions and current balances."""
    try:
        return {"accounts": db.get_account_load_status()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/accounts/{account_name}/transactions")
def get_account_transactions(account_name: str, limit: int = 50):
    """Get recent transactions for a specific account."""
    try:
        # URL decode the account name
        import urllib.parse

        account_name = urllib.parse.unquote(account_name)

        rows = db.conn.execute(
            """
            SELECT date, payee, category, outflow, inflow, amount, description
            FROM transactions 
            WHERE account = ?
            ORDER BY date DESC
            LIMIT ?
        """,
            [account_name, limit],
        ).fetchall()

        transactions = [
            {
                "date": str(row[0]),
                "payee": row[1] or "",
                "category": row[2] or "",
                "outflow": float(row[3] or 0),
                "inflow": float(row[4] or 0),
                "amount": float(row[5] or 0),
                "description": row[6] or "",
            }
            for row in rows
        ]

        return {"account": account_name, "transactions": transactions}
    except Exception as e:
        import traceback

        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error fetching account transactions: {error_msg}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/net-worth/current-balances")
def get_current_balances():
    """Get current account balances from the database."""
    try:
        accounts = db.get_account_balances()
        total_assets = 0.0
        total_debt = 0.0
        results = []

        for account in accounts:
            account_type = account.get("type", "Unknown") or "Unknown"
            is_asset = "credit" not in account_type.lower() and "debt" not in account_type.lower()
            net_value = account.get("net_value", 0.0)

            results.append(
                {
                    "name": account.get("name", "Unknown"),
                    "type": account_type,
                    "debit": account.get("debit", 0.0),
                    "credit": account.get("credit", 0.0),
                    "net_value": net_value,
                    "is_asset": is_asset,
                }
            )

            if is_asset:
                total_assets += net_value
            else:
                total_debt += abs(net_value)

        return {
            "accounts": results,
            "total_assets": total_assets,
            "total_debt": total_debt,
            "net_worth": total_assets - total_debt,
        }
    except Exception as e:
        import traceback

        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error fetching current balances: {error_msg}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
