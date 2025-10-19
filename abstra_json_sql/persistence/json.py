import json
from pathlib import Path
from typing import List, Optional

from ..tables import Column, ColumnType, ITablesSnapshot, Table


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
                        col = Column(name=key, schema=ColumnType.from_value(value))
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

    def _insert(self, table_name: str, row: dict):
        table_id, columns = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        table_path = self.workdir / f"{table_id}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        # Create temp table for conversion
        temp_table = Table(name=table_name, columns=columns, data=[], table_id=table_id)

        rows = json.loads(table_path.read_text())
        assert isinstance(rows, list), (
            f"File {table_path} does not contain a list of rows"
        )

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
        assert isinstance(rows, list), (
            f"File {table_path} does not contain a list of rows"
        )

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
        assert isinstance(rows, list), (
            f"File {table_path} does not contain a list of rows"
        )

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
        assert isinstance(rows, list), (
            f"File {table_path} does not contain a list of rows"
        )

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
                col.schema = new_type
                break
        else:
            raise ValueError(f"Column {column_name} not found in table {table_name}")
        self._save_table_metadata(table_id, table_name, columns)

    def _update(self, table_name: str, idx: int, changes: dict):
        table_id, columns = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        table_path = self.workdir / f"{table_id}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        # Create temp table for conversion
        temp_table = Table(name=table_name, columns=columns, data=[], table_id=table_id)

        rows = json.loads(table_path.read_text())
        assert isinstance(rows, list), (
            f"File {table_path} does not contain a list of rows"
        )
        if idx < 0 or idx >= len(rows):
            raise IndexError(f"Index {idx} out of range for table {table_name}")

        # Convert changes to column ID format
        changes_with_ids = temp_table.convert_row_to_column_ids(changes)
        rows[idx].update(changes_with_ids)
        table_path.write_text(json.dumps(rows, indent=2))

    def _delete(self, table_name: str, idxs: List[int]):
        table_id, _ = self._get_table_metadata_by_name(table_name)
        if table_id is None:
            raise ValueError(f"Table {table_name} not found")

        table_path = self.workdir / f"{table_id}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")

        rows = json.loads(table_path.read_text())
        assert isinstance(rows, list), (
            f"File {table_path} does not contain a list of rows"
        )

        # Sort indices in descending order to avoid index shifting
        for idx in sorted(idxs, reverse=True):
            if idx < 0 or idx >= len(rows):
                raise IndexError(f"Index {idx} out of range for table {table_name}")
            del rows[idx]
        table_path.write_text(json.dumps(rows, indent=2))
