from typing import Any, List, Optional
from pathlib import Path
from abc import ABC, abstractmethod
import json
from enum import Enum
import uuid


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
            fk_data = col_dict["foreign_key"]
            col_dict["foreign_key"] = ForeignKey(
                table=fk_data["table"], column=fk_data["column"]
            )
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
                # If column not found, keep original name (for backward compatibility)
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


class InMemoryTables(ITablesSnapshot):
    def __init__(self, tables: List[Table] = None):
        if tables is None:
            self.tables = []
        else:
            self.tables = []
            for table in tables:
                if isinstance(table, dict):
                    # Convert dict to Table object for backward compatibility
                    columns = []
                    for col_data in table.get("columns", []):
                        if isinstance(col_data, dict):
                            columns.append(Column.from_dict(col_data))
                        else:
                            columns.append(col_data)

                    new_table = Table(
                        name=table["name"],
                        columns=columns,
                        data=[],  # Start with empty data
                        table_id=table.get("table_id"),
                    )

                    # Convert data to column ID format
                    for row in table.get("data", []):
                        converted_row = new_table.convert_row_to_column_ids(row)
                        new_table.data.append(converted_row)

                    self.tables.append(new_table)
                else:
                    # Convert existing table data to column ID format if needed
                    converted_data = []
                    for row in table.data:
                        converted_row = table.convert_row_to_column_ids(row)
                        converted_data.append(converted_row)
                    table.data = converted_data
                    self.tables.append(table)

    def get_table(self, name: str) -> Optional[Table]:
        for table in self.tables:
            if table.name == name:
                # Create a copy with data converted to column names
                converted_data = []
                for row in table.data:
                    converted_data.append(table.convert_row_from_column_ids(row))

                result_table = Table(
                    name=table.name,
                    columns=table.columns,
                    data=converted_data,
                    table_id=table.table_id,
                )
                return result_table
        return None

    def _get_internal_table(self, name: str) -> Optional[Table]:
        """Get the internal table object (with column ID data format)"""
        for table in self.tables:
            if table.name == name:
                return table
        return None

    def add_table(self, table: Table):
        if self.get_table(table.name) is not None:
            raise ValueError(f"Table {table.name} already exists")
        self.tables.append(table)

    def remove_table(self, name: str):
        self.tables = [table for table in self.tables if table.name != name]

    def rename_table(self, old_name: str, new_name: str):
        table = self._get_internal_table(old_name)
        if table is None:
            raise ValueError(f"Table {old_name} not found")
        if self._get_internal_table(new_name) is not None:
            raise ValueError(f"Table {new_name} already exists")
        table.name = new_name

    def add_column(self, table_name: str, column: Column):
        table = self._get_internal_table(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} not found")
        if table.get_column(column.name) is not None:
            raise ValueError(
                f"Column {column.name} already exists in table {table_name}"
            )
        table.columns.append(column)
        # Add default value to existing rows using column ID
        for row in table.data:
            row[column.column_id] = column.default

    def remove_column(self, table_name: str, column_name: str):
        table = self._get_internal_table(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} not found")
        # Find the column to get its ID before removing
        column_to_remove = table.get_column(column_name)
        if column_to_remove:
            # Remove from data using column ID
            for row in table.data:
                row.pop(column_to_remove.column_id, None)
        table.columns = [col for col in table.columns if col.name != column_name]

    def rename_column(self, table_name: str, old_name: str, new_name: str):
        table = self._get_internal_table(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} not found")
        column = table.get_column(old_name)
        if column is None:
            raise ValueError(f"Column {old_name} not found in table {table_name}")
        column.name = new_name

    def change_column_type(
        self, table_name: str, column_name: str, new_type: ColumnType
    ):
        table = self._get_internal_table(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} not found")
        column = table.get_column(column_name)
        if column is None:
            raise ValueError(f"Column {column_name} not found in table {table_name}")
        column.type = new_type

    def insert(self, table: str, row: dict):
        table_obj = self._get_internal_table(table)
        if table_obj is None:
            raise ValueError(f"Table {table} not found")
        # Convert row from column names to column IDs
        row_with_ids = table_obj.convert_row_to_column_ids(row)
        table_obj.data.append(row_with_ids)

    def update(self, table: str, idx: int, changes: dict):
        table_obj = self._get_internal_table(table)
        # Convert changes from column names to column IDs
        changes_with_ids = table_obj.convert_row_to_column_ids(changes)
        table_obj.data[idx].update(changes_with_ids)

    def delete(self, table: str, idxs: List[int]):
        table_obj = self._get_internal_table(table)
        if table_obj is None:
            raise ValueError(f"Table {table} not found")
        table_obj.data = [row for i, row in enumerate(table_obj.data) if i not in idxs]


