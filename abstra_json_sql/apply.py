from dataclasses import dataclass
from typing import Dict, List, Optional

from .ast import (
    AndExpression,
    Command,
    DefaultExpression,
    Delete,
    DivideExpression,
    EqualExpression,
    Expression,
    FalseExpression,
    FloatExpression,
    From,
    FunctionCallExpression,
    GreaterThanExpression,
    GreaterThanOrEqualExpression,
    GroupBy,
    Insert,
    IntExpression,
    IsExpression,
    LessThanExpression,
    LessThanOrEqualExpression,
    Limit,
    MinusExpression,
    MultiplyExpression,
    NameExpression,
    NotEqualExpression,
    NotExpression,
    NullExpression,
    OrderBy,
    OrExpression,
    PlusExpression,
    Select,
    SelectField,
    StringExpression,
    TrueExpression,
    Update,
    Where,
    Wildcard,
    With,
)
from .field_name import expression_name, field_name
from .infer import infer_expression
from .lexer import scan
from .parser import parse_expression
from .persistence import ExtendedTables
from .tables import Column, ITablesSnapshot, Table


def is_aggregate_function(name: str) -> bool:
    # Placeholder for aggregate function check
    return name.lower() in [
        "sum",
        "avg",
        "count",
        "min",
        "max",
        "every",
        "bool_or",
        "bool_and",
        "bit_or",
        "bit_and",
        "array_agg",
        "string_agg",
    ]


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
    elif isinstance(expression, FunctionCallExpression):
        if is_aggregate_function(expression.name):
            if expression.name.lower() == "count":
                assert len(expression.args) == 1, "Count function requires one argument"
                if isinstance(expression.args[0], Wildcard):
                    return len(ctx["__grouped_rows"])
                elif isinstance(expression.args[0], NameExpression):
                    return len(
                        [
                            row
                            for row in ctx["__grouped_rows"]
                            if apply_expression(expression.args[0], {**ctx, **row})
                            is not None
                            and apply_expression(expression.args[0], {**ctx, **row})
                            is not None
                        ]
                    )
            elif expression.name.lower() == "sum":
                assert len(expression.args) == 1, "Sum function requires one argument"
                return sum(
                    apply_expression(expression.args[0], {**ctx, **row})
                    for row in ctx["__grouped_rows"]
                    if apply_expression(expression.args[0], {**ctx, **row}) is not None
                    and isinstance(
                        apply_expression(expression.args[0], {**ctx, **row}),
                        (int, float),
                    )
                )
            elif expression.name.lower() == "avg":
                assert len(expression.args) == 1, "Avg function requires one argument"
                values = [
                    apply_expression(expression.args[0], {**ctx, **row})
                    for row in ctx["__grouped_rows"]
                    if apply_expression(expression.args[0], {**ctx, **row}) is not None
                    and isinstance(
                        apply_expression(expression.args[0], {**ctx, **row}),
                        (int, float),
                    )
                ]
                if not values:
                    return None
                return sum(values) / len(values)
            elif expression.name.lower() == "min":
                assert len(expression.args) == 1, "Min function requires one argument"
                values = [
                    apply_expression(expression.args[0], {**ctx, **row})
                    for row in ctx["__grouped_rows"]
                    if apply_expression(expression.args[0], {**ctx, **row}) is not None
                    and isinstance(
                        apply_expression(expression.args[0], {**ctx, **row}),
                        (int, float),
                    )
                ]
                if not values:
                    return None
                return min(values)
            elif expression.name.lower() == "max":
                assert len(expression.args) == 1, "Max function requires one argument"
                values = [
                    apply_expression(expression.args[0], {**ctx, **row})
                    for row in ctx["__grouped_rows"]
                    if apply_expression(expression.args[0], {**ctx, **row}) is not None
                    and isinstance(
                        apply_expression(expression.args[0], {**ctx, **row}),
                        (int, float),
                    )
                ]
                if not values:
                    return None
                return max(values)
            elif expression.name.lower() == "every":
                assert len(expression.args) == 1, "Every function requires one argument"
                return all(
                    apply_expression(expression.args[0], {**ctx, **row})
                    for row in ctx["__grouped_rows"]
                    if apply_expression(expression.args[0], {**ctx, **row}) is not None
                    and isinstance(
                        apply_expression(expression.args[0], {**ctx, **row}), bool
                    )
                )
            elif expression.name.lower() == "bool_or":
                assert len(expression.args) == 1, (
                    "Bool_or function requires one argument"
                )
                return any(
                    apply_expression(expression.args[0], {**ctx, **row})
                    for row in ctx["__grouped_rows"]
                    if apply_expression(expression.args[0], {**ctx, **row}) is not None
                    and isinstance(
                        apply_expression(expression.args[0], {**ctx, **row}), bool
                    )
                )
            elif expression.name.lower() == "bool_and":
                assert len(expression.args) == 1, (
                    "Bool_and function requires one argument"
                )
                return all(
                    apply_expression(expression.args[0], {**ctx, **row})
                    for row in ctx["__grouped_rows"]
                    if apply_expression(expression.args[0], {**ctx, **row}) is not None
                    and isinstance(
                        apply_expression(expression.args[0], {**ctx, **row}), bool
                    )
                )
            elif expression.name.lower() == "bit_or":
                assert len(expression.args) == 1, (
                    "Bit_or function requires one argument"
                )
                not_null_rows = [
                    row
                    for row in ctx["__grouped_rows"]
                    if apply_expression(expression.args[0], {**ctx, **row}) is not None
                    and apply_expression(expression.args[0], {**ctx, **row}) is not None
                ]
                if len(not_null_rows) == 0:
                    return None
                result_bits = apply_expression(
                    expression.args[0], {**ctx, **not_null_rows[0]}
                )
                for row in not_null_rows[1:]:
                    result_bits |= apply_expression(expression.args[0], {**ctx, **row})
                return result_bits
            elif expression.name.lower() == "bit_and":
                assert len(expression.args) == 1, (
                    "Bit_and function requires one argument"
                )
                not_null_rows = [
                    row
                    for row in ctx["__grouped_rows"]
                    if apply_expression(expression.args[0], {**ctx, **row}) is not None
                    and apply_expression(expression.args[0], {**ctx, **row}) is not None
                ]
                if len(not_null_rows) == 0:
                    return None
                result_bits = apply_expression(
                    expression.args[0], {**ctx, **not_null_rows[0]}
                )
                for row in not_null_rows[1:]:
                    result_bits &= apply_expression(expression.args[0], {**ctx, **row})
                return result_bits
            elif expression.name.lower() == "array_agg":
                assert len(expression.args) == 1, (
                    "Array_agg function requires one argument"
                )
                return [
                    apply_expression(expression.args[0], {**ctx, **row})
                    for row in ctx["__grouped_rows"]
                ]
            elif expression.name.lower() == "string_agg":
                assert len(expression.args) == 2, (
                    "String_agg function requires two arguments"
                )
                separator = apply_expression(expression.args[1], ctx)
                return separator.join(
                    str(apply_expression(expression.args[0], {**ctx, **row}))
                    for row in ctx["__grouped_rows"]
                    if apply_expression(expression.args[0], {**ctx, **row}) is not None
                    and apply_expression(expression.args[0], {**ctx, **row}) is not None
                )
            else:
                raise ValueError(f"Unknown aggregate function: {expression.name}")
        else:
            args = [apply_expression(arg, ctx) for arg in expression.args]
            if expression.name == "lower":
                assert isinstance(args[0], str), (
                    "lower function requires a string argument"
                )
                return args[0].lower()
            elif expression.name == "upper":
                assert isinstance(args[0], str), (
                    "upper function requires a string argument"
                )
                return args[0].upper()
            else:
                raise ValueError(f"Unknown function: {expression.name}")
    elif isinstance(expression, NullExpression):
        return None
    elif isinstance(expression, FalseExpression):
        return False
    elif isinstance(expression, TrueExpression):
        return True
    elif isinstance(expression, IsExpression):
        left_value = apply_expression(expression.left, ctx)
        right_value = apply_expression(expression.right, ctx)
        if expression.is_not:
            return left_value is not right_value
        else:
            return left_value is right_value
    elif isinstance(expression, NotExpression):
        value = apply_expression(expression.expression, ctx)
        if isinstance(value, bool):
            return not value
        else:
            raise ValueError(f"Not expression should return bool, not {value}")
    elif isinstance(expression, AndExpression):
        left_value = apply_expression(expression.left, ctx)
        right_value = apply_expression(expression.right, ctx)
        if isinstance(left_value, bool) and isinstance(right_value, bool):
            return left_value and right_value
        else:
            raise ValueError(
                f"Unsupported types for AND: {type(left_value)}, {type(right_value)}"
            )
    elif isinstance(expression, OrExpression):
        left_value = apply_expression(expression.left, ctx)
        right_value = apply_expression(expression.right, ctx)
        if isinstance(left_value, bool) and isinstance(right_value, bool):
            return left_value or right_value
        else:
            raise ValueError(
                f"Unsupported types for OR: {type(left_value)}, {type(right_value)}"
            )
    elif isinstance(expression, DefaultExpression):
        raise ValueError("Default expression cannot be used in expressions")
    elif isinstance(expression, Wildcard):
        raise ValueError("Wildcard cannot be used in expressions")
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


