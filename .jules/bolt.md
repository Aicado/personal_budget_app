## 2025-05-14 - [DuckDB FULL OUTER JOIN vs Python Merging]
**Learning:** Replacing Python-level dictionary merging with a single SQL `FULL OUTER JOIN` in DuckDB significantly improves the performance of cross-table status checks. However, when joining on columns that may contain NULL values (like optional paths), standard `=` comparisons fail.
**Action:** Always use `IS NOT DISTINCT FROM` for join conditions in DuckDB when the join keys might contain NULL values to ensure behavior matches Python dictionary merging.

## 2025-05-15 - [Vectorized Ingestion vs Row-by-row Mapping]
**Learning:** Vectorizing Polars ingestion and using a single SQL query with `QUALIFY ROW_NUMBER()` to fetch unique mappings significantly outperforms row-by-row loops and repeated SQL calls during data ingestion. This reduced ingestion overhead by ~75%.
**Action:** Always prefer vectorized joins for mapping operations in ingestion pipelines and deduplicate external service calls (like LLM) by grouping unique keys.

## 2025-05-16 - [Parallel LLM Categorization with asyncio.gather]
**Learning:** Sequential LLM calls during ingestion create a significant bottleneck (O(N) relative to unique payees). Parallelizing these calls using `asyncio.gather` reduces the overhead to O(1) relative to batch size, assuming the service can handle concurrency.
**Action:** Use `asyncio.gather` for independent network/IO-bound tasks within ingestion pipelines to maximize throughput.

## 2025-05-16 - [Polars split_exact vs split Regression]
**Learning:** Attempting to optimize string splitting with `split_exact` in Polars can lead to data loss. Unlike regular `split`, `split_exact` returns `null` if the exact number of delimiters is not found.
**Action:** Avoid `split_exact` for optional delimiters unless `null` handling is explicitly implemented. Stick to regular `split` for robustness when data format is variable.
