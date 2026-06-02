## 2025-05-14 - [DuckDB FULL OUTER JOIN vs Python Merging]
**Learning:** Replacing Python-level dictionary merging with a single SQL `FULL OUTER JOIN` in DuckDB significantly improves the performance of cross-table status checks. However, when joining on columns that may contain NULL values (like optional paths), standard `=` comparisons fail.
**Action:** Always use `IS NOT DISTINCT FROM` for join conditions in DuckDB when the join keys might contain NULL values to ensure behavior matches Python dictionary merging.

## 2025-05-15 - [Vectorized Ingestion vs Row-by-row Mapping]
**Learning:** Vectorizing Polars ingestion and using a single SQL query with `QUALIFY ROW_NUMBER()` to fetch unique mappings significantly outperforms row-by-row loops and repeated SQL calls during data ingestion. This reduced ingestion overhead by ~75%.
**Action:** Always prefer vectorized joins for mapping operations in ingestion pipelines and deduplicate external service calls (like LLM) by grouping unique keys.

## 2025-05-16 - [Parallel LLM Categorization with Connection Pooling]
**Learning:** Sequential LLM calls during transaction ingestion create a significant bottleneck (e.g., 5.4s for 10 unique payees). Parallelizing these calls with `asyncio.gather` and using a shared `httpx.AsyncClient` for connection pooling reduces latency by ~77% (down to ~1.25s).
**Action:** Use `asyncio.Semaphore` to limit concurrency and a single `httpx.AsyncClient` per batch to maximize performance of I/O-bound LLM tasks.

## 2025-05-17 - [Vectorized Try-Cast vs Conditional Branching]
**Learning:** In Polars, cleaning currency strings using `pl.when().then().otherwise()` evaluates the cleaning expression twice. Replacing this with a single-pass `.cast(pl.Float64, strict=False).fill_null(0.0)` improves performance by ~2.6x. Additionally, `str.replace_all("$", "")` interprets `$` as a regex anchor (end-of-line) unless `literal=True` is used, which was causing a parsing bug for leading dollar signs.
**Action:** Always use `literal=True` for literal string replacements in Polars and prefer `strict=False` casts with `fill_null` for high-performance data cleaning.

## 2025-05-18 - [Account Index for Status Retrieval]
**Learning:** Adding a database index on the `account` column in the `transactions` table (DuckDB) significantly improves performance for account-specific filtering and transaction retrieval by avoiding full table scans during `GROUP BY` operations in `get_account_load_status`.
**Action:** Always index columns used in frequent `GROUP BY` or `WHERE` clauses in the core transaction table to maintain dashboard responsiveness as data volume grows.

## 2025-05-19 - [Batched Expression-based Polars Refactor]
**Learning:** Batching multiple transformations into fewer `with_columns` passes and refactoring cleaning helpers to return `pl.Expr` instead of `pl.DataFrame` significantly reduces DataFrame scanning and cloning overhead. In `TransactionAnalyzer`, this improved `parse_transactions` performance by ~3.7x (0.75s to 0.20s for 1M rows).
**Action:** Always return `pl.Expr` from helper methods in Polars processing pipelines to enable batched execution in the main flow.

## 2025-05-20 - [Single-Pass Aggregation for Averages]
**Learning:** Calculating monthly averages in `TransactionAnalyzer.get_summary_stats` using a single `select` with `pl.col("month_str").n_unique()` is ~1.6x faster than performing a separate `group_by` and then averaging. Using `.row(0, named=True)` and `dict(zip(...))` further optimizes the hand-off to Python.
**Action:** Avoid separate `group_by` operations for simple aggregate ratios (like averages per month) when they can be calculated using `n_unique` in a single scan.
