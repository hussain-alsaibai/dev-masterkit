# snapdb-cli — SnapDB Command-Line Interface

## What This Tool Does

CLI tool for [SnapDB](tools/snapdb-guide.md) — ultra-lightweight in-memory Python database. Zero dependencies, works as standalone script or pip-installed tool.

## Installation

```bash
# Via pip
pip install snapdb

# Standalone — just copy the file, zero deps
curl -O https://raw.githubusercontent.com/hussain-alsaibai/snapdb-cli/main/snapdb_cli.py
chmod +x snapdb_cli.py
```

## Usage

```bash
# Initialize DB with schema
snapdb-cli init users id:i32,name:str,email:str --path ./data

# Insert records
snapdb-cli insert users '{"id": 1, "name": "alice", "email": "alice@example.com"}' --path ./data
snapdb-cli insert users '{"id": 2, "name": "bob", "email": "bob@example.com"}' --path ./data

# Read, list, count
snapdb-cli get users 0 --path ./data
snapdb-cli list users --limit 100 --path ./data
snapdb-cli count users --path ./data

# Export
snapdb-cli export users --format json --path ./data
snapdb-cli export users --format csv --path ./data

# Benchmark
snapdb-cli benchmark users --ops 10000 --path ./data

# Live watch
snapdb-cli watch users --interval 0.5 --path ./data
```

## Schema Types

| Type | Description |
|------|-------------|
| `i8`, `i16`, `i32`, `i64` | Signed integers |
| `u8`–`u64` | Unsigned integers |
| `f32`, `f64` | Floats |
| `str` | UTF-8 string |
| `bytes:N` | Fixed-size bytes |

## Notes

- Works with both `snapdb` Python library and standalone SnapDB data files
- Supports JSON and CSV export formats
- Built-in benchmark mode for performance testing
- Live watch mode for monitoring changes
- MIT License, zero runtime dependencies

## Last Verified: 2026-08-10
