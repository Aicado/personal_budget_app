from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import io
from pathlib import Path

from .transaction_analyzer import TransactionAnalyzer
from .database import TransactionDatabase
from .backfill import backfill_database

app = FastAPI(title="YNAB Analyzer API", version="0.1.0")

# Initialize database
db = TransactionDatabase()

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
                "transactions_added": 0
            }
        else:
            db_result = db.insert_transactions(analyzer.df, file.filename)
            db_report = {
                "status": "inserted",
                "message": f"Successfully inserted {len(analyzer.df)} transactions",
                "transactions_in_file": len(analyzer.df),
                "transactions_added": len(analyzer.df),
                "file_hash": db_result.get("file_hash")
            }
        
        return {
            "filename": file.filename,
            "monthly_trends": analyzer.get_monthly_trends(),
            "category_trends": analyzer.get_category_trends(),
            "category_totals": analyzer.get_category_totals(),
            "summary_stats": analyzer.get_summary_stats(),
            "database": db_report
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
                db_result = db.insert_transactions(analyzer.df, file.filename)
                db_results.append({
                    "filename": file.filename,
                    "status": "inserted",
                    "transactions_in_file": len(analyzer.df),
                    "transactions_added": len(analyzer.df),
                    "file_hash": db_result.get("file_hash")
                })
            else:
                db_results.append({
                    "filename": file.filename,
                    "status": "duplicate",
                    "message": "File already exists in database",
                    "transactions_in_file": len(analyzer.df),
                    "transactions_added": 0
                })
        
        # Combine all dataframes
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
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
            "database_results": db_results
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
    """Get information about all uploaded files."""
    try:
        return {"files": db.get_files_info()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/backfill")
def backfill_ynab_data():
    """Backfill the database with all YNAB CSV files in the data directory."""
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "data"
        
        if not data_dir.exists():
            raise HTTPException(status_code=400, detail="data directory not found")
        
        # Run backfill
        result = backfill_database(str(data_dir))
        return result
        
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error during backfill: {error_msg}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/net-worth/current-balances")
def get_current_balances():
    """Get current account balances from current.csv files in account subdirectories.
    
    Debit = asset value (what you own)
    Credit = liability value (what you owe)
    Net Value = Debit - Credit
    """
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "data"
        
        if not data_dir.exists():
            raise HTTPException(status_code=404, detail="data directory not found")
        
        # Find all current.csv files in account subdirectories
        accounts = []
        total_assets = 0
        total_debt = 0
        
        # Scan all subdirectories for current.csv files
        for current_csv_path in data_dir.rglob("current.csv"):
            try:
                # Extract account type and name from path
                # Path structure: data/[account_type]/[account_name]/current.csv
                parts = current_csv_path.relative_to(data_dir).parts
                
                if len(parts) >= 3 and parts[-1] == "current.csv":
                    account_type = parts[0]
                    account_name = parts[1]
                    
                    # Read the current.csv file
                    df = pd.read_csv(current_csv_path)
                    
                    if len(df) > 0:
                        # Get the most recent balance (last row)
                        latest_row = df.iloc[-1]
                        
                        # Extract debit and credit values
                        debit = 0.0
                        credit = 0.0
                        
                        if 'debit' in df.columns:
                            try:
                                debit = float(latest_row['debit'])
                            except (ValueError, TypeError):
                                debit = 0.0
                        
                        if 'credit' in df.columns:
                            try:
                                credit = float(latest_row['credit'])
                            except (ValueError, TypeError):
                                credit = 0.0
                        
                        # Calculate net value: debit (asset) - credit (liability)
                        net_value = debit - credit
                        
                        # Classify as asset or debt
                        is_asset = 'credit' not in account_type.lower() and 'debt' not in account_type.lower()
                        
                        accounts.append({
                            "name": account_name.replace('_', ' ').title(),
                            "balance": net_value,
                            "debit": debit,
                            "credit": credit,
                            "type": account_type.replace('_', ' ').title(),
                            "is_asset": is_asset
                        })
                        
                        # Add to appropriate total
                        if is_asset:
                            total_assets += net_value
                        else:
                            # For debt accounts, the net_value represents net liability
                            # If positive (rewards > owed), it reduces debt
                            # If negative (owed > rewards), it increases debt
                            total_debt += abs(net_value) if net_value < 0 else -net_value
            except Exception as e:
                print(f"Warning: Error processing {current_csv_path}: {e}")
                continue
        
        if not accounts:
            return {
                "accounts": [],
                "total_assets": 0,
                "total_debt": 0,
                "net_worth": 0,
                "message": "No account balance data found"
            }
        
        return {
            "accounts": accounts,
            "total_assets": total_assets,
            "total_debt": total_debt,
            "net_worth": total_assets - total_debt
        }
        
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error fetching current balances: {error_msg}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
