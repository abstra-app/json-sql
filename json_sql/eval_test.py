from unittest import TestCase
from .eval import eval_expression

class TestEvalExpression(TestCase):
    def test_addition(self):
        from .ast import PlusExpression, NameExpression

        expression = PlusExpression(
            left=NameExpression(name="a"),
            right=NameExpression(name="b"),
        )
        ctx = {"a": 1, "b": 2}
        result = eval_expression(expression, ctx)
        self.assertEqual(result, 3)

    def test_subtraction(self):
        from .ast import MinusExpression, NameExpression

        expression = MinusExpression(
            left=NameExpression(name="a"),
            right=NameExpression(name="b"),
        )
        ctx = {"a": 5, "b": 2}
        result = eval_expression(expression, ctx)
        self.assertEqual(result, 3)

    def test_multiplication(self):
        from .ast import MultiplyExpression, NameExpression

        expression = MultiplyExpression(
            left=NameExpression(name="a"),
            right=NameExpression(name="b"),
        )
        ctx = {"a": 3, "b": 4}
        result = eval_expression(expression, ctx)
        self.assertEqual(result, 12)

    def test_division(self):
        from .ast import DivideExpression, NameExpression

        expression = DivideExpression(
            left=NameExpression(name="a"),
            right=NameExpression(name="b"),
        )
        ctx = {"a": 8, "b": 2}
        result = eval_expression(expression, ctx)
        self.assertEqual(result, 4)
    
    def test_string(self):
        from .ast import StringExpression

        expression = StringExpression(value="foo")
        ctx = {}
        result = eval_expression(expression, ctx)
        self.assertEqual(result, "foo")
    
    def test_int(self):
        from .ast import IntExpression

        expression = IntExpression(value=42)
        ctx = {}
        result = eval_expression(expression, ctx)
        self.assertEqual(result, 42)
    
    def test_float(self):
        from .ast import FloatExpression

        expression = FloatExpression(value=3.14)
        ctx = {}
        result = eval_expression(expression, ctx)
        self.assertEqual(result, 3.14)
    
    def test_boolean(self):
        from .ast import NameExpression

        expression = NameExpression(name="TrUe")
        ctx = {}
        result = eval_expression(expression, ctx)
        self.assertEqual(result, True)