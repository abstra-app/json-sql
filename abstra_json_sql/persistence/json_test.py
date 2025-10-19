import json
import tempfile
from pathlib import Path

import pytest

from ..tables import Column, ColumnType, Table
from .base_test import FsTablesTest
from .json import FileSystemJsonTables


class FileSystemJsonTablesTest(FsTablesTest):
    def test_insert(self):
        tables = FileSystemJsonTables(workdir=self.path)
        tables.insert("test_table", {"id": 1, "name": "Test"})
        self.assertEqual(len(tables.get_table("test_table").data), 1)

    def test_update(self):
        tables = FileSystemJsonTables(workdir=self.path)
        tables.insert("test_table", {"id": 1, "name": "Test"})
        tables.update("test_table", 0, {"name": "Updated Test"})
        self.assertEqual(tables.get_table("test_table").data[0]["name"], "Updated Test")

    def test_delete(self):
        tables = FileSystemJsonTables(workdir=self.path)
        tables.insert("test_table", {"id": 1, "name": "Test"})
        tables.delete("test_table", [0])
        self.assertEqual(len(tables.get_table("test_table").data), 0)


class TestFileSystemJsonTables:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def tables(self, temp_dir):
        return FileSystemJsonTables(temp_dir)

    @pytest.fixture
    def sample_table(self):
        return Table(
            name="users",
            columns=[
                Column(name="id", schema=ColumnType.int, is_primary_key=True),
                Column(name="name", schema=ColumnType.string),
                Column(name="age", schema=ColumnType.int),
            ],
            data=[
                {"id": 1, "name": "Alice", "age": 30},
                {"id": 2, "name": "Bob", "age": 25},
            ],
        )

    def test_metadata_table_creation(self, tables, temp_dir):
        assert (temp_dir / "__schema__.json").exists()
        metadata = json.loads((temp_dir / "__schema__.json").read_text())
        assert metadata == {}

    def test_add_table(self, tables, sample_table, temp_dir):
        tables.add_table(sample_table)

        # Check data file exists with UUID name
        table_id = sample_table.table_id
        assert (temp_dir / f"{table_id}.json").exists()

        # Check metadata is saved
        metadata = json.loads((temp_dir / "__schema__.json").read_text())
        assert table_id in metadata
        assert metadata[table_id]["table_name"] == "users"
        assert len(metadata[table_id]["columns"]) == 3

    def test_add_duplicate_table(self, tables, sample_table, temp_dir):
        tables.add_table(sample_table)
        with pytest.raises(ValueError, match="Table users already exists"):
            tables.add_table(sample_table)

    def test_get_table(self, tables, sample_table):
        tables.add_table(sample_table)
        retrieved = tables.get_table("users")
        assert retrieved.name == "users"
        assert len(retrieved.data) == 2
        assert len(retrieved.columns) == 3

    def test_get_nonexistent_table(self, tables):
        with pytest.raises(FileNotFoundError):
            tables.get_table("nonexistent")

    def test_remove_table(self, tables, sample_table, temp_dir):
        tables.add_table(sample_table)
        table_id = sample_table.table_id

        # Verify file exists before removal
        assert (temp_dir / f"{table_id}.json").exists()

        tables.remove_table("users")

        # File should be removed
        assert not (temp_dir / f"{table_id}.json").exists()

        # Metadata should be removed
        metadata = json.loads((temp_dir / "__schema__.json").read_text())
        assert table_id not in metadata

    def test_rename_table(self, tables, sample_table, temp_dir):
        tables.add_table(sample_table)
        table_id = sample_table.table_id

        tables.rename_table("users", "people")

        # File name should stay the same (UUID-based)
        assert (temp_dir / f"{table_id}.json").exists()

        # Metadata should reflect the new table name
        metadata = json.loads((temp_dir / "__schema__.json").read_text())
        assert table_id in metadata
        assert metadata[table_id]["table_name"] == "people"

    def test_add_column(self, tables, sample_table):
        tables.add_table(sample_table)
        new_column = Column(
            name="email", schema=ColumnType.string, default="test@example.com"
        )
        tables.add_column("users", new_column)

        table = tables.get_table("users")
        assert len(table.columns) == 4
        assert table.get_column("email") is not None
        # Check that default value was added to existing rows
        assert all(row["email"] == "test@example.com" for row in table.data)

    def test_remove_column(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.remove_column("users", "age")

        table = tables.get_table("users")
        assert len(table.columns) == 2
        assert table.get_column("age") is None
        # Check that column was removed from data
        assert all("age" not in row for row in table.data)

    def test_rename_column(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.rename_column("users", "age", "years")

        table = tables.get_table("users")
        assert table.get_column("age") is None
        assert table.get_column("years") is not None
        # Check that column was renamed in data
        assert all("age" not in row and "years" in row for row in table.data)

    def test_change_column_type(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.change_column_type("users", "age", ColumnType.string)

        table = tables.get_table("users")
        age_col = table.get_column("age")
        assert age_col.schema == ColumnType.string

    def test_insert(self, tables, sample_table):
        tables.add_table(sample_table)
        new_row = {"id": 3, "name": "Charlie", "age": 35}
        tables.insert("users", new_row)

        table = tables.get_table("users")
        assert len(table.data) == 3
        assert table.data[2] == new_row

    def test_update(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.update("users", 0, {"name": "Alice Updated"})

        table = tables.get_table("users")
        assert table.data[0]["name"] == "Alice Updated"

    def test_delete(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.delete("users", [0])

        table = tables.get_table("users")
        assert len(table.data) == 1
        assert table.data[0]["name"] == "Bob"


def test_new_uuid_implementation():
    """Test the new UUID-based file naming implementation"""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create tables instance
        tables = FileSystemJsonTables(workdir=temp_path)

        # Create a sample table
        table = Table(
            name="users",
            columns=[
                Column(name="id", schema=ColumnType.int, is_primary_key=True),
                Column(name="name", schema=ColumnType.string),
            ],
            data=[
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ],
        )

        # Add the table
        tables.add_table(table)

        # Check that the UUID-named file exists
        table_file = temp_path / f"{table.table_id}.json"
        assert table_file.exists()

        # Check schema file
        schema_file = temp_path / "__schema__.json"
        assert schema_file.exists()

        schema_content = json.loads(schema_file.read_text())
        assert table.table_id in schema_content
        assert schema_content[table.table_id]["table_name"] == "users"

        # Try to retrieve the table
        retrieved_table = tables.get_table("users")
        assert retrieved_table.name == "users"
        assert retrieved_table.table_id == table.table_id
        assert retrieved_table.data == [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]

        # Test insert
        tables.insert("users", {"id": 3, "name": "Charlie"})

        # Retrieve again
        updated_table = tables.get_table("users")
        assert len(updated_table.data) == 3
        assert updated_table.data[2] == {"id": 3, "name": "Charlie"}


def test_uuid_file_names_and_rename():
    """Test UUID-based file naming and table rename behavior"""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create tables instance
        tables = FileSystemJsonTables(workdir=temp_path)

        # Create a sample table
        table = Table(
            name="users",
            columns=[
                Column(name="id", schema=ColumnType.int, is_primary_key=True),
                Column(name="name", schema=ColumnType.string),
            ],
            data=[
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ],
        )

        # Add the table
        tables.add_table(table)

        # Verify initial files
        uuid_file = temp_path / f"{table.table_id}.json"
        schema_file = temp_path / "__schema__.json"

        assert uuid_file.exists()
        assert schema_file.exists()

        # Check schema content
        schema_content = json.loads(schema_file.read_text())
        assert table.table_id in schema_content
        assert schema_content[table.table_id]["table_name"] == "users"
        assert len(schema_content[table.table_id]["columns"]) == 2

        # Test rename
        tables.rename_table("users", "people")

        # File name should stay the same (UUID-based)
        assert uuid_file.exists()

        # Schema content should reflect the new table name
        schema_content_after = json.loads(schema_file.read_text())
        assert table.table_id in schema_content_after
        assert schema_content_after[table.table_id]["table_name"] == "people"

        # Should be able to retrieve by new name
        retrieved_table = tables.get_table("people")
        assert retrieved_table.name == "people"
        assert retrieved_table.table_id == table.table_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
