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
    "WITH",
    "SELECT",
    "INSERT INTO",
    "VALUES",
    "DEFAULT VALUES",
    "FROM",
    "WHERE",
    "AND",
    "AS",
    "ON",
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
    "OR",
    "INNER JOIN",
    "RIGHT OUTER JOIN",
    "LEFT OUTER JOIN",
    "LEFT JOIN",
    "RIGHT JOIN",
    "FULL JOIN",
    "FULL OUTER JOIN",
    "CROSS JOIN",
    "NATURAL JOIN",
    "JOIN",
    "LIMIT",
    "TRUE",
    "FALSE",
]
keywords.sort(reverse=True)


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
