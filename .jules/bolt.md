## 2025-05-14 - [DuckDB FULL OUTER JOIN vs Python Merging]
**Learning:** Replacing Python-level dictionary merging with a single SQL `FULL OUTER JOIN` in DuckDB significantly improves the performance of cross-table status checks. However, when joining on columns that may contain NULL values (like optional paths), standard `=` comparisons fail.
**Action:** Always use `IS NOT DISTINCT FROM` for join conditions in DuckDB when the join keys might contain NULL values to ensure behavior matches Python dictionary merging.

## 2025-05-15 - [Vectorized Ingestion vs Row-by-row Mapping]
**Learning:** Vectorizing Polars ingestion and using a single SQL query with `QUALIFY ROW_NUMBER()` to fetch unique mappings significantly outperforms row-by-row loops and repeated SQL calls during data ingestion. This reduced ingestion overhead by ~75%.
**Action:** Always prefer vectorized joins for mapping operations in ingestion pipelines and deduplicate external service calls (like LLM) by grouping unique keys.

## 2025-05-16 - [Parallel LLM Categorization with Semaphore]
**Learning:** Parallelizing I/O-bound LLM categorization calls using `asyncio.gather` in a synchronous database method (via `nest_asyncio`) significantly reduces ingestion latency (up to 87%). Using an `asyncio.Semaphore` is critical to avoid overwhelming local LLM services like Ollama.
**Action:** When performing multiple independent I/O-bound tasks in ingestion pipelines, always use `asyncio.gather` with a concurrency limit (Semaphore) to maximize throughput without sacrificing stability.
