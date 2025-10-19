from typing import List, Optional

from ..tables import Column, ColumnType, ITablesSnapshot, Table


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
                        col.schema = new_type
                        return
        self.snapshot.change_column_type(table_name, column_name, new_type)

    def _insert(self, table_name: str, row: dict):
        for table in self.extra_tables:
            if table.name == table_name:
                # Convert row from column names to column IDs
                row_with_ids = table.convert_row_to_column_ids(row)
                table.data.append(row_with_ids)
                return
        self.snapshot.insert(table_name, row)

    def _update(self, table_name, idx, changes):
        for table in self.extra_tables:
            if table.name == table_name:
                # Convert changes from column names to column IDs
                changes_with_ids = table.convert_row_to_column_ids(changes)
                table.data[idx].update(changes_with_ids)
                return
        self.snapshot.update(table_name, idx, changes)

    def _delete(self, table_name: str, idxs: List[int]):
        for table in self.extra_tables:
            if table.name == table_name:
                # Sort indices in descending order to avoid index shifting
                for idx in sorted(idxs, reverse=True):
                    if 0 <= idx < len(table.data):
                        del table.data[idx]
                return
        self.snapshot.delete(table_name, idxs)
