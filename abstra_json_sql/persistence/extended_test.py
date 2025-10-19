import pytest

from ..tables import Column, ColumnType, Table
from .extended import ExtendedTables
from .memory import InMemoryTables


class TestExtendedTables:
    @pytest.fixture
    def base_tables(self):
        return InMemoryTables(tables=[])

    @pytest.fixture
    def extra_table(self):
        return Table(
            name="extra",
            columns=[Column(name="id", schema=ColumnType.int)],
            data=[{"id": 1}],
        )

    def test_extended_tables_creation(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        assert extended.snapshot == base_tables
        assert len(extended.extra_tables) == 1

    def test_get_table_from_base(self, base_tables, extra_table):
        base_table = Table(
            name="base", columns=[Column(name="id", schema=ColumnType.int)], data=[]
        )
        base_tables.add_table(base_table)

        extended = ExtendedTables(base_tables, [extra_table])
        retrieved = extended.get_table("base")
        assert retrieved is not None
        assert retrieved.name == "base"

    def test_get_table_from_extra(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        retrieved = extended.get_table("extra")
        assert retrieved is not None
        assert retrieved.name == "extra"

    def test_get_nonexistent_table(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        assert extended.get_table("nonexistent") is None

    def test_add_table(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        new_table = Table(
            name="new", columns=[Column(name="id", schema=ColumnType.int)], data=[]
        )
        extended.add_table(new_table)

        assert len(extended.extra_tables) == 2
        assert extended.get_table("new") is not None

    def test_remove_table(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        extended.remove_table("extra")

        assert len(extended.extra_tables) == 0
        assert extended.get_table("extra") is None

    def test_insert_extra_table(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        extended.insert("extra", {"id": 2})

        table = extended.get_table("extra")
        assert len(table.data) == 2

    def test_update_extra_table(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        extended.update("extra", 0, {"id": 999})

        table = extended.get_table("extra")
        assert table.data[0]["id"] == 999

    def test_delete_extra_table(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        extended.delete("extra", [0])

        table = extended.get_table("extra")
        assert len(table.data) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
