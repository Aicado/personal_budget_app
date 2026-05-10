## 2025-05-14 - [DuckDB FULL OUTER JOIN vs Python Merging]
**Learning:** Replacing Python-level dictionary merging with a single SQL `FULL OUTER JOIN` in DuckDB significantly improves the performance of cross-table status checks. However, when joining on columns that may contain NULL values (like optional paths), standard `=` comparisons fail.
**Action:** Always use `IS NOT DISTINCT FROM` for join conditions in DuckDB when the join keys might contain NULL values to ensure behavior matches Python dictionary merging.

## 2025-05-15 - [Vectorized Ingestion vs Row-by-row Mapping]
**Learning:** Vectorizing Polars ingestion and using a single SQL query with `QUALIFY ROW_NUMBER()` to fetch unique mappings significantly outperforms row-by-row loops and repeated SQL calls during data ingestion. This reduced ingestion overhead by ~75%.
**Action:** Always prefer vectorized joins for mapping operations in ingestion pipelines and deduplicate external service calls (like LLM) by grouping unique keys.

## 2024-05-16 - [Parallelizing LLM Categorization with Semaphore]
**Learning:** Sequential calls to an LLM service during data ingestion create a massive bottleneck. Parallelizing these calls using `asyncio.gather` with a `Semaphore` (e.g., limit 10) can reduce ingestion time by ~85%. To avoid race conditions, snapshot any shared state (like known categories) before spawning parallel tasks.
**Action:** Always use concurrent execution for I/O-bound external service calls in the ingestion pipeline, and use semaphores to prevent resource exhaustion.
