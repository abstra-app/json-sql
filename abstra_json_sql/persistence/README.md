# Persistence Implementations

This directory contains the different persistence implementations for the table storage system.

## Structure

- `memory.py` - In-memory table storage (`InMemoryTables`)
- `json.py` - File system storage using JSON files (`FileSystemJsonTables`)
- `jsonl.py` - File system storage using JSONL files (`FileSystemJsonLTables`) 
- `extended.py` - Extended tables that combine a base persistence layer with additional in-memory tables (`ExtendedTables`)

## Usage

All persistence implementations conform to the `ITablesSnapshot` interface defined in the main `tables.py` file. You can import them directly from the main module:

```python
from abstra_json_sql.tables import (
    InMemoryTables,
    FileSystemJsonTables, 
    FileSystemJsonLTables,
    ExtendedTables
)
```

Or import them from the persistence module:

```python
from abstra_json_sql.persistence import (
    InMemoryTables,
    FileSystemJsonTables,
    FileSystemJsonLTables, 
    ExtendedTables
)
```
