from .tokens import Token
from typing import List, Tuple, Optional, Union
from .ast import (
    Ast,
    Select,
    Delete,
    SelectField,
    Limit,
    IntExpression,
    Wildcard,
    Update,
    FunctionCallExpression,
    With,
    WithPart,
    From,
    Insert,
    NameExpression,
    EqualExpression,
    GroupBy,
    FloatExpression,
    FalseExpression,
    DefaultExpression,
    NullExpression,
    IsExpression,
    TrueExpression,
    NotExpression,
    LessThanOrEqualExpression,
    NotEqualExpression,
    GreaterThanExpression,
    LessThanExpression,
    AndExpression,
    OrExpression,
    GreaterThanOrEqualExpression,
    Where,
    Having,
    StringExpression,
    OrderBy,
    OrderField,
    PlusExpression,
    MinusExpression,
    Join,
    MultiplyExpression,
    DivideExpression,
    Expression,
)


def parse_order(tokens: List[Token]) -> Tuple[OrderBy, List[Token]]:
    if (
        not tokens
        or tokens[0].type != "keyword"
        or tokens[0].value.upper() != "ORDER BY"
    ):
        return None, tokens

    tokens = tokens[1:]
    assert tokens, "Expected ORDER BY fields"

    order_fields: List[OrderField] = []
    while tokens:
        if tokens[0].type == "keyword" and tokens[0].value.upper() == "LIMIT":
            break
        elif tokens[0].type == "keyword" and tokens[0].value.upper() == "HAVING":
            break
        exp, tokens = parse_expression(tokens)
        if (
            tokens
            and tokens[0].type == "keyword"
            and tokens[0].value.upper()
            in [
                "ASC",
                "DESC",
            ]
        ):
            direction = tokens[0].value.upper()
            tokens = tokens[1:]
        else:
            direction = "ASC"
        order_fields.append(OrderField(expression=exp, direction=direction))

    return OrderBy(fields=order_fields), tokens


