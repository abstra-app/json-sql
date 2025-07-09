from typing import List, Optional, Literal, Union, Tuple
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
class FunctionCallExpression(Expression):
    name: str
    args: List[Expression]


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
class AndExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class OrExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class FalseExpression(Expression):
    pass


@dataclass
class TrueExpression(Expression):
    pass


@dataclass
class DefaultExpression(Expression):
    pass


@dataclass
class NotExpression(Expression):
    expression: Expression


@dataclass
class IsExpression(Expression):
    left: Expression
    right: Expression
    is_not: bool = False


@dataclass
class NullExpression(Expression):
    pass


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
class Wildcard(Ast):
    pass


@dataclass
class Join(Ast):
    table: str
    table_alias: str
    join_type: Literal["INNER", "LEFT", "RIGHT", "FULL", "CROSS", "NATURAL"]
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
class Having(Ast):
    expression: Expression


@dataclass
class SelectField(Ast):
    expression: Union[Expression, Wildcard]
    alias: Optional[str] = None


@dataclass
class OrderField(Ast):
    expression: Expression
    direction: Literal["ASC", "DESC"]


@dataclass
class OrderBy(Ast):
    fields: List[OrderField]


@dataclass
class GroupBy(Ast):
    fields: List[Expression]


@dataclass
class Limit(Ast):
    limit: int
    offset: int = 0


@dataclass
class Select(Command):
    field_parts: List[SelectField]
    from_part: Optional[From] = None
    where_part: Optional[Where] = None
    group_part: Optional[GroupBy] = None
    having_part: Optional[Where] = None
    order_part: Optional[OrderBy] = None
    limit_part: Optional[Limit] = None


@dataclass
class WithPart(Ast):
    name: str
    command: Command


@dataclass
class With(Command):
    parts: List[WithPart]
    command: Command


@dataclass
class Insert(Command):
    table_name: str
    table_alias: Optional[str] = None
    columns: Optional[List[str]] = None
    values: Optional[List[List[Expression]]] = None
    returning_fields: Optional[List[SelectField]] = None


@dataclass
class Update(Command):
    table_name: str
    changes: List[Tuple[str, Expression]]
    table_alias: Optional[str] = None
    returning_fields: Optional[List[SelectField]] = None
    where: Optional[Where] = None


@dataclass
class Delete(Command): ...
