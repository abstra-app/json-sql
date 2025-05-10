from .tokens import Token
from typing import List, Tuple, Optional
from .ast import (
    Ast,
    Select,
    SelectField,
    Limit,
    IntExpression,
    Wildcard,
    FunctionCallExpression,
    From,
    NameExpression,
    EqualExpression,
    GroupBy,
    FloatExpression,
    FalseExpression,
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
        next_token = tokens[0]
        tokens = tokens[1:]
        if next_token.type == "int":
            stack.append(IntExpression(value=int(next_token.value)))
        elif next_token.type == "float":
            stack.append(FloatExpression(value=float(next_token.value)))
        elif next_token.type == "str":
            stack.append(StringExpression(value=next_token.value))
        elif next_token.type == "name":
            name_value = next_token.value
            if tokens and tokens[0].type == "paren_left":
                if (
                    next_token.value.lower() == "count"
                    and tokens[1].type == "wildcard"
                    and tokens[2].type == "paren_right"
                ):
                    tokens = tokens[3:]
                    stack.append(
                        FunctionCallExpression(name="count", args=[Wildcard()])
                    )
                    continue
                tokens = tokens[1:]
                args = []
                while True:
                    param_expression, tokens = parse_expression(tokens)
                    args.append(param_expression)
                    if tokens and tokens[0].type == "comma":
                        tokens = tokens[1:]
                    elif tokens and tokens[0].type == "paren_right":
                        tokens = tokens[1:]
                        break
                    else:
                        raise ValueError("Expected comma or closing parenthesis")

                stack.append(FunctionCallExpression(name=name_value, args=args))
            else:
                stack.append(NameExpression(name=name_value))
        elif next_token.type == "operator":
            operator = next_token.value
            if operator == "+":
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(PlusExpression(left=left, right=right))
            elif operator == "-":
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(MinusExpression(left=left, right=right))
            elif operator == "*":
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(MultiplyExpression(left=left, right=right))
            elif operator == "/":
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(DivideExpression(left=left, right=right))
            elif operator == "=":
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(EqualExpression(left=left, right=right))
            elif operator == "<":
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(LessThanExpression(left=left, right=right))
            elif operator == "<=":
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(LessThanOrEqualExpression(left=left, right=right))
            elif operator == ">":
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(GreaterThanExpression(left=left, right=right))
            elif operator == ">=":
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(GreaterThanOrEqualExpression(left=left, right=right))
            elif operator == "!=" or operator == "<>":
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(NotEqualExpression(left=left, right=right))
            else:
                raise ValueError(f"Unknown operator: {operator}")
        elif next_token.type == "keyword":
            if next_token.value.upper() == "AND":
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(AndExpression(left=left, right=right))
            elif next_token.value.upper() == "OR":
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(OrExpression(left=left, right=right))
            elif next_token.value.upper() == "NOT":
                tokens = tokens[1:]
                expression, tokens = parse_expression(tokens)
                stack.append(NotExpression(expression=expression))
            elif next_token.value.upper() == "TRUE":
                stack.append(TrueExpression())
                tokens = tokens[1:]
            elif next_token.value.upper() == "FALSE":
                stack.append(FalseExpression())
                tokens = tokens[1:]
            elif next_token.value.upper() == "IS":
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(IsExpression(left=left, right=right, is_not=False))
            elif next_token.value.upper() == "IS NOT":
                left = stack.pop()
                right, tokens = parse_expression(tokens)
                stack.append(IsExpression(left=left, right=right, is_not=True))
            elif next_token.value.upper() == "NULL":
                stack.append(NullExpression())
            else:
                tokens = [next_token] + tokens
                break
        else:
            tokens = [next_token] + tokens
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
    else:
        return From(table=table.value), tokens


def parse_fields(tokens: List[Token]) -> Tuple[List[SelectField], List[Token]]:
    if not tokens or tokens[0].type != "keyword" or tokens[0].value.upper() != "SELECT":
        raise ValueError("Expected SELECT statement")
    tokens = tokens[1:]
    fields: List[SelectField] = []
    while tokens:
        if tokens[0].type == "keyword" and tokens[0].value.upper() == "FROM":
            break
        elif tokens[0].type == "wildcard":
            fields.append(Wildcard())
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
                assert (
                    alias_token.type == "name"
                ), f"Expected alias name, got {alias_token}"
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

    accepted_keywords = accept_keyword(tokens, accepted_keywords)
    from_part, tokens = parse_from(tokens)

    accepted_keywords = accept_keyword(tokens, accepted_keywords)
    where_part, tokens = parse_where(tokens)

    accepted_keywords = accept_keyword(tokens, accepted_keywords)
    group_part, tokens = parse_group_by(tokens)

    accepted_keywords = accept_keyword(tokens, accepted_keywords)
    having_part, tokens = parse_having(tokens)

    accepted_keywords = accept_keyword(tokens, accepted_keywords)
    order_part, tokens = parse_order(tokens)

    accepted_keywords = accept_keyword(tokens, accepted_keywords)
    limit_part, tokens = parse_limit(tokens)

    return Select(
        field_parts=field_parts,
        from_part=from_part,
        where_part=where_part,
        having_part=having_part,
        order_part=order_part,
        limit_part=limit_part,
        group_part=group_part,
    ), tokens


def parse(tokens: List[Token]) -> Ast:
    select_part, tokens = parse_select(tokens)
    if tokens:
        raise ValueError(
            "Unexpected tokens after SELECT statement. Remaining tokens: " + str(tokens)
        )

    if select_part is not None:
        return select_part
    else:
        raise ValueError("Failed to parse SELECT statement")