class FileSystemJsonTables(ITablesSnapshot):
    workdir: Path

    def __init__(self, workdir: Path):
        self.workdir = workdir
        self._ensure_metadata_table()

    def _ensure_metadata_table(self):
        """Ensure the metadata table exists"""
        metadata_path = self.workdir / "__schema__.json"
        if not metadata_path.exists():
            metadata_path.write_text(json.dumps({}))

    def _get_table_metadata_by_name(
        self, table_name: str
    ) -> tuple[Optional[str], Optional[List[Column]]]:
        """Get table metadata (id and columns) by table name from the __schema__.json file"""
        metadata_path = self.workdir / "__schema__.json"
        metadata = json.loads(metadata_path.read_text())

        for table_id, table_info in metadata.items():
            if table_info.get("table_name") == table_name:
                columns = []
                for col_dict in table_info.get("columns", []):
                    columns.append(Column.from_dict(col_dict))
                return table_id, columns
        return None, None

    def _get_table_metadata_by_id(
        self, table_id: str
    ) -> tuple[Optional[str], Optional[List[Column]]]:
        """Get table metadata (name and columns) by table ID from the __schema__.json file"""
        metadata_path = self.workdir / "__schema__.json"
        metadata = json.loads(metadata_path.read_text())

        table_info = metadata.get(table_id)
        if table_info:
            columns = []
            for col_dict in table_info.get("columns", []):
                columns.append(Column.from_dict(col_dict))
            return table_info.get("table_name"), columns
        return None, None

    def _save_table_metadata(
        self, table_id: str, table_name: str, columns: List[Column]
    ):
        """Save table metadata to the __schema__.json file"""
        metadata_path = self.workdir / "__schema__.json"
        metadata = json.loads(metadata_path.read_text())

        # Convert Column objects to dicts with proper serialization
        column_dicts = []
        for col in columns:
            col_dict = col.to_dict()
            column_dicts.append(col_dict)

        metadata[table_id] = {"table_name": table_name, "columns": column_dicts}
        metadata_path.write_text(json.dumps(metadata, indent=2))

    def _remove_table_metadata(self, table_id: str):
        """Remove table metadata from the __schema__.json file"""
        metadata_path = self.workdir / "__schema__.json"
        metadata = json.loads(metadata_path.read_text())
        if table_id in metadata:
            del metadata[table_id]
        metadata_path.write_text(json.dumps(metadata, indent=2))

    def get_table(self, name: str) -> Optional[Table]:
        table_id, columns = self._get_table_metadata_by_name(name)
        if table_id is None:
            raise FileNotFoundError(f"Table {name} not found")

        table_path = self.workdir / f"{table_id}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        rows = json.loads(table_path.read_text())

        if not columns:
            # Fallback: infer columns from data if metadata doesn't exist
            columns_set = set()
            for row in rows:
                assert isinstance(row, dict), f"Row {row} is not a dictionary"
                for key, value in row.items():
                    if key not in [col.name for col in columns_set]:
                        col = Column(name=key, type=ColumnType.from_value(value))
                        columns_set.add(col)
            columns = list(columns_set)
            # Save inferred metadata
            self._save_table_metadata(table_id, name, columns)

        # Create table object for conversion purposes
        temp_table = Table(name=name, columns=columns, data=[], table_id=table_id)

        # Convert data from column IDs to column names
        converted_data = []
        for row in rows:
            converted_row = temp_table.convert_row_from_column_ids(row)
            converted_data.append(converted_row)

        return Table(name=name, columns=columns, data=converted_data, table_id=table_id)

    def add_table(self, table: Table):
        # Check if table name already exists
        existing_id, _ = self._get_table_metadata_by_name(table.name)
        if existing_id is not None:
            raise ValueError(f"Table {table.name} already exists")

        table_path = self.workdir / f"{table.table_id}.json"
        if table_path.exists():
            raise ValueError(f"Table with ID {table.table_id} already exists")

        # Convert data to column ID format before saving
        data_with_ids = []
        for row in table.data:
            row_with_ids = table.convert_row_to_column_ids(row)
            data_with_ids.append(row_with_ids)

        table_path.write_text(json.dumps(data_with_ids, indent=2))
        # Save columns metadata
        self._save_table_metadata(table.table_id, table.name, table.columns)

    def remove_table(self, name: str):
        table_id, _ = self._get_table_metadata_by_name(name)
        if table_id is None:
            raise ValueError(f"Table {name} not found")

        table_path = self.workdir / f"{table_id}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        table_path.unlink()
        self._remove_table_metadata(table_id)

    def rename_table(self, old_name: str, new_name: str):
        table_id, columns = self._get_table_metadata_by_name(old_name)
        if table_id is None:
            raise ValueError(f"Table {old_name} not found")

        # Check if new name already exists
        existing_id, _ = self._get_table_metadata_by_name(new_name)
        if existing_id is not None:
            raise ValueError(f"Table {new_name} already exists")

        # Update metadata with new name
        self._save_table_metadata(table_id, new_name, columns)

    def insert(self, table_name: str, row: dict):
        table_id, columns = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        table_path = self.workdir / f"{table_id}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        # Create temp table for conversion
        temp_table = Table(name=table_name, columns=columns, data=[], table_id=table_id)

        rows = json.loads(table_path.read_text())
        assert isinstance(
            rows, list
        ), f"File {table_path} does not contain a list of rows"

        # Convert row to column ID format
        row_with_ids = temp_table.convert_row_to_column_ids(row)
        rows.append(row_with_ids)
        table_path.write_text(json.dumps(rows, indent=2))

    def add_column(self, table_name: str, column: Column):
        table_id, existing_columns = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        table_path = self.workdir / f"{table_id}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        rows = json.loads(table_path.read_text())
        assert isinstance(
            rows, list
        ), f"File {table_path} does not contain a list of rows"

        # Check if column already exists
        if any(col.name == column.name for col in existing_columns):
            raise ValueError(
                f"Column {column.name} already exists in table {table_name}"
            )

        # Add column to data using column ID
        for row in rows:
            row[column.column_id] = column.default
        table_path.write_text(json.dumps(rows, indent=2))

        # Update metadata
        existing_columns.append(column)
        self._save_table_metadata(table_id, table_name, existing_columns)

    def remove_column(self, table_name: str, column_name: str):
        table_id, columns = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        table_path = self.workdir / f"{table_id}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        rows = json.loads(table_path.read_text())
        assert isinstance(
            rows, list
        ), f"File {table_path} does not contain a list of rows"

        # Remove column from data using column ID
        column_to_remove = None
        for col in columns:
            if col.name == column_name:
                column_to_remove = col
                break

        if column_to_remove:
            for row in rows:
                if column_to_remove.column_id in row:
                    del row[column_to_remove.column_id]
        table_path.write_text(json.dumps(rows, indent=2))

        # Update metadata
        columns = [col for col in columns if col.name != column_name]
        self._save_table_metadata(table_id, table_name, columns)

    def rename_column(self, table_name: str, old_name: str, new_name: str):
        table_id, columns = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        table_path = self.workdir / f"{table_id}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        rows = json.loads(table_path.read_text())
        assert isinstance(
            rows, list
        ), f"File {table_path} does not contain a list of rows"

        # Data doesn't need to change for rename_column since we use column IDs
        # Only metadata needs to be updated
        for col in columns:
            if col.name == old_name:
                col.name = new_name
        self._save_table_metadata(table_id, table_name, columns)

    def change_column_type(
        self, table_name: str, column_name: str, new_type: ColumnType
    ):
        table_id, columns = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        # Update metadata
        for col in columns:
            if col.name == column_name:
                col.type = new_type
                break
        else:
            raise ValueError(f"Column {column_name} not found in table {table_name}")
        self._save_table_metadata(table_id, table_name, columns)

    def update(self, table_name: str, idx: int, changes: dict):
        table_id, columns = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        table_path = self.workdir / f"{table_id}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        # Create temp table for conversion
        temp_table = Table(name=table_name, columns=columns, data=[], table_id=table_id)

        rows = json.loads(table_path.read_text())
        assert isinstance(
            rows, list
        ), f"File {table_path} does not contain a list of rows"
        if idx < 0 or idx >= len(rows):
            raise IndexError(f"Index {idx} out of range for table {table_name}")

        # Convert changes to column ID format
        changes_with_ids = temp_table.convert_row_to_column_ids(changes)
        rows[idx].update(changes_with_ids)
        table_path.write_text(json.dumps(rows, indent=2))

    def delete(self, table_name: str, idxs: List[int]):
        table_id, _ = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        table_path = self.workdir / f"{table_id}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        rows = json.loads(table_path.read_text())
        assert isinstance(
            rows, list
        ), f"File {table_path} does not contain a list of rows"

        # Sort indices in descending order to avoid index shifting
        for idx in sorted(idxs, reverse=True):
            if idx < 0 or idx >= len(rows):
                raise IndexError(f"Index {idx} out of range for table {table_name}")
            del rows[idx]
        table_path.write_text(json.dumps(rows, indent=2))