def parse_expression(tokens: List[Token]) -> Tuple[Expression, List[Token]]:
    stack = []

    while tokens:
        if tokens[0].type == "paren_left":
            tokens = tokens[1:]

            if tokens[0].value.upper() in [
                "SELECT",
                "WITH",
                "INSERT",
                "UPDATE",
                "DELETE",
            ]:
                subquery, tokens = parse_command(tokens)
                stack.append(subquery)
            else:
                expression, tokens = parse_expression(tokens)
                stack.append(expression)
            if tokens and tokens[0].type == "paren_right":
                tokens = tokens[1:]
                break
            else:
                raise ValueError("Expected closing parenthesis")
        elif tokens[0].type == "paren_right":
            break
        elif tokens[0].type == "keyword":
            if tokens[0].value.upper() == "AND":
                tokens = tokens[1:]
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(AndExpression(left=left, right=right))
            elif tokens[0].value.upper() == "OR":
                tokens = tokens[1:]
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(OrExpression(left=left, right=right))
            elif tokens[0].value.upper() == "NOT":
                tokens = tokens[1:]
                expression, tokens = parse_expression(tokens)
                stack.append(NotExpression(expression=expression))
            elif tokens[0].value.upper() == "TRUE":
                tokens = tokens[1:]
                stack.append(TrueExpression())
            elif tokens[0].value.upper() == "FALSE":
                tokens = tokens[1:]
                stack.append(FalseExpression())
            elif tokens[0].value.upper() == "IS":
                tokens = tokens[1:]
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(IsExpression(left=left, right=right, is_not=False))
            elif tokens[0].value.upper() == "IS NOT":
                tokens = tokens[1:]
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(IsExpression(left=left, right=right, is_not=True))
            elif tokens[0].value.upper() == "NULL":
                tokens = tokens[1:]
                stack.append(NullExpression())
            else:
                break
        elif tokens[0].type == "int":
            stack.append(IntExpression(value=int(tokens[0].value)))
            tokens = tokens[1:]
        elif tokens[0].type == "float":
            stack.append(FloatExpression(value=float(tokens[0].value)))
            tokens = tokens[1:]
        elif tokens[0].type == "str":
            stack.append(StringExpression(value=tokens[0].value))
            tokens = tokens[1:]
        elif tokens[0].type == "name":
            name_value = tokens[0].value
            tokens = tokens[1:]

            if not tokens or tokens[0].type != "paren_left":
                stack.append(NameExpression(name=name_value))
                continue
            else:
                if (
                    name_value.lower() == "count"
                    and tokens[1].type == "wildcard"
                    and tokens[2].type == "paren_right"
                ):
                    tokens = tokens[3:]
                    stack.append(
                        FunctionCallExpression(name="count", args=[Wildcard()])
                    )
                else:
                    tokens = tokens[1:]
                    args = []
                    while True:
                        param_expression, tokens = parse_expression(tokens)
                        args.append(param_expression)
                        if tokens[0].type == "comma":
                            tokens = tokens[1:]
                            continue
                        elif tokens[0].type == "paren_right":
                            tokens = tokens[1:]
                            break
                        else:
                            raise ValueError("Expected comma or closing parenthesis")

                    stack.append(FunctionCallExpression(name=name_value, args=args))
            print(f"{stack=}")
            print(f"{tokens=}")
            continue
        elif tokens[0].type == "operator":
            operator = tokens[0].value
            print(f"Operator: {operator}")
            if operator == "+":
                tokens = tokens[1:]
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(PlusExpression(left=left, right=right))
            elif operator == "-":
                tokens = tokens[1:]
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(MinusExpression(left=left, right=right))
            elif operator == "*":
                tokens = tokens[1:]
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(MultiplyExpression(left=left, right=right))
            elif operator == "/":
                tokens = tokens[1:]
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(DivideExpression(left=left, right=right))
            elif operator == "=":
                tokens = tokens[1:]
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(EqualExpression(left=left, right=right))
            elif operator == "<":
                tokens = tokens[1:]
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(LessThanExpression(left=left, right=right))
            elif operator == "<=":
                tokens = tokens[1:]
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(LessThanOrEqualExpression(left=left, right=right))
            elif operator == ">":
                tokens = tokens[1:]
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(GreaterThanExpression(left=left, right=right))
            elif operator == ">=":
                tokens = tokens[1:]
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(GreaterThanOrEqualExpression(left=left, right=right))
            elif operator == "!=" or operator == "<>":
                tokens = tokens[1:]
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(NotEqualExpression(left=left, right=right))
            else:
                raise ValueError(f"Unknown operator: {operator}")
        else:
            break
    if len(stack) == 1:
        return stack[0], tokens
    else:
        raise ValueError("Invalid expression: " + str(stack))


def parse_where(tokens: List[Token]) -> Tuple[Optional[Where], List[Token]]:
    if not tokens or tokens[0].type != "keyword" or tokens[0].value.upper() != "WHERE":
        return None, tokens
    tokens = tokens[1:]
    expression, tokens = parse_expression(tokens)
    return Where(expression=expression), tokens


def parse_having(tokens: List[Token]) -> Tuple[Optional[Where], List[Token]]:
    if not tokens or tokens[0].type != "keyword" or tokens[0].value.upper() != "HAVING":
        return None, tokens
    tokens = tokens[1:]
    expression, tokens = parse_expression(tokens)
    return Having(expression=expression), tokens


def parse_group_by(tokens: List[Token]) -> Tuple[Optional[GroupBy], List[Token]]:
    if (
        not tokens
        or tokens[0].type != "keyword"
        or tokens[0].value.upper() != "GROUP BY"
    ):
        return None, tokens
    tokens = tokens[1:]
    group_fields: List[Expression] = []
    while tokens:
        if tokens[0].type == "keyword" and tokens[0].value.upper() == "ORDER BY":
            break
        elif tokens[0].type == "keyword" and tokens[0].value.upper() == "LIMIT":
            break
        elif tokens[0].type == "keyword" and tokens[0].value.upper() == "HAVING":
            break
        elif tokens[0].type == "comma":
            tokens = tokens[1:]
        else:
            exp, tokens = parse_expression(tokens)
            group_fields.append(exp)
    return GroupBy(fields=group_fields), tokens


