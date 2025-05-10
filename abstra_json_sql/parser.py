from .tokens import Token
from typing import List, Tuple
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
    FloatExpression,
    LessThanOrEqualExpression,
    NotEqualExpression,
    GreaterThanExpression,
    LessThanExpression,
    GreaterThanOrEqualExpression,
    Where,
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
    if not tokens:
        return None, tokens

    assert tokens[0].type == "keyword" and tokens[0].value.upper() == "ORDER BY", (
        "Expected ORDER BY statement, got: " + str(tokens[0])
    )
    tokens = tokens[1:]
    if not tokens:
        return None, tokens

    order_fields: List[OrderField] = []
    while tokens and tokens[0].type != "comma":
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
                right, tokens = parse_expression(tokens)
                left = stack.pop()
                stack.append(PlusExpression(left=left, right=right))
            elif operator == "-":
                right, tokens = parse_expression(tokens)
                left = stack.pop()
                stack.append(MinusExpression(left=left, right=right))
            elif operator == "*":
                right, tokens = parse_expression(tokens)
                left = stack.pop()
                stack.append(MultiplyExpression(left=left, right=right))
            elif operator == "/":
                right, tokens = parse_expression(tokens)
                left = stack.pop()
                stack.append(DivideExpression(left=left, right=right))
            elif operator == "=":
                right, tokens = parse_expression(tokens)
                left = stack.pop()
                stack.append(EqualExpression(left=left, right=right))
            elif operator == "<":
                right, tokens = parse_expression(tokens)
                left = stack.pop()
                stack.append(LessThanExpression(left=left, right=right))
            elif operator == "<=":
                right, tokens = parse_expression(tokens)
                left = stack.pop()
                stack.append(LessThanOrEqualExpression(left=left, right=right))
            elif operator == ">":
                right, tokens = parse_expression(tokens)
                left = stack.pop()
                stack.append(GreaterThanExpression(left=left, right=right))
            elif operator == ">=":
                right, tokens = parse_expression(tokens)
                left = stack.pop()
                stack.append(GreaterThanOrEqualExpression(left=left, right=right))
            elif operator == "!=" or operator == "<>":
                right, tokens = parse_expression(tokens)
                left = stack.pop()
                stack.append(NotEqualExpression(left=left, right=right))
            else:
                raise ValueError(f"Unknown operator: {operator}")
        else:
            tokens = [next_token] + tokens
            break
    if len(stack) == 1:
        return stack[0], tokens
    else:
        raise ValueError("Invalid expression: " + str(stack))


def parse_where(tokens: List[Token]) -> Tuple[Where, List[Token]]:
    if not tokens or tokens[0].type != "keyword" or tokens[0].value.upper() != "WHERE":
        return None, tokens
    tokens = tokens[1:]
    expression, tokens = parse_expression(tokens)
    return Where(expression=expression), tokens


def parse_from(tokens: List[Token]) -> Tuple[From, List[Token]]:
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
    fields: List[SelectField] = []
    while tokens and tokens[0].type != "comma":
        if tokens[0].type == "keyword" and tokens[0].value.upper() == "FROM":
            break
        if tokens[0].type == "wildcard":
            fields.append(Wildcard())
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


def parse_select(tokens: List[Token]) -> Tuple[Select, List[Token]]:
    if not tokens or tokens[0].type != "keyword" or tokens[0].value.upper() != "SELECT":
        raise ValueError("Expected SELECT statement")
    tokens = tokens[1:]
    field_parts, tokens = parse_fields(tokens)
    from_part, tokens = parse_from(tokens)
    where_part, tokens = parse_where(tokens)
    order_part, tokens = parse_order(tokens)
    limit_part, tokens = parse_limit(tokens)

    return Select(
        field_parts=field_parts,
        from_part=from_part,
        where_part=where_part,
        order_part=order_part,
        limit_part=limit_part,
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
