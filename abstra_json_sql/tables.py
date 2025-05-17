from typing import List, Optional
from pydantic import BaseModel
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


class ForeignKey(BaseModel):
    table: str
    column: str


class Column(BaseModel):
    name: str
    type: ColumnType
    is_primary_key: bool = False
    foreign_key: Optional[ForeignKey] = None

    def __hash__(self):
        return hash((self.name, self.type, self.is_primary_key, self.foreign_key))


class Table(BaseModel):
    name: str
    columns: List[Column]
    data: List[dict] = []


class ITablesSnapshot(ABC):
    @abstractmethod
    def get_table(self, name: str) -> Optional[Table]:
        raise NotImplementedError("get_table method must be implemented")


class InMemoryTables(BaseModel, ITablesSnapshot):
    tables: List[Table]

    def get_table(self, name: str) -> Optional[Table]:
        for table in self.tables:
            if table.name == name:
                return table
        return None


class FileSystemTables(ITablesSnapshot):
    workdir: Path

    def __init__(self, workdir: Path):
        self.workdir = workdir

    def get_table(self, name: str):
        table_path = self.workdir / f"{name}.json"
        if not table_path.exists():
            raise FileNotFoundError(f"File {table_path} does not exist")
        rows = json.loads(table_path.read_text())
        columns = set()
        for row in rows:
            assert isinstance(row, dict), f"Row {row} is not a dictionary"
            for key, value in row.items():
                if key not in columns:
                    col = Column(name=key, type=type(value).__name__)
                    columns.add(col)
        return Table(name=name, columns=list(columns), data=rows)


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
