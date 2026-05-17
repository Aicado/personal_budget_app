## 2025-05-14 - [DuckDB FULL OUTER JOIN vs Python Merging]
**Learning:** Replacing Python-level dictionary merging with a single SQL `FULL OUTER JOIN` in DuckDB significantly improves the performance of cross-table status checks. However, when joining on columns that may contain NULL values (like optional paths), standard `=` comparisons fail.
**Action:** Always use `IS NOT DISTINCT FROM` for join conditions in DuckDB when the join keys might contain NULL values to ensure behavior matches Python dictionary merging.

## 2025-05-15 - [Vectorized Ingestion vs Row-by-row Mapping]
**Learning:** Vectorizing Polars ingestion and using a single SQL query with `QUALIFY ROW_NUMBER()` to fetch unique mappings significantly outperforms row-by-row loops and repeated SQL calls during data ingestion. This reduced ingestion overhead by ~75%.
**Action:** Always prefer vectorized joins for mapping operations in ingestion pipelines and deduplicate external service calls (like LLM) by grouping unique keys.

## 2025-05-16 - [Parallel LLM Categorization with Connection Pooling]
**Learning:** Sequential LLM calls during transaction ingestion create a significant bottleneck (e.g., 5.4s for 10 unique payees). Parallelizing these calls with `asyncio.gather` and using a shared `httpx.AsyncClient` for connection pooling reduces latency by ~77% (down to ~1.25s).
**Action:** Use `asyncio.Semaphore` to limit concurrency and a single `httpx.AsyncClient` per batch to maximize performance of I/O-bound LLM tasks.