def apply_having(having: Where, data: List[dict], ctx: dict):
    result = []
    for row in data:
        value = apply_expression(having.expression, {**ctx, **row})
        if value is True:
            result.append(row)
        elif value is False:
            continue
        else:
            raise ValueError(f"Having expressions should return bool, not {value}")
    return result


def apply_order_by(order_by: OrderBy, data: List[dict], ctx: dict):
    @dataclass
    class Comparable:
        value: list

        def __lt__(self, other):
            assert isinstance(other, Comparable), "other should be Comparable"
            for i in range(len(self.value)):
                if self.value[i] is None:
                    return True
                elif other.value[i] is None:
                    return False
                if self.value[i] < other.value[i]:
                    return True
                elif self.value[i] > other.value[i]:
                    return False
            return False

        def __gt__(self, other):
            assert isinstance(other, Comparable), "other should be Comparable"
            for i in range(len(self.value)):
                if self.value[i] is None:
                    return False
                elif other.value[i] is None:
                    return True
                if self.value[i] > other.value[i]:
                    return True
                elif self.value[i] < other.value[i]:
                    return False
            return False

    sorted_data = sorted(
        data,
        key=lambda row: Comparable(
            [
                apply_expression(field.expression, {**ctx, **row})
                for field in order_by.fields
            ]
        ),
        reverse=any(field.direction == "DESC" for field in order_by.fields),
    )

    return sorted_data


