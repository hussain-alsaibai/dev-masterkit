# Changelog

All notable changes to `tiny-bulkhead` are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-10-13

### Added
- `Bulkhead` class with `acquire` / `release` / context-manager / `run` API.
- `BulkheadPool` for named-bulkhead registries.
- Async support via `acquire_async` / `release_async` / `run_async` / `async with bh()`.
- `BulkheadStats` snapshot dataclass (JSON-serializable).
- `BulkheadFull` and `BulkheadTimeout` exceptions.
- 23 unit tests (concurrency, async, pool, stats, edge cases).
