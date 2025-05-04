from typing import List
from pathlib import Path
from json_sql.tables import TablesSnapshot, Table
from json import loads
from eval import eval_sql


def query(code: str, json_paths: List[Path], ctx: dict) -> List[dict]:
    tables = TablesSnapshot(
        tables=[
            Table(name=path.stem, columns=[], data=loads(path.read_text()))
            for path in json_paths
        ]
    )
    return eval_sql(code=code, tables=tables, ctx=ctx)


def help(): ...
