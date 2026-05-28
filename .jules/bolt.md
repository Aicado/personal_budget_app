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

## 2025-05-19 - [Payee Mapping Filtered Lookup]
**Learning:** In transaction ingestion, fetching all unique payee mappings from DuckDB creates a scalability bottleneck. Filtering the lookup query to only include payees present in the current batch (using WHERE payee IN (SELECT UNNEST(?))) combined with a database index on the payee column ensures that mapping performance remains high regardless of history size.
**Action:** Always filter metadata lookups by batch keys and index the lookup column to maintain ingestion speed as the database scales.

## 2025-05-19 - [DuckDB Grouping Sets vs Separate Queries]
**Learning:** For multi-level aggregations (e.g., stats, category totals, and monthly trends), using a single SQL query with GROUPING SETS was ~3.5x slower than executing three focused queries in this DuckDB/FastAPI environment (0.024s vs 0.085s). The overhead of complex grouping logic in a single pass exceeded the cost of multiple scans on this dataset.
**Action:** Measure single-pass complex queries against multiple simple queries in DuckDB; columnar stores often favor multiple simple scans over complex branching logic.

## 2025-05-19 - [Indexing Columnar Aggregations]
**Learning:** Adding traditional B-Tree indexes on columns used primarily for grouping (like month_year or category) in DuckDB's columnar format can significantly degrade performance (e.g., 0.02s -> 0.8s for aggregation). DuckDB's zone maps and vectorized execution are already highly optimized for these scans.
**Action:** Avoid indexing columns used mainly for GROUP BY in DuckDB unless specific range or point lookups are the primary bottleneck, as the index overhead often outweighs the scan benefits.
