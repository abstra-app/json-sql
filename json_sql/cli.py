from typing import List
from pathlib import Path
from json_sql.tables import FileSystemTables, Table
from json import loads
from eval import eval_sql


def query(code: str, workdir: Path, ctx: dict):
    tables = FileSystemTables(workdir=workdir)
    result = eval_sql(code=code, tables=tables, ctx=ctx)
    return result


def help(): ...
