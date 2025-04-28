from unittest import TestCase
from .parser import parse
from .lexer import scan
from .ast import (
    Select,
    From,
    SelectWildcard,
    SelectField,
    NameExpression,
    EqualExpression,
    StringExpression,
    Where,
    OrderBy,
    OrderField,
)


class ParserTest(TestCase):
    def test_select_literal(self):
        tokens = scan("SELECT foo")
        ast = parse(tokens)
        self.assertEqual(
            ast,
            Select(
                field_parts=[SelectField(expression=NameExpression(name="foo"))],
                from_part=None,
            ),
        )

    def test_select_wildcard(self):
        tokens = scan("SELECT * FROM users")
        ast = parse(tokens)
        self.assertEqual(
            ast,
            Select(
                field_parts=[SelectWildcard()],
                from_part=From(
                    table="users",
                ),
            ),
        )

    def test_select_with_field(self):
        tokens = scan("SELECT name FROM users")
        ast = parse(tokens)
        self.assertEqual(
            ast,
            Select(
                field_parts=[SelectField(expression=NameExpression(name="name"))],
                from_part=From(
                    table="users",
                ),
            ),
        )

    def test_select_where(self):
        self.maxDiff = None
        tokens = scan("SELECT name FROM users WHERE name = 'John'")
        ast = parse(tokens)
        self.assertEqual(
            ast,
            Select(
                field_parts=[SelectField(expression=NameExpression(name="name"))],
                from_part=From(
                    table="users",
                ),
                where_part=Where(
                    expression=EqualExpression(
                        left=NameExpression(name="name"),
                        right=StringExpression(value="John"),
                    )
                ),
            ),
        )

    def test_select_order(self):
        tokens = scan("SELECT foo FROM users ORDER BY bar DESC")
        ast = parse(tokens)
        self.assertEqual(
            ast,
            Select(
                field_parts=[SelectField(expression=NameExpression(name="foo"))],
                from_part=From(
                    table="users",
                ),
                order_part=OrderBy(
                    fields=[
                        OrderField(expression=NameExpression(name="bar"), direction="DESC")
                    ]
                ),
            ),
        )
