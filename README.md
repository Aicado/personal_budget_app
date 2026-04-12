# Personal Budget App (YNAB Analyzer)

A high-performance full-stack application designed to analyze personal budget data, visualize spending trends, and manage historical transaction records. Unlike simple CSV viewers, this app uses a dedicated OLAP database (DuckDB) and a vectorized data processing engine (Polars) to provide deep insights into your financial habits.

## 🎯 Core Features

- **Automated Data Ingestion**: Seamlessly processes YNAB CSV exports and "Current Balance" snapshots.
- **OLAP-Powered Analysis**: Uses DuckDB for lightning-fast queries across years of transaction data.
- **Monthly Trends**: Visualize income, expenses, and net monthly trends with interactive reports.
- **Category Intelligence**: Detailed spending breakdowns by category and category groups.
- **Multi-File Support**: Aggregates data from multiple accounts and time periods into a unified view.
- **Local-First Security**: All data is processed and stored locally on your machine.

---

## 🏗 Backend Architecture & Database

The backend is built with **FastAPI**, **DuckDB**, and **Polars**, focusing on speed, reliability, and ease of data management.

### 🗄 Database Schema (DuckDB)
The application uses **DuckDB**, an in-process SQL OLAP database management system. It is optimized for analytical queries and handles large datasets with minimal overhead.

The schema consists of three primary tables:
- `transactions`: Stores every individual transaction with metadata (account, category, inflow/outflow, etc.).
- `accounts`: Stores current balance snapshots, including `net_value`, `current_debit`, and `current_credit`.
- `categories`: Maintains a registry of unique categories and their parent groups.

#### Duplicate Detection
To prevent data corruption from repeated uploads, we use a **MD5 hashing strategy**. Before insertion, a hash is generated from the CSV content. If the hash exists in the `transactions` table, the upload is safely ignored.

### 🔄 Data Ingestion & Backfill Logic
The ingestion engine (found in `src/backend/backfill.py` and `src/backend/transaction_analyzer.py`) follows a sophisticated pipeline:

1. **Discovery**: The `backfill` script recursively scans the `data/` directory for `current.csv` (balances) and `ynab_data/*.csv` (transactions).
2. **Parsing (Polars)**: CSVs are loaded using Polars for high-speed cleaning. We handle:
   - Date standardization (MM/DD/YYYY to ISO).
   - Currency cleaning (removing symbols, handling empty strings).
   - Column normalization (mapping YNAB's varying export formats).
3. **Account Linkage**: Transactions are linked to specific account metadata extracted from the file structure (e.g., `data/Assets/Checking/current.csv` informs the app about the "Checking" account).
4. **Current Balance vs. Transactions**:
   - **Transactions** provide the historical "story".
   - **Current Balances** provide the "state of the union" at a specific point in time.
   - The app merges these two sources to provide a complete picture of net worth alongside spending trends.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- `uv` ([Install uv](https://docs.astral.sh/uv/))
- Node.js 18+

### 2. Setup & Installation
```bash
# Install all dependencies (Python & Node)
bash setup.sh

# Alternatively, using uv directly
uv venv
uv sync
npm install
```

### 3. Run the Application
```bash
# Start both Backend (8000) and Frontend (5173)
bash start.sh
```

---

## 🛠 Tech Stack

- **Frontend**: React 19, TypeScript, Vite, CSS3
- **Backend**: FastAPI (Python)
- **Data Engine**: Polars (Vectorized processing)
- **Database**: DuckDB (Analytical SQL)
- **Package Management**: `uv` (Python), `npm` (Node)

---

## 📁 Project Structure

```
.
├── src/
│   ├── backend/           # FastAPI, DuckDB logic, Polars analyzers
│   │   ├── database.py    # DuckDB schema & connection management
│   │   ├── backfill.py    # Automated data ingestion logic
│   │   ├── main.py        # API endpoints
│   │   └── transaction_analyzer.py # Data cleaning & stats
│   ├── components/        # React UI components
│   └── App.tsx            # Main frontend entry
├── data/                  # Root for your CSV data
│   ├── Assets/            # Account-specific directories
│   │   └── Checking/
│   │       └── current.csv # Account balance snapshots
│   └── ynab_data/         # Historical transaction exports
├── pyproject.toml         # Python dependencies (managed by uv)
└── package.json           # Frontend dependencies
```

---

## 🔧 Development with `uv`

This project leverages `uv` for extremely fast dependency management.

```bash
# Add a new Python package
uv add <package>

# Run a script in the managed environment
uv run python src/backend/backfill.py

# Sync the environment
uv sync
```

---

## 📝 API Endpoints

- `POST /analyze`: Process a single CSV and return statistics.
- `POST /analyze-multiple`: Batch process multiple files.
- `GET /accounts/status`: View which accounts have transactions vs. current balances.
- `GET /net-worth/current-balances`: Aggregated net worth view.
- `GET /database/stats`: Overview of records stored in DuckDB.

---

## 🔐 Privacy
Your financial data is **never** uploaded to a server. All processing happens in-memory or in your local DuckDB file located at `db/ynab_analyzer.duckdb`.
