from unittest import TestCase
from .eval import eval_sql
from .data_schema import TablesSnapshot, Table, Column


class TestEvalSQL(TestCase):
    def test_eval_sql(self):
        code = "select 1+1"
        tables = TablesSnapshot(
            tables=[],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{None: 2}])