def parse_join(tokens: List[Token]) -> Tuple[Optional[Join], List[Token]]:
    if len(tokens) == 0:
        return None, tokens

    # JOIN
    if tokens[0].type == "keyword" and tokens[0].value.upper() in [
        "INNER JOIN",
        "JOIN",
    ]:
        join_type = "INNER"
        tokens = tokens[1:]
    elif tokens[0].type == "keyword" and tokens[0].value.upper() in [
        "LEFT JOIN",
        "LEFT OUTER JOIN",
    ]:
        join_type = "LEFT"
        tokens = tokens[1:]
    elif tokens[0].type == "keyword" and tokens[0].value.upper() in [
        "RIGHT JOIN",
        "RIGHT OUTER JOIN",
    ]:
        join_type = "RIGHT"
        tokens = tokens[1:]
    elif tokens[0].type == "keyword" and tokens[0].value.upper() in [
        "FULL JOIN",
        "FULL OUTER JOIN",
    ]:
        join_type = "FULL"
        tokens = tokens[1:]
    elif tokens[0].type == "keyword" and tokens[0].value.upper() in ["CROSS JOIN"]:
        join_type = "CROSS"
        tokens = tokens[1:]
    elif tokens[0].type == "keyword" and tokens[0].value.upper() in ["NATURAL JOIN"]:
        join_type = "NATURAL"
        tokens = tokens[1:]
    else:
        return None, tokens

    # Table
    table = tokens[0]
    assert table.type == "name", f"Expected table name, got {table}"
    tokens = tokens[1:]

    # AS
    if (
        len(tokens) > 0
        and tokens[0].type == "keyword"
        and tokens[0].value.upper() == "AS"
    ):
        tokens = tokens[1:]
        alias_token = tokens[0]
        assert alias_token.type == "name", f"Expected alias name, got {alias_token}"
        tokens = tokens[1:]
    else:
        alias_token = None

    # ON
    if (
        len(tokens) > 0
        and tokens[0].type == "keyword"
        and tokens[0].value.upper() == "ON"
    ):
        tokens = tokens[1:]
        on_expression, tokens = parse_expression(tokens)
    else:
        raise ValueError("Expected ON clause after JOIN")

    return Join(
        table=table.value,
        table_alias=alias_token.value if alias_token else None,
        join_type=join_type,
        on=on_expression,
    ), tokens


def parse_from(tokens: List[Token]) -> Tuple[Optional[From], List[Token]]:
    if len(tokens) == 0:
        return None, tokens
    if tokens[0].type != "keyword" or tokens[0].value.upper() != "FROM":
        raise ValueError("Expected FROM statement")

    tokens = tokens[1:]
    table = tokens[0]
    assert table.type == "name", f"Expected table name, got {table}"

    tokens = tokens[1:]

    if (
        len(tokens) > 0
        and tokens[0].type == "keyword"
        and tokens[0].value.upper() == "AS"
    ):
        tokens = tokens[1:]
        alias_token = tokens[0]
        assert alias_token.type == "name", f"Expected alias name, got {alias_token}"
        tokens = tokens[1:]
        return From(table=table.value, alias=alias_token.value), tokens

    join: List[Join] = []
    while True:
        if len(tokens) == 0:
            break
        j, tokens = parse_join(tokens)
        if j is None:
            break
        join.append(j)

    if len(join) == 0:
        return From(table=table.value), tokens
    else:
        return From(table=table.value, join=join), tokens


