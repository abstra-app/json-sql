from unittest import TestCase

import pytest

from .persistence import InMemoryTables
from .tables import (
    Column,
    ColumnType,
    ForeignKey,
    Table,
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
        col = Column(name="id", schema=ColumnType.int, is_primary_key=True)
        assert col.name == "id"
        assert col.schema == ColumnType.int
        assert col.is_primary_key is True
        assert col.foreign_key is None
        assert col.default is None

    def test_column_with_foreign_key(self):
        fk = ForeignKey(table="users", column="id")
        col = Column(name="user_id", schema=ColumnType.int, foreign_key=fk)
        assert col.foreign_key.table == "users"
        assert col.foreign_key.column == "id"

    def test_column_hash(self):
        col1 = Column(name="id", schema=ColumnType.int)
        col2 = Column(name="id", schema=ColumnType.int)
        assert hash(col1) == hash(col2)


class TestTable:
    def test_table_creation(self):
        columns = [
            Column(name="id", schema=ColumnType.int, is_primary_key=True),
            Column(name="name", schema=ColumnType.string),
        ]
        table = Table(name="users", columns=columns)
        assert table.name == "users"
        assert len(table.columns) == 2
        assert table.data == []

    def test_get_column(self):
        columns = [
            Column(name="id", schema=ColumnType.int),
            Column(name="name", schema=ColumnType.string),
        ]
        table = Table(name="users", columns=columns)

        col = table.get_column("id")
        assert col is not None
        assert col.name == "id"

        col = table.get_column("nonexistent")
        assert col is None


class TestFrom(TestCase):
    def test_from_pydantic_base_model(self):
        from pydantic import BaseModel, Field

        class UserModel(BaseModel):
            id: int = Field(..., primary_key=True)
            name: str

        table = Table.from_pydantic_base_model(UserModel)
        assert table.name == "user_model"
        assert len(table.columns) == 2
        assert table.columns[0].name == "id"
        assert table.columns[0].is_primary_key is True
        assert table.columns[1].name == "name"

    def test_from_pydantic_base_model_with_table_name(self):
        from pydantic import BaseModel, Field

        class UserModel(BaseModel):
            id: int = Field(..., primary_key=True)
            name: str

        table = Table.from_pydantic_base_model(UserModel, table_name="custom_table")
        assert table.name == "custom_table"
        assert len(table.columns) == 2
        assert table.columns[0].name == "id"
        assert table.columns[0].is_primary_key is True
        assert table.columns[1].name == "name"

    def test_in_memory_from_pydantic_base_models(self):
        from pydantic import BaseModel, Field

        class UserModel(BaseModel):
            id: int = Field(..., primary_key=True)
            name: str

        class ProductModel(BaseModel):
            id: int = Field(..., primary_key=True)
            title: str

        snapshot = InMemoryTables.from_pydantic_base_models([UserModel, ProductModel])
        assert len(snapshot.tables) == 2
        assert snapshot.tables[0].name == "user_model"
        assert snapshot.tables[1].name == "product_model"

        snapshot.insert("user_model", {"id": 1, "name": "Alice"})

        with self.assertRaises(ValueError):
            snapshot.insert("nonexistent_table", {"id": 1, "name": "Alice"})

        user2 = UserModel(id=2, name="Bob")
        snapshot.insert("user_model", user2)
        assert len(snapshot.get_table("user_model").data) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
