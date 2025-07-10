from typing import Any, List, Optional
from pathlib import Path
from abc import ABC, abstractmethod
import json
from enum import Enum


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
    ):
        self.name = name
        self.type = type
        self.is_primary_key = is_primary_key
        self.foreign_key = foreign_key
        self.default = default

    def __hash__(self):
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
    def __init__(self, name: str, columns: List[Column], data: List[dict] = None):
        self.name = name
        self.columns = columns
        self.data = data if data is not None else []

    def get_column(self, name: str) -> Optional[Column]:
        for column in self.columns:
            if column.name == name:
                return column
        return None


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
                    self.tables.append(
                        Table(
                            name=table["name"],
                            columns=columns,
                            data=table.get("data", []),
                        )
                    )
                else:
                    self.tables.append(table)

    def get_table(self, name: str) -> Optional[Table]:
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
        table = self.get_table(old_name)
        if table is None:
            raise ValueError(f"Table {old_name} not found")
        if self.get_table(new_name) is not None:
            raise ValueError(f"Table {new_name} already exists")
        table.name = new_name

    def add_column(self, table_name: str, column: Column):
        table = self.get_table(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} not found")
        if table.get_column(column.name) is not None:
            raise ValueError(
                f"Column {column.name} already exists in table {table_name}"
            )
        table.columns.append(column)

    def remove_column(self, table_name: str, column_name: str):
        table = self.get_table(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} not found")
        table.columns = [col for col in table.columns if col.name != column_name]

    def rename_column(self, table_name: str, old_name: str, new_name: str):
        table = self.get_table(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} not found")
        column = table.get_column(old_name)
        if column is None:
            raise ValueError(f"Column {old_name} not found in table {table_name}")
        column.name = new_name

    def change_column_type(
        self, table_name: str, column_name: str, new_type: ColumnType
    ):
        table = self.get_table(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} not found")
        column = table.get_column(column_name)
        if column is None:
            raise ValueError(f"Column {column_name} not found in table {table_name}")
        column.type = new_type

    def insert(self, table: str, row: dict):
        table_obj = self.get_table(table)
        if table_obj is None:
            raise ValueError(f"Table {table} not found")
        table_obj.data.append(row)

    def update(self, table: str, idx: int, changes: dict):
        table_obj = self.get_table(table)
        table_obj.data[idx].update(changes)

    def delete(self, table: str, idxs: List[int]):
        table_obj = self.get_table(table)
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

    def _get_table_metadata(self, table_name: str) -> List[Column]:
        """Get table metadata from the __schema__.json file"""
        metadata_path = self.workdir / "__schema__.json"
        metadata = json.loads(metadata_path.read_text())
        table_metadata = metadata.get(table_name, [])
        columns = []
        for col_dict in table_metadata:
            columns.append(Column.from_dict(col_dict))
        return columns

    def _save_table_metadata(self, table_name: str, columns: List[Column]):
        """Save table metadata to the __schema__.json file"""
        metadata_path = self.workdir / "__schema__.json"
        metadata = json.loads(metadata_path.read_text())
        # Convert Column objects to dicts with proper serialization
        column_dicts = []
        for col in columns:
            col_dict = col.to_dict()
            column_dicts.append(col_dict)
        metadata[table_name] = column_dicts
        metadata_path.write_text(json.dumps(metadata, indent=2))

    def _remove_table_metadata(self, table_name: str):
        """Remove table metadata from the __schema__.json file"""
        metadata_path = self.workdir / "__schema__.json"
        metadata = json.loads(metadata_path.read_text())
        if table_name in metadata:
            del metadata[table_name]
        metadata_path.write_text(json.dumps(metadata, indent=2))

    def get_table(self, name: str):
        table_path = self.workdir / f"{name}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")
        rows = json.loads(table_path.read_text())
        columns = self._get_table_metadata(name)
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
            self._save_table_metadata(name, columns)
        return Table(name=name, columns=columns, data=rows)

    def add_table(self, table: Table):
        table_path = self.workdir / f"{table.name}.json"
        if table_path.exists():
            raise ValueError(f"Table {table.name} already exists")
        table_path.write_text(json.dumps(table.data, indent=2))
        # Save columns metadata
        self._save_table_metadata(table.name, table.columns)

    def remove_table(self, name: str):
        table_path = self.workdir / f"{name}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")
        table_path.unlink()
        self._remove_table_metadata(name)

    def rename_table(self, old_name: str, new_name: str):
        old_path = self.workdir / f"{old_name}.json"
        new_path = self.workdir / f"{new_name}.json"
        if not old_path.exists():
            raise FileNotFoundError(f"File {old_path} does not exist")
        if new_path.exists():
            raise ValueError(f"File {new_path} already exists")
        old_path.rename(new_path)

        # Update metadata
        columns = self._get_table_metadata(old_name)
        self._remove_table_metadata(old_name)
        self._save_table_metadata(new_name, columns)

    def insert(self, table_name: str, row: dict):
        table_path = self.workdir / f"{table_name}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")
        rows = json.loads(table_path.read_text())
        assert isinstance(
            rows, list
        ), f"File {table_path} does not contain a list of rows"
        rows.append(row)
        table_path.write_text(json.dumps(rows, indent=2))

    def add_column(self, table_name: str, column: Column):
        table_path = self.workdir / f"{table_name}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")
        rows = json.loads(table_path.read_text())
        assert isinstance(
            rows, list
        ), f"File {table_path} does not contain a list of rows"

        # Check if column already exists
        existing_columns = self._get_table_metadata(table_name)
        if any(col.name == column.name for col in existing_columns):
            raise ValueError(
                f"Column {column.name} already exists in table {table_name}"
            )

        # Add column to data
        for row in rows:
            row[column.name] = column.default
        table_path.write_text(json.dumps(rows, indent=2))

        # Update metadata
        existing_columns.append(column)
        self._save_table_metadata(table_name, existing_columns)

    def remove_column(self, table_name: str, column_name: str):
        table_path = self.workdir / f"{table_name}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")
        rows = json.loads(table_path.read_text())
        assert isinstance(
            rows, list
        ), f"File {table_path} does not contain a list of rows"

        # Remove column from data
        for row in rows:
            if column_name in row:
                del row[column_name]
        table_path.write_text(json.dumps(rows, indent=2))

        # Update metadata
        columns = self._get_table_metadata(table_name)
        columns = [col for col in columns if col.name != column_name]
        self._save_table_metadata(table_name, columns)

    def rename_column(self, table_name: str, old_name: str, new_name: str):
        table_path = self.workdir / f"{table_name}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")
        rows = json.loads(table_path.read_text())
        assert isinstance(
            rows, list
        ), f"File {table_path} does not contain a list of rows"

        # Rename column in data
        for row in rows:
            if old_name in row:
                row[new_name] = row.pop(old_name)
        table_path.write_text(json.dumps(rows, indent=2))

        # Update metadata
        columns = self._get_table_metadata(table_name)
        for col in columns:
            if col.name == old_name:
                col.name = new_name
        self._save_table_metadata(table_name, columns)

    def change_column_type(
        self, table_name: str, column_name: str, new_type: ColumnType
    ):
        # Update metadata
        columns = self._get_table_metadata(table_name)
        for col in columns:
            if col.name == column_name:
                col.type = new_type
                break
        else:
            raise ValueError(f"Column {column_name} not found in table {table_name}")
        self._save_table_metadata(table_name, columns)

    def update(self, table_name: str, idx: int, changes: dict):
        table_path = self.workdir / f"{table_name}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")
        rows = json.loads(table_path.read_text())
        assert isinstance(
            rows, list
        ), f"File {table_path} does not contain a list of rows"
        if idx < 0 or idx >= len(rows):
            raise IndexError(f"Index {idx} out of range for table {table_name}")
        rows[idx].update(changes)
        table_path.write_text(json.dumps(rows, indent=2))

    def delete(self, table_name: str, idxs: List[int]):
        table_path = self.workdir / f"{table_name}.json"
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
        if not metadata_path.exists():
            metadata_path.write_text("")

    def _get_table_metadata(self, table_name: str) -> List[Column]:
        """Get table metadata from the __schema__.jsonl file"""
        metadata_path = self.workdir / "__schema__.jsonl"
        if not metadata_path.exists():
            return []

        with metadata_path.open("r") as f:
            for line in f:
                if line.strip():
                    metadata_entry = json.loads(line.strip())
                    if metadata_entry.get("table_name") == table_name:
                        columns = []
                        for col_dict in metadata_entry.get("columns", []):
                            columns.append(Column.from_dict(col_dict))
                        return columns
        return []

    def _save_table_metadata(self, table_name: str, columns: List[Column]):
        """Save table metadata to the __schema__.jsonl file"""
        metadata_path = self.workdir / "__schema__.jsonl"

        # Read existing metadata and filter out the current table
        existing_metadata = []
        if metadata_path.exists():
            with metadata_path.open("r") as f:
                for line in f:
                    if line.strip():
                        metadata_entry = json.loads(line.strip())
                        if metadata_entry.get("table_name") != table_name:
                            existing_metadata.append(metadata_entry)

        # Add the new metadata entry
        column_dicts = []
        for col in columns:
            col_dict = col.to_dict()
            column_dicts.append(col_dict)

        new_entry = {"table_name": table_name, "columns": column_dicts}
        existing_metadata.append(new_entry)

        # Write all metadata back
        with metadata_path.open("w") as f:
            for entry in existing_metadata:
                f.write(json.dumps(entry) + "\n")

    def _remove_table_metadata(self, table_name: str):
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
                    if metadata_entry.get("table_name") != table_name:
                        remaining_metadata.append(metadata_entry)

        # Write remaining metadata back
        with metadata_path.open("w") as f:
            for entry in remaining_metadata:
                f.write(json.dumps(entry) + "\n")

    def get_table(self, name: str) -> Optional[Table]:
        table_path = self.workdir / f"{name}.jsonl"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        columns = self._get_table_metadata(name)
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
            self._save_table_metadata(name, columns)

        return Table(name=name, columns=columns, data=data)

    def add_table(self, table: Table):
        table_path = self.workdir / f"{table.name}.jsonl"
        if table_path.exists():
            raise ValueError(f"Table {table.name} already exists")
        with table_path.open("w") as f:
            for row in table.data:
                f.write(json.dumps(row) + "\n")
        # Save columns metadata
        self._save_table_metadata(table.name, table.columns)

    def remove_table(self, name: str):
        table_path = self.workdir / f"{name}.jsonl"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")
        table_path.unlink()
        self._remove_table_metadata(name)

    def rename_table(self, old_name: str, new_name: str):
        old_path = self.workdir / f"{old_name}.jsonl"
        new_path = self.workdir / f"{new_name}.jsonl"
        if not old_path.exists():
            raise FileNotFoundError(f"File {old_path} does not exist")
        if new_path.exists():
            raise ValueError(f"File {new_path} already exists")
        old_path.rename(new_path)

        # Update metadata
        columns = self._get_table_metadata(old_name)
        self._remove_table_metadata(old_name)
        self._save_table_metadata(new_name, columns)

    def add_column(self, table_name: str, column: Column):
        table_path = self.workdir / f"{table_name}.jsonl"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        # Check if column already exists
        existing_columns = self._get_table_metadata(table_name)
        if any(col.name == column.name for col in existing_columns):
            raise ValueError(
                f"Column {column.name} already exists in table {table_name}"
            )

        # Add column to data
        rows = []
        with table_path.open("r") as f:
            for line in f:
                if line.strip():
                    row = json.loads(line.strip())
                    row[column.name] = column.default
                    rows.append(row)

        with table_path.open("w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

        # Update metadata
        existing_columns.append(column)
        self._save_table_metadata(table_name, existing_columns)

    def remove_column(self, table_name: str, column_name: str):
        table_path = self.workdir / f"{table_name}.jsonl"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        # Remove column from data
        rows = []
        with table_path.open("r") as f:
            for line in f:
                if line.strip():
                    row = json.loads(line.strip())
                    row.pop(column_name, None)
                    rows.append(row)

        with table_path.open("w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

        # Update metadata
        columns = self._get_table_metadata(table_name)
        columns = [col for col in columns if col.name != column_name]
        self._save_table_metadata(table_name, columns)

    def rename_column(self, table_name: str, old_name: str, new_name: str):
        table_path = self.workdir / f"{table_name}.jsonl"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        # Rename column in data
        rows = []
        with table_path.open("r") as f:
            for line in f:
                if line.strip():
                    row = json.loads(line.strip())
                    if old_name in row:
                        row[new_name] = row.pop(old_name)
                    rows.append(row)

        with table_path.open("w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

        # Update metadata
        columns = self._get_table_metadata(table_name)
        for col in columns:
            if col.name == old_name:
                col.name = new_name
        self._save_table_metadata(table_name, columns)

    def change_column_type(
        self, table_name: str, column_name: str, new_type: ColumnType
    ):
        # Update metadata
        columns = self._get_table_metadata(table_name)
        for col in columns:
            if col.name == column_name:
                col.type = new_type
                break
        else:
            raise ValueError(f"Column {column_name} not found in table {table_name}")
        self._save_table_metadata(table_name, columns)

    def insert(self, table_name: str, row: dict):
        table_path = self.workdir / f"{table_name}.jsonl"
        with table_path.open("a") as f:
            f.write(json.dumps(row) + "\n")

    def update(self, table_name: str, idx: int, changes: dict):
        table_path = self.workdir / f"{table_name}.jsonl"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        rows = []
        with table_path.open("r") as f:
            for i, line in enumerate(f):
                if line.strip():
                    row = json.loads(line.strip())
                    if i == idx:
                        row.update(changes)
                    rows.append(row)

        if idx < 0 or idx >= len(rows):
            raise IndexError(f"Index {idx} out of range for table {table_name}")

        with table_path.open("w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

    def delete(self, table_name: str, idxs: List[int]):
        table_path = self.workdir / f"{table_name}.jsonl"
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
        self.extra_tables = tables

    def get_table(self, name: str) -> Optional[Table]:
        table = self.snapshot.get_table(name)
        if table:
            return table
        for table in self.extra_tables:
            if table.name == name:
                return table
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
                # Add default value to existing rows
                for row in table.data:
                    row[column.name] = column.default
                return
        self.snapshot.add_column(table_name, column)

    def remove_column(self, table_name: str, column_name: str):
        for table in self.extra_tables:
            if table.name == table_name:
                table.columns = [
                    col for col in table.columns if col.name != column_name
                ]
                # Remove column from existing rows
                for row in table.data:
                    if column_name in row:
                        del row[column_name]
                return
        self.snapshot.remove_column(table_name, column_name)

    def rename_column(self, table_name: str, old_name: str, new_name: str):
        for table in self.extra_tables:
            if table.name == table_name:
                # Update column name
                for col in table.columns:
                    if col.name == old_name:
                        col.name = new_name
                        break
                # Update data
                for row in table.data:
                    if old_name in row:
                        row[new_name] = row.pop(old_name)
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
                table.data.append(row)
                return
        self.snapshot.insert(table_name, row)

    def update(self, table_name, idx, changes):
        for table in self.extra_tables:
            if table.name == table_name:
                table.data[idx].update(changes)
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