class FileSystemJsonLTables(ITablesSnapshot):
    workdir: Path

    def __init__(self, workdir: Path):
        self.workdir = workdir
        self._ensure_metadata_table()

    def _ensure_metadata_table(self):
        """Ensure the metadata table exists"""
        metadata_path = self.workdir / "__schema__.jsonl"
        self.workdir.mkdir(parents=True, exist_ok=True)
        if not metadata_path.exists():
            metadata_path.write_text("")

    def _get_table_metadata_by_name(
        self, table_name: str
    ) -> tuple[Optional[str], Optional[List[Column]]]:
        """Get table metadata (id and columns) by table name from the __schema__.jsonl file"""
        metadata_path = self.workdir / "__schema__.jsonl"
        if not metadata_path.exists():
            return None, None

        with metadata_path.open("r") as f:
            for line in f:
                if line.strip():
                    metadata_entry = json.loads(line.strip())
                    if metadata_entry.get("table_name") == table_name:
                        table_id = metadata_entry.get("table_id")
                        columns = []
                        for col_dict in metadata_entry.get("columns", []):
                            columns.append(Column.from_dict(col_dict))
                        return table_id, columns
        return None, None

    def _get_table_metadata_by_id(
        self, table_id: str
    ) -> tuple[Optional[str], Optional[List[Column]]]:
        """Get table metadata (name and columns) by table ID from the __schema__.jsonl file"""
        metadata_path = self.workdir / "__schema__.jsonl"
        if not metadata_path.exists():
            return None, None

        with metadata_path.open("r") as f:
            for line in f:
                if line.strip():
                    metadata_entry = json.loads(line.strip())
                    if metadata_entry.get("table_id") == table_id:
                        table_name = metadata_entry.get("table_name")
                        columns = []
                        for col_dict in metadata_entry.get("columns", []):
                            columns.append(Column.from_dict(col_dict))
                        return table_name, columns
        return None, None

    def _save_table_metadata(
        self, table_id: str, table_name: str, columns: List[Column]
    ):
        """Save table metadata to the __schema__.jsonl file"""
        metadata_path = self.workdir / "__schema__.jsonl"

        # Read existing metadata and filter out the current table
        existing_metadata = []
        if metadata_path.exists():
            with metadata_path.open("r") as f:
                for line in f:
                    if line.strip():
                        metadata_entry = json.loads(line.strip())
                        if (
                            metadata_entry.get("table_id") != table_id
                            and metadata_entry.get("table_name") != table_name
                        ):
                            existing_metadata.append(metadata_entry)

        # Add the new metadata entry
        column_dicts = []
        for col in columns:
            col_dict = col.to_dict()
            column_dicts.append(col_dict)

        new_entry = {
            "table_id": table_id,
            "table_name": table_name,
            "columns": column_dicts,
        }
        existing_metadata.append(new_entry)

        # Write all metadata back
        with metadata_path.open("w") as f:
            for entry in existing_metadata:
                f.write(json.dumps(entry) + "\n")

    def _remove_table_metadata(self, table_id: str):
        """Remove table metadata from the __schema__.jsonl file"""
        metadata_path = self.workdir / "__schema__.jsonl"
        if not metadata_path.exists():
            return

        # Read existing metadata and filter out the table to remove
        remaining_metadata = []
        with metadata_path.open("r") as f:
            for line in f:
                if line.strip():
                    metadata_entry = json.loads(line.strip())
                    if metadata_entry.get("table_id") != table_id:
                        remaining_metadata.append(metadata_entry)

        # Write remaining metadata back
        with metadata_path.open("w") as f:
            for entry in remaining_metadata:
                f.write(json.dumps(entry) + "\n")

    def get_table(self, name: str) -> Optional[Table]:
        table_id, columns = self._get_table_metadata_by_name(name)
        if table_id is None:
            raise FileNotFoundError(f"Table {name} not found")

        table_path = self.workdir / f"{table_id}.jsonl"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        data = []
        with table_path.open("r") as f:
            for line in f:
                if line.strip():
                    row = json.loads(line.strip())
                    assert isinstance(row, dict), f"Row {row} is not a dictionary"
                    data.append(row)

        if not columns:
            # Fallback: infer columns from data if metadata doesn't exist
            columns_set = set()
            for row in data:
                for key, value in row.items():
                    if key not in [col.name for col in columns_set]:
                        col = Column(name=key, type=ColumnType.from_value(value))
                        columns_set.add(col)
            columns = list(columns_set)
            # Save inferred metadata
            self._save_table_metadata(table_id, name, columns)

        # Create table object for conversion purposes
        temp_table = Table(name=name, columns=columns, data=[], table_id=table_id)

        # Convert data from column IDs to column names
        converted_data = []
        for row in data:
            converted_row = temp_table.convert_row_from_column_ids(row)
            converted_data.append(converted_row)

        return Table(name=name, columns=columns, data=converted_data, table_id=table_id)

    def add_table(self, table: Table):
        # Check if table name already exists
        existing_id, _ = self._get_table_metadata_by_name(table.name)
        if existing_id is not None:
            raise ValueError(f"Table {table.name} already exists")

        table_path = self.workdir / f"{table.table_id}.jsonl"
        if table_path.exists():
            raise ValueError(f"Table with ID {table.table_id} already exists")

        with table_path.open("w") as f:
            for row in table.data:
                # Convert row to column ID format before saving
                row_with_ids = table.convert_row_to_column_ids(row)
                f.write(json.dumps(row_with_ids) + "\n")
        # Save columns metadata
        self._save_table_metadata(table.table_id, table.name, table.columns)

    def remove_table(self, name: str):
        table_id, _ = self._get_table_metadata_by_name(name)
        if table_id is None:
            raise ValueError(f"Table {name} not found")

        table_path = self.workdir / f"{table_id}.jsonl"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        table_path.unlink()
        self._remove_table_metadata(table_id)

    def rename_table(self, old_name: str, new_name: str):
        table_id, columns = self._get_table_metadata_by_name(old_name)
        if table_id is None:
            raise ValueError(f"Table {old_name} not found")

        # Check if new name already exists
        existing_id, _ = self._get_table_metadata_by_name(new_name)
        if existing_id is not None:
            raise ValueError(f"Table {new_name} already exists")

        # Update metadata with new name
        self._save_table_metadata(table_id, new_name, columns)

    def add_column(self, table_name: str, column: Column):
        table_id, existing_columns = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        table_path = self.workdir / f"{table_id}.jsonl"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        # Check if column already exists
        if any(col.name == column.name for col in existing_columns):
            raise ValueError(
                f"Column {column.name} already exists in table {table_name}"
            )

        # Add column to data using column ID
        rows = []
        with table_path.open("r") as f:
            for line in f:
                if line.strip():
                    row = json.loads(line.strip())
                    row[column.column_id] = column.default
                    rows.append(row)

        with table_path.open("w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

        # Update metadata
        existing_columns.append(column)
        self._save_table_metadata(table_id, table_name, existing_columns)

    def remove_column(self, table_name: str, column_name: str):
        table_id, columns = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        table_path = self.workdir / f"{table_id}.jsonl"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        # Remove column from data using column ID
        column_to_remove = None
        for col in columns:
            if col.name == column_name:
                column_to_remove = col
                break

        rows = []
        with table_path.open("r") as f:
            for line in f:
                if line.strip():
                    row = json.loads(line.strip())
                    if column_to_remove:
                        row.pop(column_to_remove.column_id, None)
                    rows.append(row)

        with table_path.open("w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

        # Update metadata
        columns = [col for col in columns if col.name != column_name]
        self._save_table_metadata(table_id, table_name, columns)

    def rename_column(self, table_name: str, old_name: str, new_name: str):
        table_id, columns = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        table_path = self.workdir / f"{table_id}.jsonl"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        # Data doesn't need to change for rename_column since we use column IDs
        # Only metadata needs to be updated
        for col in columns:
            if col.name == old_name:
                col.name = new_name
        self._save_table_metadata(table_id, table_name, columns)

    def change_column_type(
        self, table_name: str, column_name: str, new_type: ColumnType
    ):
        table_id, columns = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        # Update metadata
        for col in columns:
            if col.name == column_name:
                col.type = new_type
                break
        else:
            raise ValueError(f"Column {column_name} not found in table {table_name}")
        self._save_table_metadata(table_id, table_name, columns)

    def insert(self, table_name: str, row: dict):
        table_id, columns = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        # Create temp table for conversion
        temp_table = Table(name=table_name, columns=columns, data=[], table_id=table_id)

        table_path = self.workdir / f"{table_id}.jsonl"
        with table_path.open("a") as f:
            # Convert row to column ID format
            row_with_ids = temp_table.convert_row_to_column_ids(row)
            f.write(json.dumps(row_with_ids) + "\n")

    def update(self, table_name: str, idx: int, changes: dict):
        table_id, columns = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        # Create temp table for conversion
        temp_table = Table(name=table_name, columns=columns, data=[], table_id=table_id)

        table_path = self.workdir / f"{table_id}.jsonl"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        rows = []
        with table_path.open("r") as f:
            for i, line in enumerate(f):
                if line.strip():
                    row = json.loads(line.strip())
                    if i == idx:
                        # Convert changes to column ID format
                        changes_with_ids = temp_table.convert_row_to_column_ids(changes)
                        row.update(changes_with_ids)
                    rows.append(row)

        if idx < 0 or idx >= len(rows):
            raise IndexError(f"Index {idx} out of range for table {table_name}")

        with table_path.open("w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

    def delete(self, table_name: str, idxs: List[int]):
        table_id, _ = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        table_path = self.workdir / f"{table_id}.jsonl"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        rows = []
        with table_path.open("r") as f:
            for i, line in enumerate(f):
                if line.strip() and i not in idxs:
                    rows.append(json.loads(line.strip()))

        with table_path.open("w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")


class ExtendedTables(ITablesSnapshot):
    snapshot: ITablesSnapshot
    extra_tables: List[Table]

    def __init__(self, snapshot: ITablesSnapshot, tables: List[Table]):
        self.snapshot = snapshot
        self.extra_tables = []

        # Convert existing table data to column ID format if needed
        for table in tables:
            converted_data = []
            for row in table.data:
                converted_row = table.convert_row_to_column_ids(row)
                converted_data.append(converted_row)
            table.data = converted_data
            self.extra_tables.append(table)

    def get_table(self, name: str) -> Optional[Table]:
        table = self.snapshot.get_table(name)
        if table:
            return table
        for table in self.extra_tables:
            if table.name == name:
                # Create a copy with data converted to column names
                converted_data = []
                for row in table.data:
                    converted_data.append(table.convert_row_from_column_ids(row))

                result_table = Table(
                    name=table.name,
                    columns=table.columns,
                    data=converted_data,
                    table_id=table.table_id,
                )
                return result_table
        return None

    def add_table(self, table: Table):
        self.extra_tables.append(table)

    def remove_table(self, name: str):
        self.extra_tables = [table for table in self.extra_tables if table.name != name]

    def rename_table(self, old_name: str, new_name: str):
        for table in self.extra_tables:
            if table.name == old_name:
                table.name = new_name
                return
        self.snapshot.rename_table(old_name, new_name)

    def add_column(self, table_name: str, column: Column):
        for table in self.extra_tables:
            if table.name == table_name:
                table.columns.append(column)
                # Add default value to existing rows using column ID
                for row in table.data:
                    row[column.column_id] = column.default
                return
        self.snapshot.add_column(table_name, column)

    def remove_column(self, table_name: str, column_name: str):
        for table in self.extra_tables:
            if table.name == table_name:
                # Find the column to get its ID before removing
                column_to_remove = table.get_column(column_name)
                table.columns = [
                    col for col in table.columns if col.name != column_name
                ]
                # Remove column from existing rows using column ID
                if column_to_remove:
                    for row in table.data:
                        row.pop(column_to_remove.column_id, None)
                return
        self.snapshot.remove_column(table_name, column_name)

    def rename_column(self, table_name: str, old_name: str, new_name: str):
        for table in self.extra_tables:
            if table.name == table_name:
                # Update column name (data doesn't need to change since we use column IDs)
                for col in table.columns:
                    if col.name == old_name:
                        col.name = new_name
                        break
                return
        self.snapshot.rename_column(table_name, old_name, new_name)

    def change_column_type(
        self, table_name: str, column_name: str, new_type: ColumnType
    ):
        for table in self.extra_tables:
            if table.name == table_name:
                for col in table.columns:
                    if col.name == column_name:
                        col.type = new_type
                        return
        self.snapshot.change_column_type(table_name, column_name, new_type)

    def insert(self, table_name: str, row: dict):
        for table in self.extra_tables:
            if table.name == table_name:
                # Convert row from column names to column IDs
                row_with_ids = table.convert_row_to_column_ids(row)
                table.data.append(row_with_ids)
                return
        self.snapshot.insert(table_name, row)

    def update(self, table_name, idx, changes):
        for table in self.extra_tables:
            if table.name == table_name:
                # Convert changes from column names to column IDs
                changes_with_ids = table.convert_row_to_column_ids(changes)
                table.data[idx].update(changes_with_ids)
                return
        self.snapshot.update(table_name, idx, changes)

    def delete(self, table_name: str, idxs: List[int]):
        for table in self.extra_tables:
            if table.name == table_name:
                # Sort indices in descending order to avoid index shifting
                for idx in sorted(idxs, reverse=True):
                    if 0 <= idx < len(table.data):
                        del table.data[idx]
                return
        self.snapshot.delete(table_name, idxs)
