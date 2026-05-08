## 2025-05-14 - [DuckDB FULL OUTER JOIN vs Python Merging]
**Learning:** Replacing Python-level dictionary merging with a single SQL `FULL OUTER JOIN` in DuckDB significantly improves the performance of cross-table status checks. However, when joining on columns that may contain NULL values (like optional paths), standard `=` comparisons fail.
**Action:** Always use `IS NOT DISTINCT FROM` for join conditions in DuckDB when the join keys might contain NULL values to ensure behavior matches Python dictionary merging.

## 2025-05-15 - [Vectorized Ingestion vs Row-by-row Mapping]
**Learning:** Vectorizing Polars ingestion and using a single SQL query with `QUALIFY ROW_NUMBER()` to fetch unique mappings significantly outperforms row-by-row loops and repeated SQL calls during data ingestion. This reduced ingestion overhead by ~75%.
**Action:** Always prefer vectorized joins for mapping operations in ingestion pipelines and deduplicate external service calls (like LLM) by grouping unique keys.

## 2025-05-16 - [Parallelizing LLM categorization in synchronous DB methods]
**Learning:** Parallelizing I/O-bound LLM calls in synchronous database methods (like `insert_transactions`) using `asyncio.gather` and `asyncio.Semaphore` avoids the massive overhead of repeated event loop restarts (`loop.run_until_complete` in a loop) and sequential network latency. This yielded an ~84% speedup in benchmarks.
**Action:** Use an `async` batch processor helper and a single `loop.run_until_complete` call when dealing with multiple I/O-bound tasks in a synchronous context to maximize throughput.
