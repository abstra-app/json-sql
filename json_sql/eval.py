from .data_schema import TableSnapshot, Table
from typing import List
from .ast import (
    Expression,
    StringExpression,
    IntExpression,
    FloatExpression,
    NameExpression,
    Where,
    PlusExpression,
    Order,
    MinusExpression,
    MultiplyExpression,
    DivideExpression,
    EqualExpression,
    NotEqualExpression,
    GreaterThanExpression,
    GreaterThanOrEqualExpression,
    LessThanExpression,
    LessThanOrEqualExpression,
)


def eval_expression(expression: Expression, ctx: dict):
    if isinstance(expression, StringExpression):
        return expression.value
    elif isinstance(expression, IntExpression):
        return expression.value
    elif isinstance(expression, FloatExpression):
        return expression.value
    elif isinstance(expression, NameExpression) and expression.name.lower() in [
        "true",
        "false",
    ]:
        return expression.name.lower() == "true"
    elif isinstance(expression, NameExpression):
        if expression.name in ctx:
            return ctx[expression.name]
        else:
            raise ValueError(f"Unknown variable: {expression.name}")
    elif isinstance(expression, PlusExpression):
        left_value = eval_expression(expression.left, ctx)
        right_value = eval_expression(expression.right, ctx)
        if isinstance(left_value, (int, float)) and isinstance(
            right_value, (int, float)
        ):
            return left_value + right_value
        else:
            raise ValueError(
                f"Unsupported types for addition: {type(left_value)}, {type(right_value)}"
            )
    elif isinstance(expression, MinusExpression):
        left_value = eval_expression(expression.left, ctx)
        right_value = eval_expression(expression.right, ctx)
        if isinstance(left_value, (int, float)) and isinstance(
            right_value, (int, float)
        ):
            return left_value - right_value
        else:
            raise ValueError(
                f"Unsupported types for subtraction: {type(left_value)}, {type(right_value)}"
            )
    elif isinstance(expression, MultiplyExpression):
        left_value = eval_expression(expression.left, ctx)
        right_value = eval_expression(expression.right, ctx)
        if isinstance(left_value, (int, float)) and isinstance(
            right_value, (int, float)
        ):
            return left_value * right_value
        else:
            raise ValueError(
                f"Unsupported types for multiplication: {type(left_value)}, {type(right_value)}"
            )
    elif isinstance(expression, DivideExpression):
        left_value = eval_expression(expression.left, ctx)
        right_value = eval_expression(expression.right, ctx)
        if isinstance(left_value, (int, float)) and isinstance(
            right_value, (int, float)
        ):
            if right_value == 0:
                raise ValueError("Division by zero")
            return left_value / right_value
        else:
            raise ValueError(
                f"Unsupported types for division: {type(left_value)}, {type(right_value)}"
            )
    elif isinstance(expression, EqualExpression):
        left_value = eval_expression(expression.left, ctx)
        right_value = eval_expression(expression.right, ctx)
        if left_value == right_value:
            return True
        else:
            return False
    elif isinstance(expression, NotEqualExpression):
        left_value = eval_expression(expression.left, ctx)
        right_value = eval_expression(expression.right, ctx)
        if left_value != right_value:
            return True
        else:
            return False
    elif isinstance(expression, GreaterThanExpression):
        left_value = eval_expression(expression.left, ctx)
        right_value = eval_expression(expression.right, ctx)
        if isinstance(left_value, (int, float)) and isinstance(
            right_value, (int, float)
        ):
            return left_value > right_value
        else:
            raise ValueError(
                f"Unsupported types for greater than: {type(left_value)}, {type(right_value)}"
            )
    elif isinstance(expression, GreaterThanOrEqualExpression):
        left_value = eval_expression(expression.left, ctx)
        right_value = eval_expression(expression.right, ctx)
        if isinstance(left_value, (int, float)) and isinstance(
            right_value, (int, float)
        ):
            return left_value >= right_value
        else:
            raise ValueError(
                f"Unsupported types for greater than or equal: {type(left_value)}, {type(right_value)}"
            )
    elif isinstance(expression, LessThanExpression):
        left_value = eval_expression(expression.left, ctx)
        right_value = eval_expression(expression.right, ctx)
        if isinstance(left_value, (int, float)) and isinstance(
            right_value, (int, float)
        ):
            return left_value < right_value
        else:
            raise ValueError(
                f"Unsupported types for less than: {type(left_value)}, {type(right_value)}"
            )
    elif isinstance(expression, LessThanOrEqualExpression):
        left_value = eval_expression(expression.left, ctx)
        right_value = eval_expression(expression.right, ctx)
        if isinstance(left_value, (int, float)) and isinstance(
            right_value, (int, float)
        ):
            return left_value <= right_value
        else:
            raise ValueError(
                f"Unsupported types for less than or equal: {type(left_value)}, {type(right_value)}"
            )
    else:
        raise ValueError(f"Unsupported expression type: {type(expression)}")


def eval_where(where: Where, data: List[dict], ctx: dict):
    result = []
    for row in data:
        value = eval_expression(where.expression, {**ctx, **row})
        if value is True:
            result.append(row)
        elif value is False:
            continue
        else:
            raise ValueError(f"Where expressions should return bool, not {value}")
    return result


def eval_order_by(order_by: Order, data: List[dict], ctx: dict):
    for order_field in order_by.fields:
        data.sort(
            key=lambda x: eval_expression(order_field.expression),
            reverse=(order_field.order == "DESC"),
        )
    return data