def parse_fields(tokens: List[Token]) -> Tuple[List[SelectField], List[Token]]:
    if (
        not tokens
        or tokens[0].type != "keyword"
        or tokens[0].value.upper()
        not in [
            "SELECT",
            "RETURNING",
        ]
    ):
        raise ValueError(f"Expected SELECT or RETURNING statement, got {tokens[0]}")
    tokens = tokens[1:]
    fields: List[SelectField] = []
    while tokens:
        if tokens[0].type == "keyword" and tokens[0].value.upper() == "FROM":
            break
        elif tokens[0].type == "wildcard":
            fields.append(SelectField(Wildcard()))
            tokens = tokens[1:]
        elif tokens[0].type == "comma":
            tokens = tokens[1:]
        else:
            exp, tokens = parse_expression(tokens)
            field = SelectField(expression=exp)
            if (
                tokens
                and tokens[0].type == "keyword"
                and tokens[0].value.upper() == "AS"
            ):
                tokens = tokens[1:]
                alias_token = tokens[0]
                assert alias_token.type == "name", (
                    f"Expected alias name, got {alias_token}"
                )
                field.alias = alias_token.value
                tokens = tokens[1:]
            fields.append(field)
    return fields, tokens


def parse_limit(tokens: List[Token]) -> Tuple[Limit, List[Token]]:
    if not tokens or tokens[0].type != "keyword" or tokens[0].value.upper() != "LIMIT":
        return None, tokens

    tokens = tokens[1:]
    limit_token = tokens[0]
    assert limit_token.type == "int", f"Expected limit value, got {limit_token}"
    limit_value = limit_token.value
    limit_int = int(limit_value)
    tokens = tokens[1:]

    if tokens and tokens[0].type == "keyword" and tokens[0].value.upper() == "OFFSET":
        tokens = tokens[1:]
        offset_token = tokens[0]
        assert offset_token.type == "int", f"Expected offset value, got {offset_token}"
        offset_value = offset_token.value
        offset_int = int(offset_value)
        tokens = tokens[1:]
        return Limit(limit=limit_int, offset=offset_int), tokens
    else:
        return Limit(limit=limit_int), tokens


def accept_keyword(tokens: List[Token], accepted: List[str]):
    if len(tokens) == 0:
        return accepted

    first_token = tokens[0]
    for idx, accepted_keyword in enumerate(accepted):
        if (
            idx == 0
            and first_token.type == "keyword"
            and first_token.value.upper() == accepted_keyword.upper()
        ):
            return accepted[1:]
        elif first_token.value.upper() == accepted_keyword.upper():
            return accepted
    raise ValueError(
        f"Unexpected token {first_token} after {accepted}. Expected one of {accepted}"
    )


def parse_select(tokens: List[Token]) -> Tuple[Select, List[Token]]:
    accepted_keywords = [
        "SELECT",
        "FROM",
        "WHERE",
        "GROUP BY",
        "HAVING",
        "ORDER BY",
        "LIMIT",
    ]

    accepted_keywords = accept_keyword(tokens, accepted_keywords)
    field_parts, tokens = parse_fields(tokens)

    if tokens and tokens[0].type != "paren_right":
        accepted_keywords = accept_keyword(tokens, accepted_keywords)
        from_part, tokens = parse_from(tokens)
    else:
        from_part = None

    if tokens and tokens[0].type != "paren_right":
        accepted_keywords = accept_keyword(tokens, accepted_keywords)
        where_part, tokens = parse_where(tokens)
    else:
        where_part = None

    if tokens and tokens[0].type != "paren_right":
        accepted_keywords = accept_keyword(tokens, accepted_keywords)
        group_part, tokens = parse_group_by(tokens)
    else:
        group_part = None

    if tokens and tokens[0].type != "paren_right":
        accepted_keywords = accept_keyword(tokens, accepted_keywords)
        having_part, tokens = parse_having(tokens)
    else:
        having_part = None

    if tokens and tokens[0].type != "paren_right":
        accepted_keywords = accept_keyword(tokens, accepted_keywords)
        order_part, tokens = parse_order(tokens)
    else:
        order_part = None

    if tokens and tokens[0].type != "paren_right":
        accepted_keywords = accept_keyword(tokens, accepted_keywords)
        limit_part, tokens = parse_limit(tokens)
    else:
        limit_part = None

    return Select(
        field_parts=field_parts,
        from_part=from_part,
        where_part=where_part,
        having_part=having_part,
        order_part=order_part,
        limit_part=limit_part,
        group_part=group_part,
    ), tokens


