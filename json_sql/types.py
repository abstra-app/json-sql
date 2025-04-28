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
]

keywords = [
    "SELECT",
    "FROM",
    "WHERE",
    "AND",
    "OR",
    "NOT",
    "IN",
    "LIKE",
    "BETWEEN",
    "IS",
    "NULL",
    "EXISTS",
    "DISTINCT",
    "ORDER BY",
    "GROUP BY",
    "HAVING",
    "ASC",
    "DESC",
    "INNER JOIN",
    "LEFT JOIN",
    "RIGHT JOIN",
    "FULL JOIN",
    "CROSS JOIN",
    "NATURAL JOIN",
    "JOIN",
]


@dataclass
class Token:
    type: Literal["name", "operator", "str", "int", "float", "keyword", "wildcard"]
    value: str