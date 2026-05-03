## 2025-05-14 - [DuckDB FULL OUTER JOIN vs Python Merging]
**Learning:** Replacing Python-level dictionary merging with a single SQL `FULL OUTER JOIN` in DuckDB significantly improves the performance of cross-table status checks. However, when joining on columns that may contain NULL values (like optional paths), standard `=` comparisons fail.
**Action:** Always use `IS NOT DISTINCT FROM` for join conditions in DuckDB when the join keys might contain NULL values to ensure behavior matches Python dictionary merging.

## 2025-05-15 - [Vectorized Ingestion vs Row-by-row Mapping]
**Learning:** Vectorizing Polars ingestion and using a single SQL query with `QUALIFY ROW_NUMBER()` to fetch unique mappings significantly outperforms row-by-row loops and repeated SQL calls during data ingestion. This reduced ingestion overhead by ~75%.
**Action:** Always prefer vectorized joins for mapping operations in ingestion pipelines and deduplicate external service calls (like LLM) by grouping unique keys.

## 2025-05-16 - [Parallel LLM Categorization]
**Learning:** Parallelizing I/O-bound LLM calls in synchronous database methods using `asyncio.gather` and `asyncio.Semaphore` significantly reduces ingestion latency (measured ~70% speedup). To avoid race conditions in parallel tasks, pass a static snapshot of known categories.
**Action:** Use `asyncio.Semaphore` (limit 10) and `asyncio.gather` for external API calls within ingestion pipelines, and always snapshot shared state before concurrent execution.
