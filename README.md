# abstra-json-sql

`abstra-json-sql` is a Python library that allows you to **run SQL queries on JSON data**. It is designed to be simple and easy to use, while providing powerful features for querying and manipulating JSON data.

## Usage

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

## Installation

You can install `abstra-json-sql` using pip:

```sh
pip install abstra-json-sql
```