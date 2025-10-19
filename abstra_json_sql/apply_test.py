from unittest import TestCase

from .apply import (
    apply_expression,
    apply_group_by,
    apply_limit,
    apply_order_by,
    apply_where,
)
from .ast import (
    DivideExpression,
    FloatExpression,
    GreaterThanExpression,
    GroupBy,
    IntExpression,
    Limit,
    MinusExpression,
    MultiplyExpression,
    NameExpression,
    OrderBy,
    OrderField,
    PlusExpression,
    StringExpression,
    Where,
)


class TestApplyExpression(TestCase):
    def test_addition(self):
        expression = PlusExpression(
            left=NameExpression(name="a"),
            right=NameExpression(name="b"),
        )
        ctx = {"a": 1, "b": 2}
        result = apply_expression(expression, ctx)
        self.assertEqual(result, 3)

    def test_subtraction(self):
        expression = MinusExpression(
            left=NameExpression(name="a"),
            right=NameExpression(name="b"),
        )
        ctx = {"a": 5, "b": 2}
        result = apply_expression(expression, ctx)
        self.assertEqual(result, 3)

    def test_multiplication(self):
        expression = MultiplyExpression(
            left=NameExpression(name="a"),
            right=NameExpression(name="b"),
        )
        ctx = {"a": 3, "b": 4}
        result = apply_expression(expression, ctx)
        self.assertEqual(result, 12)

    def test_division(self):
        expression = DivideExpression(
            left=NameExpression(name="a"),
            right=NameExpression(name="b"),
        )
        ctx = {"a": 8, "b": 2}
        result = apply_expression(expression, ctx)
        self.assertEqual(result, 4)

    def test_string(self):
        expression = StringExpression(value="foo")
        ctx = {}
        result = apply_expression(expression, ctx)
        self.assertEqual(result, "foo")

    def test_int(self):
        expression = IntExpression(value=42)
        ctx = {}
        result = apply_expression(expression, ctx)
        self.assertEqual(result, 42)

    def test_float(self):
        expression = FloatExpression(value=3.14)
        ctx = {}
        result = apply_expression(expression, ctx)
        self.assertEqual(result, 3.14)

    def test_boolean(self):
        expression = NameExpression(name="TrUe")
        ctx = {}
        result = apply_expression(expression, ctx)
        self.assertEqual(result, True)

    def test_parentheses(self):
        expression = PlusExpression(
            left=MultiplyExpression(
                left=NameExpression(name="a"),
                right=NameExpression(name="b"),
            ),
            right=NameExpression(name="c"),
        )
        ctx = {"a": 2, "b": 3, "c": 4}
        result = apply_expression(expression, ctx)
        self.assertEqual(result, 10)


class TestApplyWhere(TestCase):
    def test_where_no_context(self):
        where = Where(
            expression=GreaterThanExpression(
                left=NameExpression(name="age"),
                right=IntExpression(value=18),
            )
        )

        data = [
            {"name": "Alice", "age": 20},
            {"name": "Bob", "age": 17},
            {"name": "Charlie", "age": 19},
            {"name": "David", "age": 16},
            {"name": "Eve", "age": 22},
        ]

        result = apply_where(where=where, data=data, ctx={})

        self.assertEqual(
            result,
            [
                {"name": "Alice", "age": 20},
                {"name": "Charlie", "age": 19},
                {"name": "Eve", "age": 22},
            ],
        )

    def test_with_context(self):
        where = Where(
            expression=GreaterThanExpression(
                left=NameExpression(name="age"),
                right=NameExpression(name="minimum_age"),
            )
        )

        data = [
            {"name": "Alice", "age": 20},
            {"name": "Bob", "age": 17},
            {"name": "Charlie", "age": 19},
            {"name": "David", "age": 16},
            {"name": "Eve", "age": 22},
        ]

        result = apply_where(
            where=where,
            data=data,
            ctx={
                "minimum_age": 18,
            },
        )

        self.assertEqual(
            result,
            [
                {"name": "Alice", "age": 20},
                {"name": "Charlie", "age": 19},
                {"name": "Eve", "age": 22},
            ],
        )


class TestApplyOrderBy(TestCase):
    def test_order_by(self):
        order_by = OrderBy(
            fields=[
                OrderField(
                    expression=NameExpression(name="age"),
                    direction="ASC",
                )
            ]
        )

        data = [
            {"name": "Alice", "age": 20},
            {"name": "Bob", "age": 17},
            {"name": "Charlie", "age": 19},
            {"name": "David", "age": 16},
            {"name": "Eve", "age": 22},
        ]

        result = apply_order_by(order_by=order_by, data=data, ctx={})

        self.assertEqual(
            result,
            [
                {"name": "David", "age": 16},
                {"name": "Bob", "age": 17},
                {"name": "Charlie", "age": 19},
                {"name": "Alice", "age": 20},
                {"name": "Eve", "age": 22},
            ],
        )


class TestApplyGroupBy(TestCase):
    def test_group_by(self):
        group_by = GroupBy(
            fields=[
                NameExpression(name="team"),
            ],
        )

        data = [
            {"name": "Alice", "team": "foo"},
            {"name": "Bob", "team": "bar"},
            {"name": "Charlie", "team": "foo"},
            {"name": "David", "team": "bar"},
            {"name": "Eve", "team": "foo"},
        ]

        result = apply_group_by(group_by=group_by, data=data, ctx={})

        self.assertEqual(
            result,
            [
                {
                    "team": "foo",
                    "__grouped_rows": [
                        {"name": "Alice", "team": "foo"},
                        {"name": "Charlie", "team": "foo"},
                        {"name": "Eve", "team": "foo"},
                    ],
                },
                {
                    "team": "bar",
                    "__grouped_rows": [
                        {"name": "Bob", "team": "bar"},
                        {"name": "David", "team": "bar"},
                    ],
                },
            ],
        )


class TestApplyLimit(TestCase):
    def test_limit(self):
        data = [
            {"name": "Alice", "age": 20},
            {"name": "Bob", "age": 17},
            {"name": "Charlie", "age": 19},
            {"name": "David", "age": 16},
            {"name": "Eve", "age": 22},
        ]

        limit = Limit(limit=3)
        result = apply_limit(data=data, limit=limit, ctx={})

        self.assertEqual(
            result,
            [
                {"name": "Alice", "age": 20},
                {"name": "Bob", "age": 17},
                {"name": "Charlie", "age": 19},
            ],
        )