def parse_insert(tokens: List[Token]) -> Tuple[Ast, List[Token]]:
    if (
        not tokens
        or tokens[0].type != "keyword"
        or tokens[0].value.upper() != "INSERT INTO"
    ):
        raise ValueError("Expected INSERT INTO statement")

    tokens = tokens[1:]
    table = tokens[0]
    assert table.type == "name", f"Expected table name, got {table}"
    tokens = tokens[1:]

    if not tokens:
        raise ValueError("Expected VALUES or DEFAULT VALUES after INSERT INTO")

    if tokens[0].type == "keyword" and tokens[0].value.upper() == "AS":
        tokens = tokens[1:]
        alias_token = tokens[0]
        assert alias_token.type == "name", f"Expected alias name, got {alias_token}"
        alias_name = alias_token.value
        tokens = tokens[1:]
    else:
        alias_name = None

    if tokens[0].type == "paren_left":
        tokens = tokens[1:]
        columns: List[str] = []
        while True:
            if tokens[0].type == "paren_right":
                tokens = tokens[1:]
                break
            elif tokens[0].type == "comma":
                tokens = tokens[1:]
            else:
                column = tokens[0]
                assert column.type == "name", f"Expected column name, got {column}"
                columns.append(column.value)
                tokens = tokens[1:]
        if not columns:
            raise ValueError("Expected column names after INSERT INTO")
    else:
        columns = None

    if tokens[0].type == "keyword" and tokens[0].value.upper() == "VALUES":
        tokens = tokens[1:]
        rows: List[List[Expression]] = []
        while tokens:
            if tokens[0].type == "paren_left":
                tokens = tokens[1:]
                value_expressions: List[Expression] = []
                while True:
                    if tokens[0].type == "paren_right":
                        tokens = tokens[1:]
                        break
                    elif tokens[0].type == "comma":
                        tokens = tokens[1:]
                    elif (
                        tokens[0].type == "keyword"
                        and tokens[0].value.upper() == "DEFAULT"
                    ):
                        tokens = tokens[1:]
                        value_expressions.append(DefaultExpression())
                    else:
                        exp, tokens = parse_expression(tokens)
                        value_expressions.append(exp)
                rows.append(value_expressions)
            elif tokens[0].type == "keyword" and tokens[0].value.upper() in [
                "SELECT",
                "WITH",
                "INSERT",
                "UPDATE",
                "DELETE",
            ]:
                subquery, tokens = parse_command(tokens)
                rows.append(subquery)
            elif tokens[0].type == "comma":
                tokens = tokens[1:]
            else:
                break
        if not rows:
            raise ValueError("Expected VALUES after INSERT INTO")
    elif tokens[0].type == "keyword" and tokens[0].value.upper() == "DEFAULT VALUES":
        tokens = tokens[1:]
        rows = None
    else:
        raise ValueError("Expected VALUES or DEFAULT VALUES after INSERT INTO")

    if (
        tokens
        and tokens[0].type == "keyword"
        and tokens[0].value.upper() == "RETURNING"
    ):
        returning_fields, tokens = parse_fields(tokens)
    else:
        returning_fields = None
    return Insert(
        table_name=table.value,
        table_alias=alias_name,
        columns=columns,
        values=rows,
        returning_fields=returning_fields,
    ), tokens


