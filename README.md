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

You can query the JSON files using SQL syntax. For example, to get all users from the `users` file, you can run:

```sh
abstra-json-sql "select * from users"
```

This will return all the users in the `users.json` file.

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
- [ ] `UPDATE`
- [ ] `DELETE`

- [ ] `CREATE`
- [ ] `DROP`
- [ ] `ALTER`
