from typing import List, Optional

from ..tables import Column, ColumnType, ITablesSnapshot, Table


class InMemoryTables(ITablesSnapshot):
    def _update(self, table: str, idx: int, changes: dict):
        table_obj = self._get_internal_table(table)
        if table_obj is None:
            raise ValueError(f"Table {table} not found")
        # Convert changes from column names to column IDs
        changes_with_ids = table_obj.convert_row_to_column_ids(changes)
        table_obj.data[idx].update(changes_with_ids)

    def _delete(self, table: str, idxs: List[int]):
        table_obj = self._get_internal_table(table)
        if table_obj is None:
            raise ValueError(f"Table {table} not found")
        table_obj.data = [row for i, row in enumerate(table_obj.data) if i not in idxs]

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
        column.schema = new_type

    def _insert(self, table: str, row: dict):
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
