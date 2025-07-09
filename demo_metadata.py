#!/usr/bin/env python3
"""
Demonstration of the new metadata system for JSON and JSONL tables
"""

import tempfile
import json
from pathlib import Path
from abstra_json_sql.tables import (
    Column, ColumnType, Table, 
    FileSystemJsonTables, FileSystemJsonLTables
)

def demonstrate_json_tables():
    print("=== FileSystemJsonTables with metadata.json ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        tables = FileSystemJsonTables(temp_path)
        
        # Create a sample table
        user_table = Table(
            name="users",
            columns=[
                Column(name="id", type=ColumnType.int, is_primary_key=True),
                Column(name="name", type=ColumnType.string),
                Column(name="email", type=ColumnType.string),
                Column(name="age", type=ColumnType.int)
            ],
            data=[
                {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30},
                {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 25}
            ]
        )
        
        # Add table
        tables.add_table(user_table)
        
        print(f"Created table: {user_table.name}")
        print(f"Data file: {temp_path / 'users.json'}")
        print(f"Metadata file: {temp_path / 'metadata.json'}")
        
        # Show metadata content
        metadata_content = json.loads((temp_path / "metadata.json").read_text())
        print(f"Metadata content: {json.dumps(metadata_content, indent=2)}")
        
        # Add a new column
        new_column = Column(name="active", type=ColumnType.bool, default=True)
        tables.add_column("users", new_column)
        print(f"\nAdded column: {new_column.name}")
        
        # Show updated metadata
        metadata_content = json.loads((temp_path / "metadata.json").read_text())
        print(f"Updated metadata: {json.dumps(metadata_content, indent=2)}")
        
        # Retrieve table to verify
        retrieved_table = tables.get_table("users")
        print(f"\nRetrieved table columns: {[col.name for col in retrieved_table.columns]}")
        print(f"First row: {retrieved_table.data[0]}")

def demonstrate_jsonl_tables():
    print("\n=== FileSystemJsonLTables with metadata.jsonl ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        tables = FileSystemJsonLTables(temp_path)
        
        # Create a sample table
        product_table = Table(
            name="products",
            columns=[
                Column(name="id", type=ColumnType.int, is_primary_key=True),
                Column(name="name", type=ColumnType.string),
                Column(name="price", type=ColumnType.float)
            ],
            data=[
                {"id": 1, "name": "Widget", "price": 19.99},
                {"id": 2, "name": "Gadget", "price": 29.99}
            ]
        )
        
        # Add table
        tables.add_table(product_table)
        
        print(f"Created table: {product_table.name}")
        print(f"Data file: {temp_path / 'products.jsonl'}")
        print(f"Metadata file: {temp_path / 'metadata.jsonl'}")
        
        # Show metadata content
        with (temp_path / "metadata.jsonl").open("r") as f:
            metadata_line = f.readline().strip()
            metadata_content = json.loads(metadata_line)
        print(f"Metadata content: {json.dumps(metadata_content, indent=2)}")
        
        # Rename a column
        tables.rename_column("products", "price", "unit_price")
        print("\nRenamed column: price -> unit_price")
        
        # Show updated metadata
        with (temp_path / "metadata.jsonl").open("r") as f:
            metadata_line = f.readline().strip()
            metadata_content = json.loads(metadata_line)
        print(f"Updated metadata: {json.dumps(metadata_content, indent=2)}")
        
        # Retrieve table to verify
        retrieved_table = tables.get_table("products")
        print(f"\nRetrieved table columns: {[col.name for col in retrieved_table.columns]}")
        print(f"First row: {retrieved_table.data[0]}")

if __name__ == "__main__":
    demonstrate_json_tables()
    demonstrate_jsonl_tables()
    print("\n=== All demonstrations completed successfully! ===")
