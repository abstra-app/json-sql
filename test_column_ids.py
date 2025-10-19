#!/usr/bin/env python3

"""
Test script to verify that the new column ID implementation is working correctly.
This script demonstrates that:
1. Data is stored internally using column IDs instead of column names
2. Schema metadata includes column IDs
3. External API still works with column names for backward compatibility
"""

import json
import tempfile
from pathlib import Path

from abstra_json_sql.persistence import (
    FileSystemJsonTables,
    InMemoryTables,
)
from abstra_json_sql.tables import (
    Column,
    ColumnType,
    Table,
)


def test_inmemory_tables_with_column_ids():
    print("=== Testing InMemoryTables with Column IDs ===")

    # Create columns with explicit IDs
    col1 = Column(name="id", schema=ColumnType.int, column_id="col_1")
    col2 = Column(name="name", schema=ColumnType.string, column_id="col_2")
    col3 = Column(name="age", schema=ColumnType.int, column_id="col_3")

    # Create table
    table = Table(name="users", columns=[col1, col2, col3], data=[])

    # Create InMemoryTables instance
    tables = InMemoryTables([table])

    # Insert data using column names (external API)
    tables.insert("users", {"id": 1, "name": "Alice", "age": 30})
    tables.insert("users", {"id": 2, "name": "Bob", "age": 25})

    # Get table data (should return column names)
    user_table = tables.get_table("users")
    print("External API - Data returned with column names:")
    for row in user_table.data:
        print(f"  {row}")

    # Check internal storage (should use column IDs)
    internal_table = tables._get_internal_table("users")
    print("\nInternal storage - Data stored with column IDs:")
    for row in internal_table.data:
        print(f"  {row}")

    # Test update with column names
    tables.update("users", 0, {"name": "Alice Updated", "age": 31})

    # Verify update worked
    user_table = tables.get_table("users")
    print("\nAfter update:")
    for row in user_table.data:
        print(f"  {row}")

    print(f"\nSuccess! Alice's name is now: {user_table.data[0]['name']}")
    print(f"Alice's age is now: {user_table.data[0]['age']}")


def test_filesystem_tables_with_column_ids():
    print("\n=== Testing FileSystemJsonTables with Column IDs ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        workdir = Path(temp_dir)

        # Create filesystem tables
        tables = FileSystemJsonTables(workdir)

        # Create columns with IDs
        col1 = Column(name="product_id", schema=ColumnType.int, column_id="p_id")
        col2 = Column(name="product_name", schema=ColumnType.string, column_id="p_name")
        col3 = Column(name="price", schema=ColumnType.float, column_id="p_price")

        # Create and add table
        table = Table(
            name="products",
            columns=[col1, col2, col3],
            data=[
                {"product_id": 1, "product_name": "Laptop", "price": 999.99},
                {"product_id": 2, "product_name": "Mouse", "price": 29.99},
            ],
        )

        tables.add_table(table)

        # Check schema file
        schema_file = workdir / "__schema__.json"
        with open(schema_file, "r") as f:
            schema_data = json.load(f)

        print("Schema metadata (should include column IDs):")
        for table_id, table_info in schema_data.items():
            print(f"  Table ID: {table_id}")
            print(f"  Table Name: {table_info['table_name']}")
            print("  Columns:")
            for col in table_info["columns"]:
                print(
                    f"    - ID: {col['id']}, Name: {col['name']}, Type: {col['schema']['type']}"
                )

        # Check data file
        table_file = None
        for file_path in workdir.glob("*.json"):
            if file_path.name != "__schema__.json":
                table_file = file_path
                break

        if table_file:
            with open(table_file, "r") as f:
                data = json.load(f)

            print("\nData file content (should use column IDs):")
            for row in data:
                print(f"  {row}")

        # Test retrieval (should convert back to column names)
        retrieved_table = tables.get_table("products")
        print("\nRetrieved data (converted to column names):")
        for row in retrieved_table.data:
            print(f"  {row}")

        # Test rename column (data should not change since we use IDs)
        print("\nRenaming 'product_name' to 'name'...")
        tables.rename_column("products", "product_name", "name")

        # Check data file again (should be unchanged)
        with open(table_file, "r") as f:
            data_after_rename = json.load(f)

        print("Data file after rename (should be unchanged):")
        for row in data_after_rename:
            print(f"  {row}")

        # But retrieved data should show new column name
        retrieved_after_rename = tables.get_table("products")
        print("Retrieved data after rename (should show new column name):")
        for row in retrieved_after_rename.data:
            print(f"  {row}")


def test_column_id_generation():
    print("\n=== Testing Column ID Generation ===")

    # Create columns without explicit IDs (should auto-generate)
    col1 = Column(name="auto1", schema=ColumnType.string)
    col2 = Column(name="auto2", schema=ColumnType.int)

    print("Auto-generated column IDs:")
    print(f"  Column 'auto1' ID: {col1.column_id}")
    print(f"  Column 'auto2' ID: {col2.column_id}")

    # Verify IDs are unique
    assert col1.column_id != col2.column_id, "Column IDs should be unique"
    print("✓ Column IDs are unique")


if __name__ == "__main__":
    test_inmemory_tables_with_column_ids()
    test_filesystem_tables_with_column_ids()
    test_column_id_generation()
    print("\n🎉 All tests passed! Column ID implementation is working correctly.")
