from dataclasses import dataclass
from typing import List, Literal, Optional

from .ast import (
    AndExpression,
    Command,
    Delete,
    EqualExpression,
    Expression,
    Insert,
    NameExpression,
    Select,
    Update,
)
from .lexer import scan
from .parser import parse, parse_expression
from .tables import ITablesSnapshot

RuleCommand = Literal["SELECT", "INSERT", "UPDATE", "DELETE"]


def includes_expression(main: Expression, sub: Expression) -> bool:
    if main == sub:
        return True
    elif isinstance(main, AndExpression):
        return includes_expression(main.left, sub) or includes_expression(
            main.right, sub
        )
    return False


def validate_insert_condition(condition: Expression) -> bool:
    if isinstance(condition, AndExpression):
        return validate_insert_condition(condition.left) and validate_insert_condition(
            condition.right
        )
    elif isinstance(condition, EqualExpression):
        if isinstance(condition.left, NameExpression):
            return True
    return False


@dataclass
class Rule:
    type: Literal["GRANT", "REVOKE"]
    command: RuleCommand
    table_name: str
    condition: Optional[str] = None

    def __post_init__(self):
        if self.command == "INSERT" and self.condition is not None:
            cond_exp, _ = parse_expression(scan(self.condition))
            if not validate_insert_condition(cond_exp):
                raise NotImplementedError(
                    "Only simple equality conditions are supported for INSERT rules."
                )

    def condition_met(self, command: Command) -> bool:
        if self.condition is None:
            return True
        if isinstance(command, Select) and self.command == "SELECT":
            cond_exp, _ = parse_expression(scan(self.condition))
            if command.where_part is None:
                return False
            return includes_expression(command.where_part.expression, cond_exp)
        elif isinstance(command, Update) and self.command == "UPDATE":
            cond_exp, _ = parse_expression(scan(self.condition))
            if command.where is None:
                return False
            return includes_expression(command.where.expression, cond_exp)
        elif isinstance(command, Delete) and self.command == "DELETE":
            cond_exp, _ = parse_expression(scan(self.condition))
            if command.where is None:
                return False
            return includes_expression(command.where.expression, cond_exp)
        elif isinstance(command, Insert) and self.command == "INSERT":
            cond_exp, _ = parse_expression(scan(self.condition))
            if command.columns is None:
                return False

            for value in command.values:
                insert_expression = AndExpression.from_list(
                    [
                        EqualExpression(NameExpression(field), val)
                        for field, val in zip(command.columns, value)
                    ]
                )
                if includes_expression(insert_expression, cond_exp):
                    return True
        return False

    def check(self, command: Command) -> Literal["ALLOW", "DENY", "NO_MATCH"]:
        if isinstance(command, Select) and self.command == "SELECT":
            if self.table_name in command.get_tables():
                if self.condition_met(command):
                    return "ALLOW" if self.type == "GRANT" else "DENY"
                else:
                    return "NO_MATCH"
        elif isinstance(command, Insert) and self.command == "INSERT":
            if self.table_name == command.table_name:
                if self.condition_met(command):
                    return "ALLOW" if self.type == "GRANT" else "DENY"
                else:
                    return "NO_MATCH"
        elif isinstance(command, Update) and self.command == "UPDATE":
            if self.table_name == command.table_name:
                if self.condition_met(command):
                    return "ALLOW" if self.type == "GRANT" else "DENY"
                else:
                    return "NO_MATCH"
        elif isinstance(command, Delete) and self.command == "DELETE":
            if self.table_name == command.table_name:
                if self.condition_met(command):
                    return "ALLOW" if self.type == "GRANT" else "DENY"
                else:
                    return "NO_MATCH"
        return "NO_MATCH"


class Permissions:
    default: bool
    rules: List[Rule]

    def __init__(self, default: bool = False):
        self.default = default
        self.rules = []

    def grant(
        self, command: RuleCommand, table_name: str, condition: Optional[str] = None
    ) -> "ITablesSnapshot":
        self.rules.append(Rule("GRANT", command, table_name, condition))
        return self

    def revoke(
        self, command: RuleCommand, table_name: str, condition: Optional[str] = None
    ) -> "ITablesSnapshot":
        self.rules.append(Rule("REVOKE", command, table_name, condition))
        return self

    def allowed(self, sql: str):
        cmd = parse(scan(sql))
        allowed = self.default
        for rule in self.rules:
            result = rule.check(cmd)
            if result == "ALLOW":
                allowed = True
            elif result == "DENY":
                allowed = False
        return allowed
