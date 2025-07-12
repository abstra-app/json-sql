import pytest
from .tables import (
    Column,
    ColumnType,
    Table,
    ForeignKey,
)


class TestColumnType:
    def test_from_value_int(self):
        assert ColumnType.from_value(42) == ColumnType.int

    def test_from_value_string(self):
        assert ColumnType.from_value("hello") == ColumnType.string

    def test_from_value_float(self):
        assert ColumnType.from_value(3.14) == ColumnType.float

    def test_from_value_bool(self):
        assert ColumnType.from_value(True) == ColumnType.bool

    def test_from_value_none(self):
        assert ColumnType.from_value(None) == ColumnType.null

    def test_from_value_unknown(self):
        assert ColumnType.from_value([1, 2, 3]) == ColumnType.unknown


class TestColumn:
    def test_column_creation(self):
        col = Column(name="id", type=ColumnType.int, is_primary_key=True)
        assert col.name == "id"
        assert col.type == ColumnType.int
        assert col.is_primary_key is True
        assert col.foreign_key is None
        assert col.default is None

    def test_column_with_foreign_key(self):
        fk = ForeignKey(table="users", column="id")
        col = Column(name="user_id", type=ColumnType.int, foreign_key=fk)
        assert col.foreign_key.table == "users"
        assert col.foreign_key.column == "id"

    def test_column_hash(self):
        col1 = Column(name="id", type=ColumnType.int)
        col2 = Column(name="id", type=ColumnType.int)
        assert hash(col1) == hash(col2)


class TestTable:
    def test_table_creation(self):
        columns = [
            Column(name="id", type=ColumnType.int, is_primary_key=True),
            Column(name="name", type=ColumnType.string),
        ]
        table = Table(name="users", columns=columns)
        assert table.name == "users"
        assert len(table.columns) == 2
        assert table.data == []

    def test_get_column(self):
        columns = [
            Column(name="id", type=ColumnType.int),
            Column(name="name", type=ColumnType.string),
        ]
        table = Table(name="users", columns=columns)

        col = table.get_column("id")
        assert col is not None
        assert col.name == "id"

        col = table.get_column("nonexistent")
        assert col is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
