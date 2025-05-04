from unittest import TestCase
from .lexer import scan, Token


class TestTokens(TestCase):
    def test_simple(self):
        code = "select a from b where c = d"
        self.assertEqual(
            scan(code),
            [
                Token("keyword", "select"),
                Token("name", "a"),
                Token("keyword", "from"),
                Token("name", "b"),
                Token("keyword", "where"),
                Token("name", "c"),
                Token("operator", "="),
                Token("name", "d"),
            ],
        )

    def test_joined_expression(self):
        code = "select 1+1"
        self.assertEqual(
            scan(code),
            [
                Token("keyword", "select"),
                Token("int", "1"),
                Token("operator", "+"),
                Token("int", "1"),
            ],
        )

    def test_joined_comparison(self):
        code = "select a=b"
        self.assertEqual(
            scan(code),
            [
                Token("keyword", "select"),
                Token("name", "a"),
                Token("operator", "="),
                Token("name", "b"),
            ],
        )

    def test_str(self):
        code = "select 'foo'='bar'"
        self.assertEqual(
            scan(code),
            [
                Token("keyword", "select"),
                Token("str", "foo"),
                Token("operator", "="),
                Token("str", "bar"),
            ],
        )

    def test_escaped_str(self):
        code = "select 'foo''s name' = 'bar''s name'"
        self.assertEqual(
            scan(code),
            [
                Token("keyword", "select"),
                Token("str", "foo's name"),
                Token("operator", "="),
                Token("str", "bar's name"),
            ],
        )

    def test_tricky_escape(self):
        code = "select 'foo''' = '''bar'"
        self.assertEqual(
            scan(code),
            [
                Token("keyword", "select"),
                Token("str", "foo'"),
                Token("operator", "="),
                Token("str", "'bar"),
            ],
        )

    def test_quoted_name(self):
        code = 'select foo from "my table"'
        self.assertEqual(
            scan(code),
            [
                Token("keyword", "select"),
                Token("name", "foo"),
                Token("keyword", "from"),
                Token("name", "my table"),
            ],
        )

    def test_escaped_quoted_name(self):
        code = 'select foo from "my ""table"""'
        self.assertEqual(
            scan(code),
            [
                Token("keyword", "select"),
                Token("name", "foo"),
                Token("keyword", "from"),
                Token("name", 'my "table"'),
            ],
        )

    def test_wildcard(self):
        code = "select * from users"
        self.assertEqual(
            scan(code),
            [
                Token("keyword", "select"),
                Token("wildcard", "*"),
                Token("keyword", "from"),
                Token("name", "users"),
            ],
        )

    def test_order_by(self):
        code = "select foo from users order by bar"
        self.assertEqual(
            scan(code),
            [
                Token("keyword", "select"),
                Token("name", "foo"),
                Token("keyword", "from"),
                Token("name", "users"),
                Token("keyword", "order by"),
                Token("name", "bar"),
            ],
        )

    def test_expression(self):
        code = "1+1"
        self.assertEqual(
            scan(code), [Token("int", "1"), Token("operator", "+"), Token("int", "1")]
        )
