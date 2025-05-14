from dataclasses import dataclass
from typing import Literal


operators = [
    "<>",
    ">=",
    "<=",
    "=",
    ">",
    "<",
    "!=",
    "+",
    "-",
    "*",
    "/",
]

keywords = [
    "SELECT",
    "FROM",
    "WHERE",
    "AND",
    "AS",
    "ON",
    "OR",
    "NOT",
    "IN",
    "LIKE",
    "IS NOT",
    "IS",
    "BETWEEN",
    "IS",
    "NULL",
    "EXISTS",
    "OFFSET",
    "DISTINCT",
    "ORDER BY",
    "GROUP BY",
    "HAVING",
    "ASC",
    "DESC",
    "INNER JOIN",
    "RIGHT OUTER JOIN",
    "LEFT OUTER JOIN",
    "LEFT JOIN",
    "RIGHT JOIN",
    "FULL JOIN",
    "CROSS JOIN",
    "NATURAL JOIN",
    "JOIN",
    "LIMIT",
    "TRUE",
    "FALSE",
    "NULL"
]


@dataclass
class Token:
    type: Literal[
        "name",
        "operator",
        "str",
        "int",
        "float",
        "keyword",
        "wildcard",
        "comma",
        "paren_left",
        "paren_right",
    ]
    value: str
