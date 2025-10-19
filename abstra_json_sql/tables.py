import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, List, Optional, Type

from .string_utils import snake_case

if TYPE_CHECKING:
    from pydantic import BaseModel


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

    def to_dict(self) -> str:
        return {
            "type": self.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ColumnType":
        """Create ColumnType from dictionary"""
        if "type" in data:
            return cls(data["type"])
        else:
            raise ValueError("Invalid data for ColumnType: missing 'type' key")


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
        schema: ColumnType,
        is_primary_key: bool = False,
        foreign_key: Optional[ForeignKey] = None,
        default: Optional[Any] = None,
        column_id: str = None,
    ):
        self.name = name
        self.schema = schema
        self.is_primary_key = is_primary_key
        self.foreign_key = foreign_key
        self.default = default
        self.column_id = column_id if column_id is not None else str(uuid.uuid4())

    def __hash__(self):
        # Only hash based on name and type for backward compatibility
        return hash((self.name, self.schema, self.is_primary_key, self.foreign_key))

    def __eq__(self, other):
        if not isinstance(other, Column):
            return False
        return (
            self.name == other.name
            and self.schema == other.schema
            and self.is_primary_key == other.is_primary_key
            and self.foreign_key == other.foreign_key
        )

    def to_dict(self):
        """Convert column to dictionary for serialization"""
        result = {
            "id": self.column_id,
            "name": self.name,
            "schema": self.schema.to_dict(),
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
        if "schema" in col_dict:
            col_dict["schema"] = ColumnType.from_dict(col_dict["schema"])
        # Convert foreign_key dict back to ForeignKey object
        if "foreign_key" in col_dict and col_dict["foreign_key"] is not None:
            fk_data = col_dict.pop("foreign_key")
            col_dict["foreign_key"] = ForeignKey(fk_data["table"], fk_data["column"])
        return cls(**col_dict)

    @classmethod
    def from_pydantic_field(cls, name: str, field) -> "Column":
        """Create Column object from Pydantic field (Pydantic v2 compatible)"""
        pk = False
        fk = None
        if hasattr(field, "json_schema_extra") and field.json_schema_extra:
            pk = field.json_schema_extra.get("primary_key", False)
            fk = field.json_schema_extra.get("foreign_key")
        return cls(
            name=snake_case(name),
            schema=ColumnType.from_value(field.annotation),
            is_primary_key=pk,
            foreign_key=fk,
            default=field.default,
        )


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

    @classmethod
    def from_pydantic_base_model(
        cls, model: Type["BaseModel"], table_name: str = None
    ) -> "Table":
        """Create Table object from Pydantic BaseModel"""
        name = table_name if table_name is not None else snake_case(model.__name__)
        return cls(
            name=name,
            columns=[
                Column.from_pydantic_field(name, field)
                for name, field in model.model_fields.items()
            ],
            table_id=str(uuid.uuid4()),
        )


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

    def insert(self, table_name: str, row: dict):
        # Adapt Pydantic BaseModel to dict if needed
        try:
            from pydantic import BaseModel
        except ImportError:
            BaseModel = None
        if BaseModel is not None and isinstance(row, BaseModel):
            row = row.model_dump()
        return self._insert(table_name, row)

    @abstractmethod
    def _insert(self, table_name: str, row: dict):
        raise NotImplementedError("_insert method must be implemented")

    def update(self, table_name: str, idx: int, changes: dict):
        # Adapt Pydantic BaseModel to dict if needed
        try:
            from pydantic import BaseModel
        except ImportError:
            BaseModel = None
        if BaseModel is not None and isinstance(changes, BaseModel):
            changes = changes.model_dump()
        return self._update(table_name, idx, changes)

    @abstractmethod
    def _update(self, table_name: str, idx: int, changes: dict):
        raise NotImplementedError("_update method must be implemented")

    def delete(self, table_name: str, idxs: List[int]):
        return self._delete(table_name, idxs)

    @abstractmethod
    def _delete(self, table_name: str, idxs: List[int]):
        raise NotImplementedError("_delete method must be implemented")

    @classmethod
    def from_pydantic_base_models(
        cls, models: List[Type["BaseModel"]], table_name: str = None
    ) -> "ITablesSnapshot":
        """Create ITablesSnapshot from a list of Pydantic BaseModels"""
        tables = [Table.from_pydantic_base_model(model, table_name) for model in models]
        snapshot = cls()
        for table in tables:
            snapshot.add_table(table)
        return snapshot


__all__ = [
    "ColumnType",
    "ForeignKey",
    "Column",
    "Table",
    "ITablesSnapshot",
]
