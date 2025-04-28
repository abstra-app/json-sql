from .types import Token
from typing import List
from .ast import Ast, Select, SelectField, From, NameExpression, SelectWildcard, \
    EqualExpression, NotEqualExpression, GreaterThanExpression, LessThanExpression, \
    GreaterThanOrEqualExpression, Where, StringExpression, OrderBy, OrderField

def parse_order(tokens: List[Token]) -> List[Ast]:
    if not tokens or tokens[0].type != "keyword" or tokens[0].value.upper() != "ORDER BY":
        return None, tokens
    tokens = tokens[1:]
    order_fields = []
    while tokens and tokens[0].type == "name":
        field_name = tokens[0].value
        tokens = tokens[1:]
        
        order = "ASC"
        if tokens and tokens[0].type == "keyword" and tokens[0].value.upper() in ["ASC", "DESC"]:
            order = tokens[0].value.upper()
            tokens = tokens[1:]
        
        order_fields.append(OrderField(expression=NameExpression(name=field_name), direction=order))
        
        if tokens and tokens[0].type == "comma":
            tokens = tokens[1:]
        else:
            break
    return OrderBy(fields=order_fields), tokens


def parse_where(tokens: List[Token]) -> List[Ast]:
    if not tokens or tokens[0].type != "keyword" or tokens[0].value.upper() != "WHERE":
        return None, tokens
    
    tokens = tokens[1:]
    
    if not tokens or tokens[0].type != "name":
        raise ValueError("Expected field name after WHERE")
    
    field_name = tokens[0].value
    tokens = tokens[1:]
    
    if not tokens or tokens[0].type != "operator":
        raise ValueError("Expected operator after field name")
    
    operator = tokens[0].value
    tokens = tokens[1:]
    
    if not tokens or (tokens[0].type != "str" and tokens[0].type != "number"):
        raise ValueError(f"tokens={tokens}")
    
    value = tokens[0].value
    tokens = tokens[1:]
    
    expression = None
    if operator == "=":
        expression = EqualExpression(left=NameExpression(name=field_name), right=StringExpression(value=value))
    elif operator == "!=":
        expression = NotEqualExpression(left=NameExpression(name=field_name), right=StringExpression(value=value))
    elif operator == ">":
        expression = GreaterThanExpression(left=NameExpression(name=field_name), right=StringExpression(value=value))
    elif operator == "<":
        expression = LessThanExpression(left=NameExpression(name=field_name), right=StringExpression(value=value))
    elif operator == ">=":
        expression = GreaterThanOrEqualExpression(left=NameExpression(name=field_name), right=StringExpression(value=value))
    
    return Where(expression=expression), tokens

def parse_from(tokens: List[Token]) -> List[Ast]:
    if not tokens or tokens[0].type != "keyword" or tokens[0].value.upper() != "FROM":
        return None, tokens
    tokens = tokens[1:]
    
    if not tokens or tokens[0].type != "name":
        raise ValueError("Expected table name after FROM")
    
    table_name = tokens[0].value
    tokens = tokens[1:]
    
    alias = None
    if tokens and tokens[0].type == "name":
        alias = tokens[0].value
        tokens = tokens[1:]
    
    return From(table=table_name, alias=alias), tokens

def parse_fields(tokens: List[Token]) -> List[Ast]:
    field_parts = []
    if tokens[0].type == "wildcard":
        field_parts.append(SelectWildcard())
        tokens = tokens[1:]
    elif tokens[0].type == "name":
        field_parts.append(SelectField(expression=NameExpression(name=tokens[0].value)))
        tokens = tokens[1:]
    
    if tokens and tokens[0].type == "comma":
        tokens = tokens[1:]
    
    return field_parts, tokens
    

def parse_select(tokens: List[Token]) -> Select:
    if not tokens or tokens[0].type != "keyword" or tokens[0].value.upper() != "SELECT":
        raise ValueError("Expected SELECT statement")
    tokens = tokens[1:]
    field_parts, tokens = parse_fields(tokens)
    from_part, tokens = parse_from(tokens)
    where_part, tokens = parse_where(tokens)
    order_part, tokens = parse_order(tokens)
    
   
    return Select(
        field_parts=field_parts,
        from_part=from_part,
        where_part=where_part,
        order_part=order_part
    ), tokens


def parse(tokens: List[Token]) -> Ast:
    select_part, tokens = parse_select(tokens)
    if tokens:
        raise ValueError("Unexpected tokens after SELECT statement. Remaining tokens: " + str(tokens))
    
    if select_part is not None:
        return select_part
    else:
        raise ValueError("Failed to parse SELECT statement")