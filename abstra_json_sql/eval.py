from .apply import apply_command
from .lexer import scan
from .parser import parse
from .tables import ITablesSnapshot


def eval_sql(code: str, tables: ITablesSnapshot, ctx: dict):
    tokens = scan(code)
    ast = parse(tokens)
    result = apply_command(command=ast, tables=tables, ctx=ctx)
    return result