def apply_group_by(group_by: GroupBy, data: List[dict], ctx: dict):
    groups: Dict[tuple, list] = {}
    for idx, row in enumerate(data):
        key = tuple(
            apply_expression(field, {**ctx, **row}) for field in group_by.fields
        )
        if key not in groups:
            groups[key] = []
        groups[key].append(row)
    if not group_by.fields:
        return [
            {
                "__grouped_rows": data,
                **{expression_name(field): None for field in group_by.fields},
            }
        ]
    return [
        {
            "__grouped_rows": rows,
            **{expression_name(field): key for field, key in zip(group_by.fields, key)},
        }
        for key, rows in groups.items()
    ]


def apply_limit(limit: Limit, data: List[dict], ctx: dict):
    start = limit.offset
    end = start + limit.limit
    return data[start:end]


def has_aggregation_fields(fields: List[SelectField]) -> bool:
    for field in fields:
        if isinstance(field.expression, FunctionCallExpression):
            if is_aggregate_function(field.expression.name):
                return True
    return False


def apply_select_fields(fields: List[SelectField], data: List[dict], ctx: dict):
    result = []
    for row in data:
        result_row = {}
        for field in fields:
            if isinstance(field.expression, Wildcard):
                for key, value in row.items():
                    assert isinstance(key, str), "Key should be a string"
                    parts = key.split(".")
                    last_part = parts[-1]
                    result_row[last_part] = value
            elif isinstance(field.expression, Expression):
                result_row[field_name(field)] = apply_expression(
                    field.expression, {**ctx, **row}
                )
            else:
                raise ValueError(f"Unsupported field type: {type(field)}")
        result.append(result_row)
    return result


def add_scope_to_keys(prefix: str, data: dict) -> dict:
    change = {f"{prefix}.{key}": value for key, value in data.items()}
    return {**data, **change}


def apply_from(
    from_part: Optional[From], tables: ITablesSnapshot, ctx: dict
) -> List[dict]:
    if from_part is None:
        return [{}]
    table = tables.get_table(from_part.table)
    if not table:
        raise ValueError(f"Table {from_part.table} not found")
    if from_part.join:
        for join in from_part.join:
            join_table = tables.get_table(join.table)
            if not join_table:
                raise ValueError(f"Table {join.table} not found")
            data = [
                {
                    **add_scope_to_keys(table.name, row),
                    **add_scope_to_keys(join_table.name, join_row),
                }
                for row in table.data
                for join_row in join_table.data
                if apply_expression(
                    join.on,
                    {
                        **ctx,
                        **add_scope_to_keys(table.name, row),
                        **add_scope_to_keys(join_table.name, join_row),
                    },
                )
            ]

            if join.join_type == "LEFT" or join.join_type == "FULL":
                left_data = [
                    {
                        **add_scope_to_keys(table.name, row),
                        **add_scope_to_keys(
                            join_table.name,
                            {join_col.name: None for join_col in join_table.columns},
                        ),
                    }
                    for row in table.data
                    if not any(
                        apply_expression(
                            join.on,
                            {
                                **ctx,
                                **add_scope_to_keys(table.name, row),
                                **add_scope_to_keys(join_table.name, join_row),
                            },
                        )
                        for join_row in join_table.data
                    )
                ]
                data.extend(left_data)
            if join.join_type == "RIGHT" or join.join_type == "FULL":
                right_data = [
                    {
                        **add_scope_to_keys(join_table.name, join_row),
                        **add_scope_to_keys(
                            table.name,
                            {table_col.name: None for table_col in table.columns},
                        ),
                    }
                    for join_row in join_table.data
                    if not any(
                        apply_expression(
                            join.on,
                            {
                                **ctx,
                                **add_scope_to_keys(table.name, row),
                                **add_scope_to_keys(join_table.name, join_row),
                            },
                        )
                        for row in table.data
                    )
                ]
                data.extend(right_data)
    else:
        data = [{**add_scope_to_keys(table.name, row)} for row in table.data]
    return data


