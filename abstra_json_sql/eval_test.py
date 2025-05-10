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

    def test_count_wildcard(self):
        code = "select count(*) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="text")],
                    data=[
                        {"foo": "aaa"},
                        {"foo": "bbb"},
                        {"foo": None},
                        {"foo": "ccc"},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"count": 4}])

    def test_count_name(self):
        code = "select count(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="text")],
                    data=[
                        {"foo": "aaa"},
                        {"foo": "bbb"},
                        {"foo": None},
                        {"foo": "ccc"},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"count": 3}])

    def test_avg(self):
        code = "select avg(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="int")],
                    data=[
                        {"foo": 1},
                        {"foo": 2},
                        {"foo": None},
                        {"foo": 3},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"avg": 2}])

    def test_sum(self):
        code = "select sum(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="int")],
                    data=[
                        {"foo": 1},
                        {"foo": 2},
                        {"foo": None},
                        {"foo": 3},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"sum": 6}])

    def test_min(self):
        code = "select min(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="int")],
                    data=[
                        {"foo": 1},
                        {"foo": 2},
                        {"foo": None},
                        {"foo": 3},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"min": 1}])

    def test_max(self):
        code = "select max(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="int")],
                    data=[
                        {"foo": 1},
                        {"foo": 2},
                        {"foo": None},
                        {"foo": 3},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"max": 3}])

    def test_every(self):
        code = "select every(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="bool")],
                    data=[
                        {"foo": True},
                        {"foo": False},
                        {"foo": None},
                        {"foo": True},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"every": False}])

    def test_bool_and(self):
        code = "select bool_and(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="bool")],
                    data=[
                        {"foo": True},
                        {"foo": False},
                        {"foo": None},
                        {"foo": True},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"bool_and": False}])

    def test_bool_or(self):
        code = "select bool_or(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="bool")],
                    data=[
                        {"foo": True},
                        {"foo": False},
                        {"foo": None},
                        {"foo": True},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"bool_or": True}])

    def test_bit_and(self):
        code = "select bit_and(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="int")],
                    data=[
                        {"foo": 0b0110},
                        {"foo": 0b1010},
                        {"foo": None},
                        {"foo": 0b1110},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"bit_and": 0b0010}])

    def test_bit_or(self):
        code = "select bit_or(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="int")],
                    data=[
                        {"foo": 0b0110},
                        {"foo": 0b1010},
                        {"foo": None},
                        {"foo": 0b1110},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"bit_or": 0b1110}])

    def test_array_agg(self):
        code = "select array_agg(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="int")],
                    data=[
                        {"foo": 1},
                        {"foo": 2},
                        {"foo": None},
                        {"foo": 3},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"array_agg": [1, 2, None, 3]}])

    def test_string_agg(self):
        code = "select string_agg(foo, ',') from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="text")],
                    data=[
                        {"foo": "a"},
                        {"foo": "b"},
                        {"foo": None},
                        {"foo": "c"},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"string_agg": "a,b,c"}])
