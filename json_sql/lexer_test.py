from unittest import TestCase
from .lexer import extract_tokens, Token

class TestTokens(TestCase):
    def test_simple(self):
        code = "select a from b where c = d"
        self.assertEqual(extract_tokens(code), [
            Token("name", "select"),
            Token("name", "a"),
            Token("name", "from"), 
            Token("name", "b"),
            Token("name", "where"),
            Token("name", "c"),
            Token("operator", "="),
            Token("name", "d"),
        ])
    
    def test_joined_comparison(self):
        code = "select a=b"
        self.assertEqual(extract_tokens(code), [
            Token("name", "select"),
            Token("name", "a"),
            Token("operator", "="),
            Token("name", "b")
        ])
    
    def test_str(self):
        code = "select 'foo'='bar'"
        self.assertEqual(extract_tokens(code), [
            Token("name", "select"),
            Token("str", "foo"),
            Token("operator", "="),
            Token("str", "bar")
        ])
    
    def test_escaped_str(self):
        code = "select 'foo''s name' = 'bar''s name'"
        self.assertEqual(extract_tokens(code), [
            Token("name", "select"),
            Token("str", "foo's name"),
            Token("operator", "="),
            Token("str", "bar's name")
        ])

    def test_tricky_escape(self):
        code = "select 'foo''' = '''bar'"
        self.assertEqual(extract_tokens(code), [
            Token("name", "select"),
            Token("str", "foo'"),
            Token("operator", "="),
            Token("str", "'bar")
        ])
    
    def test_quoted_name(self):
        code = 'select foo from "my table"'
        self.assertEqual(extract_tokens(code), [
            Token("name", "select"),
            Token("name", "foo"),
            Token("name", "from"),
            Token("name", "my table")
        ])