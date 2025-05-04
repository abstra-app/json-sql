from .lexer import scan
from .parser import parse
from .apply import apply_command
from .tables import TablesSnapshot


def eval_sql(code: str, tables: TablesSnapshot, ctx: dict):
    tokens = scan(code)
    ast = parse(tokens)
    result = apply_command(command=ast, tables=tables, ctx=ctx)
    return result
