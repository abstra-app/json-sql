from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
from abc import ABC, abstractmethod
import json


class ForeignKey(BaseModel):
    table: str
    column: str


class Column(BaseModel):
    name: str
    type: str
    is_primary_key: bool = False
    foreign_key: Optional[ForeignKey] = None


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
