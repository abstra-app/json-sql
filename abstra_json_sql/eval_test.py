from unittest import TestCase
from .eval import eval_sql
from .tables import InMemoryTables, Table


class TestEvalSQL(TestCase):
    def test_eval_sql(self):
        code = "select 1+1"
        tables = InMemoryTables(
            tables=[],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"?column?": 2}])

    def test_eval_select_alias(self):
        code = "select 1+1 as a"
        tables = InMemoryTables(
            tables=[],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"a": 2}])

    def test_eval_aggregate(self):
        code = "select sum(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=["foo"],
                    rows=[
                        {"foo": 1},
                        {"foo": 2},
                        {"foo": 3},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"a": 6}])
