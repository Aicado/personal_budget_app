# GitHub Copilot Instructions - Personal Budget App

You are an expert Python and React engineer assisting with the development of the YNAB Analyzer.

## 🐍 Backend Development (FastAPI, Polars, DuckDB)

### Core Technologies
- **Python 3.10+**
- **FastAPI** for the web layer.
- **Polars** for data manipulation (DO NOT use Pandas).
- **DuckDB** for persistence and analytical queries.
- **uv** for package management.

### Database Patterns (DuckDB)
- Always use `src/backend/database.py` for database interactions.
- Schema is defined in `TransactionDatabase._initialize_db`.
- Use vectorized insertion via Polars and Arrow:
  ```python
  df = pl.DataFrame(records)
  self.conn.register("temp_table", df.to_arrow())
  self.conn.execute("INSERT INTO table SELECT * FROM temp_table")
  ```
- Use `MERGE INTO` or index-based checks for duplicate prevention.

### Data Ingestion (Polars)
- Data cleaning logic lives in `src/backend/transaction_analyzer.py`.
- Handle currency with care: Clean `$`, `,`, and handle `null` before casting to `Float64`.
- Transaction amounts should follow: `amount = inflow - outflow`.

### Data Hierarchy
- `ynab_data/*.csv`: Historical transactions.
- `data/**/current.csv`: Real-time account balance snapshots.
- Accounts are identified by their path in the `data/` directory.

### Running Backend
- Always use `uv run`: `uv run -m uvicorn src.backend.main:app --reload`

## ⚛️ Frontend Development (React 19, TypeScript)

### Core Technologies
- **React 19** (Functional components, Hooks).
- **Vite** for bundling.
- **TypeScript** for type safety.
- CSS for styling (keep it modular).

### API Communication
- Use the standard `fetch` API or a lightweight wrapper.
- Backend is typically on `http://localhost:8000`.

## 🛠 Tooling
- Use `uv` for all Python tasks.
- Use `npm` for all frontend tasks.
- Prefer `Makefile` commands for common workflows (`make setup`, `make dev`).

## 🧠 Knowledge Context
- **Account Identification**: Accounts are often derived from the filesystem structure in the `data/` directory (e.g., `data/Assets/Checking`).
- **File Hashing**: We use MD5 hashes of the first 100 rows of a CSV to detect duplicate file uploads.
- **Current Balance Logic**: The `accounts` table stores the "latest" state, while the `transactions` table stores the history. When updating balances, we use the `MERGE` statement in DuckDB.
