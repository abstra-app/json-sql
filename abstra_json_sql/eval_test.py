from unittest import TestCase
from .eval import eval_sql
from .tables import InMemoryTables, Table, Column


class TestEvalSQL(TestCase):
    def test_sql(self):
        code = "select 1+1"
        tables = InMemoryTables(
            tables=[],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"?column?": 2}])

    def test_select_alias(self):
        code = "select 1+1 as a"
        tables = InMemoryTables(
            tables=[],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"a": 2}])

    def test_lower(self):
        code = "select lower(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="text")],
                    data=[
                        {"foo": "AAA"},
                        {"foo": "BBB"},
                        {"foo": "CCC"},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(
            result,
            [
                {"lower": "aaa"},
                {"lower": "bbb"},
                {"lower": "ccc"},
            ],
        )

    def test_upper(self):
        code = "select upper(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="text")],
                    data=[
                        {"foo": "aaa"},
                        {"foo": "bbb"},
                        {"foo": "ccc"},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(
            result,
            [
                {"upper": "AAA"},
                {"upper": "BBB"},
                {"upper": "CCC"},
            ],
        )

    def test_count(self):
        code = "select count(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="text")],
                    data=[
                        {"foo": "aaa"},
                        {"foo": "bbb"},
                        {"foo": "ccc"},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"count": 3}])
