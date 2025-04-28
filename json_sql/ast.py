from typing import List, Optional, Literal, Union
from .types import Token
from dataclasses import dataclass
from abc import ABC

@dataclass
class Ast(ABC): ...


@dataclass
class Command(Ast): ...

@dataclass
class Expression(Ast): ...

@dataclass
class NameExpression(Expression):
    name: str




@dataclass
class StringExpression(Expression):
    value: str


@dataclass
class IntExpression(Expression):
    value: int



@dataclass
class FloatExpression(Expression):
    value: float


@dataclass
class PlusExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class MinusExpression(Expression):
    left: Expression
    right: Expression

@dataclass
class MultiplyExpression(Expression):
    left: Expression
    right: Expression

@dataclass
class DivideExpression(Expression):
    left: Expression
    right: Expression

@dataclass
class LessThanExpression(Expression):
    left: Expression
    right: Expression

@dataclass
class LessThanOrEqualExpression(Expression):
    left: Expression
    right: Expression

@dataclass
class GreaterThanExpression(Expression):
    left: Expression
    right: Expression

@dataclass
class GreaterThanOrEqualExpression(Expression):
    left: Expression
    right: Expression

@dataclass
class EqualExpression(Expression):
    left: Expression
    right: Expression

@dataclass
class NotEqualExpression(Expression):
    left: Expression
    right: Expression

@dataclass
class Join(Ast):
    table: str
    table_alias: str
    join_type: Literal["INNER", "LEFT", "RIGHT"]
    on: Expression

@dataclass
class From(Ast):
    table: str
    alias: Optional[str] = None
    join: Optional[List[Join]] = None


@dataclass
class Where(Ast):
    expression: Expression

@dataclass
class SelectField(Ast):
    expression: Expression
    alias: Optional[str] = None

@dataclass
class OrderField(Ast):
    expression: Expression
    order: Literal["ASC", "DESC"]

@dataclass
class Order(Ast):
    fields: List[OrderField]


@dataclass
class SelectWildcard(Ast):
    pass

@dataclass
class Select(Command):
    field_parts: List[Union[SelectField, SelectWildcard]]
    from_part: Optional[From] = None
    where_part: Optional[Where] = None
    order_part: Optional[Order] = None