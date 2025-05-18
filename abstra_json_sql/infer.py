from .tables import ColumnType
from .ast import (
    Expression,
    StringExpression,
    IntExpression,
    FloatExpression,
    NullExpression,
    TrueExpression,
    FalseExpression,
    PlusExpression,
    MinusExpression,
    MultiplyExpression,
    DivideExpression,
    FunctionCallExpression,
)


def infer_expression(expr: Expression, ctx: dict) -> ColumnType:
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
    elif (
        isinstance(expr, PlusExpression)
        or isinstance(expr, MinusExpression)
        or isinstance(expr, MultiplyExpression)
        or isinstance(expr, DivideExpression)
    ):
        left_type = infer_expression(expr.left, ctx)
        right_type = infer_expression(expr.right, ctx)
        if left_type == "integer" and right_type == "integer":
            return "integer"
        elif left_type == "float" or right_type == "float":
            return "float"
        else:
            return "unknown"
    else:
        return "unknown"
