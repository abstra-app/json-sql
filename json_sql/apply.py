from typing import List, Dict
from .data_schema import TablesSnapshot
from .ast import (
    Expression,
    StringExpression,
    IntExpression,
    Select,
    FloatExpression,
    NameExpression,
    From,
    SelectField,
    Where,
    GroupBy,
    Command,
    PlusExpression,
    OrderBy,
    MinusExpression,
    MultiplyExpression,
    DivideExpression,
    EqualExpression,
    NotEqualExpression,
    GreaterThanExpression,
    GreaterThanOrEqualExpression,
    LessThanExpression,
    LessThanOrEqualExpression,
    Limit,
)


def apply_expression(expression: Expression, ctx: dict):
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
        left_value = apply_expression(expression.left, ctx)
        right_value = apply_expression(expression.right, ctx)
        if isinstance(left_value, (int, float)) and isinstance(
            right_value, (int, float)
        ):
            return left_value + right_value
        else:
            raise ValueError(
                f"Unsupported types for addition: {type(left_value)}, {type(right_value)}"
            )
    elif isinstance(expression, MinusExpression):
        left_value = apply_expression(expression.left, ctx)
        right_value = apply_expression(expression.right, ctx)
        if isinstance(left_value, (int, float)) and isinstance(
            right_value, (int, float)
        ):
            return left_value - right_value
        else:
            raise ValueError(
                f"Unsupported types for subtraction: {type(left_value)}, {type(right_value)}"
            )
    elif isinstance(expression, MultiplyExpression):
        left_value = apply_expression(expression.left, ctx)
        right_value = apply_expression(expression.right, ctx)
        if isinstance(left_value, (int, float)) and isinstance(
            right_value, (int, float)
        ):
            return left_value * right_value
        else:
            raise ValueError(
                f"Unsupported types for multiplication: {type(left_value)}, {type(right_value)}"
            )
    elif isinstance(expression, DivideExpression):
        left_value = apply_expression(expression.left, ctx)
        right_value = apply_expression(expression.right, ctx)
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
        left_value = apply_expression(expression.left, ctx)
        right_value = apply_expression(expression.right, ctx)
        if left_value == right_value:
            return True
        else:
            return False
    elif isinstance(expression, NotEqualExpression):
        left_value = apply_expression(expression.left, ctx)
        right_value = apply_expression(expression.right, ctx)
        if left_value != right_value:
            return True
        else:
            return False
    elif isinstance(expression, GreaterThanExpression):
        left_value = apply_expression(expression.left, ctx)
        right_value = apply_expression(expression.right, ctx)
        if isinstance(left_value, (int, float)) and isinstance(
            right_value, (int, float)
        ):
            return left_value > right_value
        else:
            raise ValueError(
                f"Unsupported types for greater than: {type(left_value)}, {type(right_value)}"
            )
    elif isinstance(expression, GreaterThanOrEqualExpression):
        left_value = apply_expression(expression.left, ctx)
        right_value = apply_expression(expression.right, ctx)
        if isinstance(left_value, (int, float)) and isinstance(
            right_value, (int, float)
        ):
            return left_value >= right_value
        else:
            raise ValueError(
                f"Unsupported types for greater than or equal: {type(left_value)}, {type(right_value)}"
            )
    elif isinstance(expression, LessThanExpression):
        left_value = apply_expression(expression.left, ctx)
        right_value = apply_expression(expression.right, ctx)
        if isinstance(left_value, (int, float)) and isinstance(
            right_value, (int, float)
        ):
            return left_value < right_value
        else:
            raise ValueError(
                f"Unsupported types for less than: {type(left_value)}, {type(right_value)}"
            )
    elif isinstance(expression, LessThanOrEqualExpression):
        left_value = apply_expression(expression.left, ctx)
        right_value = apply_expression(expression.right, ctx)
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


def apply_where(where: Where, data: List[dict], ctx: dict):
    result = []
    for row in data:
        value = apply_expression(where.expression, {**ctx, **row})
        if value is True:
            result.append(row)
        elif value is False:
            continue
        else:
            raise ValueError(f"Where expressions should return bool, not {value}")
    return result


def apply_order_by(order_by: OrderBy, data: List[dict], ctx: dict):
    for order_field in order_by.fields:
        data.sort(
            key=lambda x: apply_expression(order_field.expression, {**ctx, **x}),
            reverse=(order_field.direction == "DESC"),
        )
    return data

def apply_group_by(group_by: GroupBy, data: List[dict], ctx: dict):
    groups: Dict[tuple, list] = {}
    for row in data:
        key = tuple(
            apply_expression(field, {**ctx, **row}) for field in group_by.fields
        )
        if key not in groups:
            groups[key] = []
        groups[key].append(row)
    return groups

def apply_limit(limit: Limit, data: List[dict], ctx: dict):
    start = limit.offset
    end = start + limit.limit
    return data[start:end]

def apply_select_fields(fields: List[SelectField], data: List[dict], ctx: dict):
    return [
        {
            field.alias: apply_expression(field.expression, {**ctx, **row})
            for field in fields
        }
        for row in data
    ]

def apply_from(from_part: From, tables: TablesSnapshot, ctx: dict) -> List[dict]:
    table = tables.get_table(from_part.table)
    if not table:
        raise ValueError(f"Table {from_part.table} not found")
    data = table.data
    if from_part.join:
        for join in from_part.join:
            join_table = tables.get_table(join.table)
            if not join_table:
                raise ValueError(f"Table {join.table} not found")
            data = [
                {**row, **join_row}
                for row in data
                for join_row in join_table.data
                if apply_expression(join.on, {**ctx, **row, **join_row})
            ]
    return data

def apply_select(select: Select, tables: TablesSnapshot, ctx: dict):
    data = apply_from(select.from_part, tables, ctx)
    if select.where_part:
        data = apply_where(select.where_part, data, ctx)
    if select.group_part:
        data = apply_group_by(select.group_part, data, ctx)
    if select.order_part:
        data = apply_order_by(select.order_part, data, ctx)
    if select.limit_part:
        data = apply_limit(select.limit_part, data, ctx)
    if select.field_parts:
        data = apply_select_fields(select.field_parts, data, ctx)
    return data

def apply_command(command: Command, tables: TablesSnapshot, ctx: dict):
    if isinstance(command, Select):
        return apply_select(command, tables, ctx)
    else:
        raise ValueError(f"Unsupported command type: {type(command)}")