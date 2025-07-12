# abstra-json-sql

`abstra-json-sql` is a Python library that allows you to **run SQL queries on JSON data**. It is designed to be simple and easy to use, while providing powerful features for querying and manipulating JSON data.

> [!WARNING]  
> This project is in its early stages and is not yet ready for production use. The API may change, and there may be bugs. Use at your own risk.

## Installation

You can install `abstra-json-sql` using pip:

```sh
pip install abstra-json-sql
```

## Usage

### Command Line Interface

Assuming you have a directory structure like this:

```
.
├── organizations.json
├── projects.json
└── users.json
```

#### Querying Data

You can query the JSON files using SQL syntax. For example, to get all users from the `users` file, you can run:

```sh
abstra-json-sql "select * from users"
```

Or using the explicit query subcommand:

```sh
abstra-json-sql query --code "select * from users"
```

This will return all the users in the `users.json` file.

#### Interactive Mode

You can also run the CLI in interactive mode:

```sh
abstra-json-sql
```

This will start an interactive SQL prompt where you can type queries and see results immediately.

#### Creating Tables

You can create new tables interactively using the `create table` command:

```sh
abstra-json-sql create table --interactive
```

This will guide you through the process of creating a new table by asking for:
- Table name
- Column names and types (int, string, float, bool)
- Primary key designation
- Default values

The interactive table creation supports:
- **Column types**: `int`, `string`, `float`, `bool`
- **Primary keys**: Mark columns as primary keys during creation
- **Default values**: Set default values for columns
- **Validation**: Prevents duplicate table/column names and validates data types

#### Output Formats

You can specify the output format using the `--format` option:

```sh
abstra-json-sql "select * from users" --format csv
abstra-json-sql "select * from users" --format json
```

### Python API

You can also use `abstra-json-sql` in your Python code. Here's an example:

```python
from abstra_json_sql.eval import eval_sql
from abstra_json_sql.tables import InMemoryTables, Table, Column

code = "\n".join(
    [
        "select foo, count(*)",
        "from bar as baz",
        "where foo is not null",
        "group by foo",
        "having foo <> 2",
        "order by foo",
        "limit 1 offset 1",
    ]
)
tables = InMemoryTables(
    tables=[
        Table(
            name="bar",
            columns=[Column(name="foo", type="text")],
            data=[
                {"foo": 1},
                {"foo": 2},
                {"foo": 3},
                {"foo": 2},
                {"foo": None},
                {"foo": 3},
                {"foo": 1},
            ],
        )
    ],
)
ctx = {}
result = eval_sql(code=code, tables=tables, ctx=ctx)

print(result) # [{"foo": 3, "count": 2}]
```

## CLI Examples

### Basic Query
```sh
# Query all records from a table
abstra-json-sql "SELECT * FROM users"

# Query with conditions
abstra-json-sql "SELECT name, email FROM users WHERE age > 25"
```

### Interactive Table Creation
```sh
# Start interactive table creation
abstra-json-sql create table --interactive

# Example interaction:
# Table name: employees
# Column name: id
# Column type for 'id' (int/string/float/bool): int
# Is 'id' a primary key? (y/N): y
# Column name: name
# Column type for 'name' (int/string/float/bool): string
# Column name: salary
# Column type for 'salary' (int/string/float/bool): float
# Does 'salary' have a default value? (y/N): y
# Default value for 'salary': 0.0
# Column name: (press Enter to finish)
```

### Output Formats
```sh
# JSON output (default)
abstra-json-sql "SELECT * FROM users" --format json

# CSV output
abstra-json-sql "SELECT * FROM users" --format csv
```

### Working Directory
```sh
# Specify a different working directory
abstra-json-sql "SELECT * FROM users" --workdir /path/to/json/files
```
## Features

- **SQL Queries on JSON**: Run SQL queries directly on JSON files
- **Command Line Interface**: Easy-to-use CLI with multiple output formats
- **Interactive Mode**: Interactive SQL prompt for exploratory queries
- **Table Management**: Create and manage tables interactively
- **Multiple Output Formats**: Support for JSON and CSV output
- **Python API**: Use the library programmatically in your Python projects

## Supported SQL Syntax

- [x] `WITH`
    - [ ] `RECURSIVE`

- [ ] `SELECT`
    - [ ] `ALL`
    - [ ] `DISTINCT`
    - [x] `*`
    - [x] `FROM`
        - [x] `JOIN`
            - [x] `INNER JOIN`
            - [x] `LEFT JOIN`
            - [x] `RIGHT JOIN`
            - [x] `FULL JOIN`
            - [ ] `CROSS JOIN`
    - [x] `WHERE`
    - [x] `GROUP BY`
    - [x] `HAVING`
    - [ ] `WINDOW`
    - [x] `ORDER BY`
    - [x] `LIMIT`
    - [x] `OFFSET`
    - [ ] `FETCH`
    - [ ] `FOR`

- [x] `INSERT`
    - [x] `INTO`
    - [x] `VALUES`
    - [x] `DEFAULT`
    - [ ] `SELECT`
    - [x] `RETURNING`
- [x] `UPDATE`
- [x] `DELETE`

- [x] `CREATE`
    - [x] `TABLE` (via interactive CLI)
- [ ] `DROP`
- [ ] `ALTER`
