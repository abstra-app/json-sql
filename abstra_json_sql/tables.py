from typing import Any, List, Optional
from abc import ABC, abstractmethod
from enum import Enum
import uuid
from .persistence import (
    InMemoryTables,
    FileSystemJsonTables,
    FileSystemJsonLTables,
    ExtendedTables,
)


class ColumnType(Enum):
    int = "int"
    string = "string"
    float = "float"
    bool = "bool"
    null = "null"
    unknown = "unknown"

    def from_value(value: Any) -> "ColumnType":
        if isinstance(
            value, bool
        ):  # Check bool first since bool is a subclass of int in Python
            return ColumnType.bool
        elif isinstance(value, int):
            return ColumnType.int
        elif isinstance(value, str):
            return ColumnType.string
        elif isinstance(value, float):
            return ColumnType.float
        elif value is None:
            return ColumnType.null
        else:
            return ColumnType.unknown


class ForeignKey:
    def __init__(self, table: str, column: str):
        self.table = table
        self.column = column

    def __eq__(self, other):
        if not isinstance(other, ForeignKey):
            return False
        return self.table == other.table and self.column == other.column

    def __hash__(self):
        return hash((self.table, self.column))


class Column:
    def __init__(
        self,
        name: str,
        type: ColumnType,
        is_primary_key: bool = False,
        foreign_key: Optional[ForeignKey] = None,
        default: Optional[Any] = None,
        column_id: str = None,
    ):
        self.name = name
        self.type = type
        self.is_primary_key = is_primary_key
        self.foreign_key = foreign_key
        self.default = default
        self.column_id = column_id if column_id is not None else str(uuid.uuid4())

    def __hash__(self):
        # Only hash based on name and type for backward compatibility
        return hash((self.name, self.type, self.is_primary_key, self.foreign_key))

    def __eq__(self, other):
        if not isinstance(other, Column):
            return False
        return (
            self.name == other.name
            and self.type == other.type
            and self.is_primary_key == other.is_primary_key
            and self.foreign_key == other.foreign_key
        )

    def to_dict(self):
        """Convert column to dictionary for serialization"""
        result = {
            "id": self.column_id,
            "name": self.name,
            "type": self.type.value if isinstance(self.type, ColumnType) else self.type,
            "is_primary_key": self.is_primary_key,
            "default": self.default,
        }
        if self.foreign_key:
            result["foreign_key"] = {
                "table": self.foreign_key.table,
                "column": self.foreign_key.column,
            }
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Column":
        """Create Column object from dictionary"""
        col_dict = data.copy()
        # Handle legacy format without 'id' field
        if "id" in col_dict:
            col_dict["column_id"] = col_dict.pop("id")
        # Convert type string back to ColumnType enum
        if "type" in col_dict:
            col_dict["type"] = ColumnType(col_dict["type"])
        # Convert foreign_key dict back to ForeignKey object
        if "foreign_key" in col_dict and col_dict["foreign_key"] is not None:
            fk_data = col_dict.pop("foreign_key")
            col_dict["foreign_key"] = ForeignKey(fk_data["table"], fk_data["column"])
        return cls(**col_dict)


class Table:
    def __init__(
        self,
        name: str,
        columns: List[Column],
        data: List[dict] = None,
        table_id: str = None,
    ):
        self.name = name
        self.columns = columns
        self.data = data if data is not None else []
        self.table_id = table_id if table_id is not None else str(uuid.uuid4())

    def get_column(self, name: str) -> Optional[Column]:
        for column in self.columns:
            if column.name == name:
                return column
        return None

    def get_column_by_id(self, column_id: str) -> Optional[Column]:
        for column in self.columns:
            if column.column_id == column_id:
                return column
        return None

    def convert_row_to_column_ids(self, row: dict) -> dict:
        """Convert a row from column names to column IDs"""
        result = {}
        for col_name, value in row.items():
            col = self.get_column(col_name)
            if col:
                result[col.column_id] = value
            else:
                # If column not found by name, try to treat it as ID (for backward compatibility)
                result[col_name] = value
        return result

    def convert_row_from_column_ids(self, row: dict) -> dict:
        """Convert a row from column IDs to column names"""
        result = {}
        for col_id, value in row.items():
            col = self.get_column_by_id(col_id)
            if col:
                result[col.name] = value
            else:
                # If column not found by ID, try to treat it as name (for backward compatibility)
                result[col_id] = value
        return result


class ITablesSnapshot(ABC):
    @abstractmethod
    def get_table(self, name: str) -> Optional[Table]:
        raise NotImplementedError("get_table method must be implemented")

    @abstractmethod
    def add_table(self, table: Table):
        raise NotImplementedError("add_table method must be implemented")

    @abstractmethod
    def remove_table(self, name: str):
        raise NotImplementedError("remove_table method must be implemented")

    @abstractmethod
    def rename_table(self, old_name: str, new_name: str):
        raise NotImplementedError("rename_table method must be implemented")

    @abstractmethod
    def add_column(self, table_name: str, column: Column):
        raise NotImplementedError("add_column method must be implemented")

    @abstractmethod
    def remove_column(self, table_name: str, column_name: str):
        raise NotImplementedError("remove_column method must be implemented")

    @abstractmethod
    def rename_column(self, table_name: str, old_name: str, new_name: str):
        raise NotImplementedError("rename_column method must be implemented")

    @abstractmethod
    def change_column_type(
        self, table_name: str, column_name: str, new_type: ColumnType
    ):
        raise NotImplementedError("change_column_type method must be implemented")

    @abstractmethod
    def insert(self, table_name: str, row: dict):
        raise NotImplementedError("insert method must be implemented")

    @abstractmethod
    def update(self, table_name: str, idx: int, changes: dict):
        raise NotImplementedError("update method must be implemented")

    @abstractmethod
    def delete(self, table_name: str, idxs: List[int]):
        raise NotImplementedError("delete method must be implemented")


__all__ = [
    "ColumnType",
    "ForeignKey",
    "Column",
    "Table",
    "ITablesSnapshot",
    "InMemoryTables",
    "FileSystemJsonTables",
    "FileSystemJsonLTables",
    "ExtendedTables",
]
