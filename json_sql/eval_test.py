from unittest import TestCase
from .eval import eval_sql
from .tables import InMemoryTables


class TestEvalSQL(TestCase):
    def test_eval_sql(self):
        code = "select 1+1"
        tables = InMemoryTables(
            tables=[],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{None: 2}])

    def test_eval_select_alias(self):
        code = "select 1+1 as a"
        tables = InMemoryTables(
            tables=[],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"a": 2}])
