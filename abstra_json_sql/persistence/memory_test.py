from unittest import TestCase

import pytest

from ..tables import Column, ColumnType, Table
from .memory import InMemoryTables


class InMemoryTablesTest(TestCase):
    def test_insert(self):
        tables = InMemoryTables(tables=[Table(name="test_table", columns=[], data=[])])
        tables.insert("test_table", {"id": 1, "name": "Test"})
        self.assertEqual(len(tables.get_table("test_table").data), 1)

    def test_update(self):
        tables = InMemoryTables(
            tables=[
                {
                    "name": "test_table",
                    "columns": [],
                    "data": [{"id": 1, "name": "Test"}],
                }
            ]
        )
        tables.update("test_table", 0, {"name": "Updated Test"})
        self.assertEqual(tables.get_table("test_table").data[0]["name"], "Updated Test")

    def test_delete(self):
        tables = InMemoryTables(
            tables=[
                {
                    "name": "test_table",
                    "columns": [],
                    "data": [{"id": 1, "name": "Test"}],
                }
            ]
        )
        tables.delete("test_table", [0])
        self.assertEqual(len(tables.get_table("test_table").data), 0)


class TestInMemoryTables:
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

    @pytest.fixture
    def tables(self):
        return InMemoryTables(tables=[])

    def test_add_table(self, tables, sample_table):
        tables.add_table(sample_table)
        assert len(tables.tables) == 1
        assert tables.tables[0].name == "users"

    def test_add_duplicate_table(self, tables, sample_table):
        tables.add_table(sample_table)
        with pytest.raises(ValueError, match="Table users already exists"):
            tables.add_table(sample_table)

    def test_get_table(self, tables, sample_table):
        tables.add_table(sample_table)
        retrieved = tables.get_table("users")
        assert retrieved is not None
        assert retrieved.name == "users"
        assert len(retrieved.data) == 2

    def test_get_nonexistent_table(self, tables):
        assert tables.get_table("nonexistent") is None

    def test_remove_table(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.remove_table("users")
        assert len(tables.tables) == 0

    def test_rename_table(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.rename_table("users", "people")
        assert tables.get_table("users") is None
        assert tables.get_table("people") is not None

    def test_rename_nonexistent_table(self, tables):
        with pytest.raises(ValueError, match="Table nonexistent not found"):
            tables.rename_table("nonexistent", "new_name")

    def test_rename_to_existing_table(self, tables, sample_table):
        tables.add_table(sample_table)
        other_table = Table(name="other", columns=[], data=[])
        tables.add_table(other_table)
        with pytest.raises(ValueError, match="Table other already exists"):
            tables.rename_table("users", "other")

    def test_add_column(self, tables, sample_table):
        tables.add_table(sample_table)
        new_column = Column(name="email", schema=ColumnType.string)
        tables.add_column("users", new_column)

        table = tables.get_table("users")
        assert len(table.columns) == 4
        assert table.get_column("email") is not None

    def test_add_duplicate_column(self, tables, sample_table):
        tables.add_table(sample_table)
        duplicate_column = Column(name="name", schema=ColumnType.string)
        with pytest.raises(ValueError, match="Column name already exists"):
            tables.add_column("users", duplicate_column)

    def test_remove_column(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.remove_column("users", "age")

        table = tables.get_table("users")
        assert len(table.columns) == 2
        assert table.get_column("age") is None

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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