def has_implicit_aggregation(fields: List[SelectField]) -> bool:
    for field in fields:
        if isinstance(field.expression, FunctionCallExpression):
            if is_aggregate_function(field.expression.name):
                return True
    return False


def apply_select(select: Select, tables: ITablesSnapshot, ctx: dict):
    data = apply_from(select.from_part, tables, ctx)
    if select.where_part:
        data = apply_where(select.where_part, data, ctx)
    if select.group_part:
        data = apply_group_by(select.group_part, data, ctx)
    elif has_implicit_aggregation(select.field_parts):
        data = apply_group_by(GroupBy(fields=[]), data, ctx)
    if select.having_part:
        data = apply_having(select.having_part, data, ctx)
    if select.order_part:
        data = apply_order_by(select.order_part, data, ctx)
    if select.limit_part:
        data = apply_limit(select.limit_part, data, ctx)
    if select.field_parts:
        data = apply_select_fields(select.field_parts, data, ctx)
    return data


def default_row(table: Table, ctx: dict) -> dict:
    result_row = {}
    for col in table.columns:
        exp_str = col.default
        if exp_str is None:
            continue
        exp, _ = parse_expression(scan(exp_str))
        result_row[col.name] = apply_expression(exp, ctx)

    return result_row


def apply_insert(insert: Insert, tables: ITablesSnapshot, ctx: dict):
    returning_values = []
    table = tables.get_table(insert.table_name)
    if insert.values:
        for value_set in insert.values:
            new_row = default_row(table, ctx)
            new_row.update(
                {
                    col: apply_expression(
                        value,
                        ctx,
                    )
                    for col, value in zip(insert.columns, value_set)
                    if not isinstance(value, DefaultExpression)
                }
            )
            tables.insert(insert.table_name, new_row)
            returning_values.append(new_row)
    else:
        new_row = default_row(table, ctx)
        tables.insert(insert.table_name, new_row)
        returning_values.append(new_row)

    if insert.returning_fields:
        return returning_values
    else:
        return None


def apply_update(update: Update, tables: ITablesSnapshot, ctx: dict):
    returning_values = []
    table = tables.get_table(update.table_name)

    selected = [
        (idx, row)
        for idx, row in enumerate(table.data)
        if update.where is None
        or apply_expression(update.where.expression, {**ctx, **row}) is True
    ]
    for idx, row in selected:
        change = {
            col: apply_expression(
                exp,
                {**ctx, **row},
            )
            for col, exp in update.changes
            if not isinstance(exp, DefaultExpression)
        }
        tables.update(update.table_name, idx, change)
    returning_values.append(table.data[idx])

    if update.returning_fields:
        return returning_values
    else:
        return None


def apply_delete(delete: Delete, tables: ITablesSnapshot, ctx: dict):
    returning_values = []
    table = tables.get_table(delete.table_name)

    selected = [
        (idx, row)
        for idx, row in enumerate(table.data)
        if delete.where is None
        or apply_expression(delete.where.expression, {**ctx, **row}) is True
    ]
    tables.delete(delete.table_name, [idx for idx, _ in selected])
    returning_values.extend([row for _, row in selected])

    if delete.returning_fields:
        return returning_values
    else:
        return None


def apply_with(with_clause: With, tables: ITablesSnapshot, ctx: dict):
    extra_tables: List[Table] = []
    for part in with_clause.parts:
        tables = ExtendedTables(tables, extra_tables)
        data = apply_command(part.command, tables, ctx)
        assert isinstance(part.command, Select), "With parts should be Select commands"
        extra_table = Table(
            name=part.name,
            columns=[
                Column(
                    name=field_name(field),
                    schema=infer_expression(field.expression, ctx),
                )
                for field in part.command.field_parts
            ],
            data=data,
        )
        extra_tables.append(extra_table)

    tables = ExtendedTables(tables, extra_tables)
    return apply_command(with_clause.command, tables, ctx)


def apply_command(command: Command, tables: ITablesSnapshot, ctx: dict):
    if isinstance(command, Select):
        return apply_select(command, tables, ctx)
    elif isinstance(command, With):
        return apply_with(command, tables, ctx)
    elif isinstance(command, Insert):
        return apply_insert(command, tables, ctx)
    elif isinstance(command, Update):
        return apply_update(command, tables, ctx)
    elif isinstance(command, Delete):
        return apply_delete(command, tables, ctx)
    else:
        raise ValueError(f"Unsupported command type: {type(command)}")