def parse_update(tokens: List[Token]) -> Tuple[Ast, List[Token]]:
    if not tokens or tokens[0].type != "keyword" or tokens[0].value.upper() != "UPDATE":
        raise ValueError("Expected UPDATE statement")
    tokens = tokens[1:]

    table_token = tokens[0]
    assert table_token.type == "name"
    tokens = tokens[1:]

    if tokens[0].type == "keyword" and tokens[0].value.upper() == "AS":
        assert tokens[1].type == "name", "Expecting table alias"
        table_alias = tokens[1].value
        tokens = tokens[2:]
    else:
        table_alias = None

    assert tokens[0].type == "keyword" and tokens[0].value.upper() == "SET", (
        f"Expecting SET assignments, got '{tokens[0].value}'"
    )
    tokens = tokens[1:]

    changes = []
    while True:
        assert tokens[0].type == "name", "Expecting a name"
        col_name = tokens[0].value
        tokens = tokens[1:]

        assert tokens[0].type == "operator" and tokens[0].value == "="
        tokens = tokens[1:]

        exp, tokens = parse_expression(tokens)
        changes.append((col_name, exp))

        if len(tokens) > 0 and tokens[0].type == "comma":
            tokens = tokens[1:]
            continue
        else:
            break

    where, tokens = parse_where(tokens)

    if (
        len(tokens) > 0
        and tokens[0].type == "keyword"
        and tokens[0].value.upper() == "RETURNING"
    ):
        fields, tokens = parse_fields(tokens)
    else:
        fields = None

    return Update(
        table_name=table_token.value,
        table_alias=table_alias,
        changes=changes,
        where=where,
        returning_fields=fields,
    ), tokens


def parse_delete(tokens: List[Token]) -> Tuple[Ast, List[Token]]:
    if (
        not tokens
        or tokens[0].type != "keyword"
        or tokens[0].value.upper() != "DELETE FROM"
    ):
        raise ValueError("Expected DELETE FROM statement")
    tokens = tokens[1:]

    table_token = tokens[0]
    assert table_token.type == "name"
    tokens = tokens[1:]

    where, tokens = parse_where(tokens)

    if (
        len(tokens) > 0
        and tokens[0].type == "keyword"
        and tokens[0].value.upper() == "RETURNING"
    ):
        fields, tokens = parse_fields(tokens)
    else:
        fields = None

    return Delete(
        table_name=table_token.value,
        where=where,
        returning_fields=fields,
    ), tokens


def parse_with(tokens: List[Token]) -> Tuple[Optional[Ast], List[Token]]:
    if not tokens or tokens[0].type != "keyword" or tokens[0].value.upper() != "WITH":
        return None, tokens
    tokens = tokens[1:]
    parts: List[WithPart] = []

    while True:
        name = tokens[0]
        assert name.type == "name", f"Expected name, got {name}"
        tokens = tokens[1:]

        as_token = tokens[0]
        assert as_token.type == "keyword" and as_token.value.upper() == "AS", (
            f"Expected AS, got {as_token}"
        )
        tokens = tokens[1:]

        cmd, tokens = parse_expression(tokens)
        parts.append(WithPart(name=name.value, command=cmd))

        print(tokens)

        if tokens[0].type == "comma":
            tokens = tokens[1:]
            continue
        else:
            break

    command, tokens = parse_command(tokens)
    return With(parts=parts, command=command), tokens


def parse_command(tokens: List[Token]) -> Tuple[Union[With, Select], List[Token]]:
    if tokens[0].type == "keyword" and tokens[0].value.upper() == "WITH":
        return parse_with(tokens)
    elif tokens[0].type == "keyword" and tokens[0].value.upper() == "SELECT":
        return parse_select(tokens)
    elif tokens[0].type == "keyword" and tokens[0].value.upper() == "INSERT INTO":
        return parse_insert(tokens)
    elif tokens[0].type == "keyword" and tokens[0].value.upper() == "UPDATE":
        return parse_update(tokens)
    elif tokens[0].type == "keyword" and tokens[0].value.upper() == "DELETE FROM":
        return parse_delete(tokens)
    else:
        raise ValueError(
            f"Expected WITH or SELECT statement, got {tokens[0].type}: {tokens[0].value}"
        )


def parse(tokens: List[Token]) -> Ast:
    select_part, tokens = parse_command(tokens)
    if tokens:
        raise ValueError(
            "Unexpected tokens after SELECT statement. Remaining tokens: " + str(tokens)
        )

    if select_part is not None:
        return select_part
    else:
        raise ValueError("Failed to parse SELECT statement")
