from .ast import (
    DivideExpression,
    Expression,
    FalseExpression,
    FloatExpression,
    FunctionCallExpression,
    IntExpression,
    MinusExpression,
    MultiplyExpression,
    NullExpression,
    PlusExpression,
    StringExpression,
    TrueExpression,
)
from .tables import ColumnType


def infer_expression(expr: Expression, ctx: dict) -> ColumnType:
    if isinstance(expr, StringExpression):
        return ColumnType.string
    elif isinstance(expr, IntExpression):
        return ColumnType.int
    elif isinstance(expr, FloatExpression):
        return ColumnType.float
    elif isinstance(expr, TrueExpression) or isinstance(expr, FalseExpression):
        return ColumnType.bool
    elif isinstance(expr, NullExpression):
        return ColumnType.null
    elif isinstance(expr, FunctionCallExpression):
        if expr.name == "count":
            return ColumnType.int
        elif expr.name == "sum":
            return ColumnType.float
        elif expr.name == "avg":
            return ColumnType.float
    elif (
        isinstance(expr, PlusExpression)
        or isinstance(expr, MinusExpression)
        or isinstance(expr, MultiplyExpression)
        or isinstance(expr, DivideExpression)
    ):
        left_type = infer_expression(expr.left, ctx)
        right_type = infer_expression(expr.right, ctx)
        if left_type == ColumnType.int and right_type == ColumnType.int:
            return ColumnType.int
        elif left_type == ColumnType.float or right_type == ColumnType.float:
            return ColumnType.float
        else:
            return ColumnType.unknown
    else:
        return ColumnType.unknown
