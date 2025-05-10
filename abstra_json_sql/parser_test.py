from unittest import TestCase
from .parser import parse, parse_expression, parse_from, parse_limit, accept_keyword
from .lexer import scan
from .tokens import Token
from .ast import (
    Select,
    From,
    Wildcard,
    PlusExpression,
    FunctionCallExpression,
    SelectField,
    IntExpression,
    NameExpression,
    EqualExpression,
    StringExpression,
    Where,
    OrderBy,
    Limit,
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
                field_parts=[Wildcard()],
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

    def test_select_with_alias(self):
        tokens = scan("select foo from bar as baz")
        ast = parse(tokens)
        self.assertEqual(
            ast,
            Select(
                field_parts=[SelectField(expression=NameExpression(name="foo"))],
                from_part=From(
                    table="bar",
                    alias="baz",
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
                        OrderField(
                            expression=NameExpression(name="bar"), direction="DESC"
                        )
                    ]
                ),
            ),
        )


class ExpressionTest(TestCase):
    def test_plus_expression(self):
        exp = scan("1+1")
        ast, tokens = parse_expression(exp)
        self.assertEqual(
            ast,
            PlusExpression(
                left=IntExpression(value=1),
                right=IntExpression(value=1),
            ),
        )
        self.assertEqual(tokens, [])

    def test_equal_expression(self):
        exp = scan("name = 'John'")
        ast, tokens = parse_expression(exp)
        self.assertEqual(
            ast,
            EqualExpression(
                left=NameExpression(name="name"),
                right=StringExpression(value="John"),
            ),
        )
        self.assertEqual(tokens, [])

    def test_function_call_expression(self):
        tokens = scan("SUM(foo)")
        ast, tokens = parse_expression(tokens)
        self.assertEqual(
            ast,
            FunctionCallExpression(
                name="SUM",
                args=[NameExpression(name="foo")],
            ),
        )
        self.assertEqual(tokens, [])


class FromTest(TestCase):
    def test_simple(self):
        tokens = scan("FROM users")
        ast, tokens = parse_from(tokens)
        self.assertEqual(
            ast,
            From(
                table="users",
            ),
        )
        self.assertEqual(tokens, [])

    def test_with_alias(self):
        tokens = scan("FROM users AS u")
        ast, tokens = parse_from(tokens)
        self.assertEqual(
            ast,
            From(
                table="users",
                alias="u",
            ),
        )
        self.assertEqual(tokens, [])


class LimitTest(TestCase):
    def test_limit(self):
        tokens = scan("LIMIT 10")
        ast, tokens = parse_limit(tokens)
        self.assertEqual(
            ast,
            Limit(
                limit=10,
            ),
        )
        self.assertEqual(tokens, [])

    def test_limit_with_offset(self):
        tokens = scan("LIMIT 10 OFFSET 5")
        ast, tokens = parse_limit(tokens)
        self.assertEqual(
            ast,
            Limit(
                limit=10,
                offset=5,
            ),
        )
        self.assertEqual(tokens, [])


class AcceptKeywordTest(TestCase):
    def test_accept_keyword(self):
        tokens = [
            Token(type="keyword", value="having"),
            Token(type="name", value="foo"),
            Token(type="operator", value="<>"),
            Token(type="int", value="2"),
            Token(type="keyword", value="limit"),
            Token(type="int", value="1"),
            Token(type="keyword", value="offset"),
            Token(type="int", value="1"),
        ]
        accepted_keywords = ["HAVING", "ORDER BY", "LIMIT"]
        accepted_keywords = accept_keyword(tokens, accepted_keywords)
        self.assertEqual(accepted_keywords, ["ORDER BY", "LIMIT"])
