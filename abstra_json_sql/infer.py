from .ast import (
    Expression,
    StringExpression,
    IntExpression,
    FloatExpression,
    NullExpression,
    TrueExpression,
    FalseExpression,
    FunctionCallExpression,
)


def infer_expression(expr: Expression, ctx: dict):
    if isinstance(expr, StringExpression):
        return "string"
    elif isinstance(expr, IntExpression):
        return "integer"
    elif isinstance(expr, FloatExpression):
        return "float"
    elif isinstance(expr, TrueExpression) or isinstance(expr, FalseExpression):
        return "boolean"
    elif isinstance(expr, NullExpression):
        return "null"
    elif isinstance(expr, FunctionCallExpression):
        if expr.name == "count":
            return "integer"
        elif expr.name == "sum":
            return "float"
        elif expr.name == "avg":
            return "float"
    else:
        return "unknown"
