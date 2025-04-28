from typing import List, Optional
from pydantic import BaseModel

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

class TableSnapshot(BaseModel):
    tables: List[Table]