## 2025-05-14 - [DuckDB FULL OUTER JOIN vs Python Merging]
**Learning:** Replacing Python-level dictionary merging with a single SQL `FULL OUTER JOIN` in DuckDB significantly improves the performance of cross-table status checks. However, when joining on columns that may contain NULL values (like optional paths), standard `=` comparisons fail.
**Action:** Always use `IS NOT DISTINCT FROM` for join conditions in DuckDB when the join keys might contain NULL values to ensure behavior matches Python dictionary merging.

## 2025-05-14 - [Vectorized Transaction Insertion]
**Learning:** Replacing row-by-row `iter_rows` loops and N+1 SQL queries in `TransactionDatabase.insert_transactions` with vectorized Polars joins and pre-fetched mappings resulted in a ~100x performance increase (improving speed to ~45k rows/sec from ~400 rows/sec). Grouping LLM calls by unique payee also significantly reduces overhead for batches with repeated unknown payees.
**Action:** Use DuckDB's `QUALIFY ROW_NUMBER() OVER(PARTITION BY key ORDER BY created_at DESC) = 1` to pre-fetch the latest mappings in bulk, then apply them using Polars `join`.
