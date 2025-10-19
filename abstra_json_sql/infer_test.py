from unittest import TestCase

from .infer import infer_expression
from .lexer import scan
from .parser import parse_expression
from .tables import ColumnType


class TestInferExpression(TestCase):
    def test_infer_string(self):
        tokens = scan("'hello'")
        expr, _ = parse_expression(tokens)
        result = infer_expression(expr, {})
        self.assertEqual(result, ColumnType.string)

    def test_infer_integer(self):
        tokens = scan("42")
        expr, _ = parse_expression(tokens)
        result = infer_expression(expr, {})
        self.assertEqual(result, ColumnType.int)

    def test_infer_float(self):
        tokens = scan("3.14")
        expr, _ = parse_expression(tokens)
        result = infer_expression(expr, {})
        self.assertEqual(result, ColumnType.float)

    def test_infer_boolean_true(self):
        tokens = scan("true")
        expr, _ = parse_expression(tokens)
        result = infer_expression(expr, {})
        self.assertEqual(result, ColumnType.bool)

    def test_infer_boolean_false(self):
        tokens = scan("false")
        expr, _ = parse_expression(tokens)
        result = infer_expression(expr, {})
        self.assertEqual(result, ColumnType.bool)

    def test_infer_null(self):
        tokens = scan("null")
        expr, _ = parse_expression(tokens)
        result = infer_expression(expr, {})
        self.assertEqual(result, ColumnType.null)

    def test_infer_function_call_count(self):
        tokens = scan("count(*)")
        expr, _ = parse_expression(tokens)
        result = infer_expression(expr, {})
        self.assertEqual(result, ColumnType.int)

    def test_infer_function_call_sum(self):
        tokens = scan("sum(column_name)")
        expr, _ = parse_expression(tokens)
        result = infer_expression(expr, {})
        self.assertEqual(result, ColumnType.float)

    def test_infer_function_call_avg(self):
        tokens = scan("avg(column_name)")
        expr, _ = parse_expression(tokens)
        result = infer_expression(expr, {})
        self.assertEqual(result, ColumnType.float)
