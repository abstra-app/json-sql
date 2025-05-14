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

    def test_limit(self):
        code = "select foo from bar limit 1"
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
        self.assertEqual(result, [{"foo": "a"}])

    def test_limit_offset(self):
        code = "select foo from bar limit 1 offset 1"
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
        self.assertEqual(result, [{"foo": "b"}])

    def test_order_by(self):
        code = "select foo from bar order by foo"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="text")],
                    data=[
                        {"foo": "c"},
                        {"foo": "b"},
                        {"foo": None},
                        {"foo": "a"},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(
            result, [{"foo": None}, {"foo": "a"}, {"foo": "b"}, {"foo": "c"}]
        )

    def test_order_by_desc(self):
        code = "select foo from bar order by foo desc"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="text")],
                    data=[
                        {"foo": "c"},
                        {"foo": "b"},
                        {"foo": None},
                        {"foo": "a"},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(
            result, [{"foo": "c"}, {"foo": "b"}, {"foo": "a"}, {"foo": None}]
        )

    def test_order_by_asc(self):
        code = "select foo from bar order by foo asc"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="text")],
                    data=[
                        {"foo": "c"},
                        {"foo": "b"},
                        {"foo": None},
                        {"foo": "a"},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(
            result, [{"foo": None}, {"foo": "a"}, {"foo": "b"}, {"foo": "c"}]
        )

    def test_group_by(self):
        code = "select foo, count(*) from bar group by foo"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="text")],
                    data=[
                        {"foo": "a"},
                        {"foo": "b"},
                        {"foo": None},
                        {"foo": "a"},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(
            result,
            [
                {"foo": "a", "count": 2},
                {"foo": "b", "count": 1},
                {"foo": None, "count": 1},
            ],
        )

    def test_select_wildcard(self):
        code = "select * from bar"
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
        self.assertEqual(
            result,
            [
                {"foo": "a"},
                {"foo": "b"},
                {"foo": None},
                {"foo": "c"},
            ],
        )

    def test_join(self):
        code = "select a.foo, b.bar from a join b on a.id = b.a_id"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="a",
                    columns=[
                        Column(name="id", type="int"),
                        Column(name="foo", type="text"),
                    ],
                    data=[
                        {"id": 1, "foo": "a1"},
                        {"id": 2, "foo": "a2"},
                        {"id": 3, "foo": "a3"},
                    ],
                ),
                Table(
                    name="b",
                    columns=[
                        Column(name="a_id", type="int"),
                        Column(name="bar", type="text"),
                    ],
                    data=[
                        {"a_id": 1, "bar": "b1"},
                        {"a_id": 2, "bar": "b2"},
                        {"a_id": 2, "bar": "b3"},
                    ],
                ),
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(
            result,
            [
                {"foo": "a1", "bar": "b1"},
                {"foo": "a2", "bar": "b2"},
                {"foo": "a2", "bar": "b3"},
            ],
        )

    def test_left_outer_join(self):
        code = "select a.foo, b.bar from a left outer join b on a.id = b.a_id"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="a",
                    columns=[
                        Column(name="id", type="int"),
                        Column(name="foo", type="text"),
                    ],
                    data=[
                        {"id": 1, "foo": "a1"},
                        {"id": 2, "foo": "a2"},
                        {"id": 3, "foo": "a3"},
                    ],
                ),
                Table(
                    name="b",
                    columns=[
                        Column(name="a_id", type="int"),
                        Column(name="bar", type="text"),
                    ],
                    data=[
                        {"a_id": 1, "bar": "b1"},
                        {"a_id": 2, "bar": "b2"},
                        {"a_id": 2, "bar": "b3"},
                    ],
                ),
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(
            result,
            [
                {"foo": "a1", "bar": "b1"},
                {"foo": "a2", "bar": "b2"},
                {"foo": "a2", "bar": "b3"},
                {"foo": "a3", "bar": None},
            ],
        )

    def test_complete(self):
        code = "\n".join(
            [
                "select foo, count(*)",
                "from bar as baz",
                "where foo is not null",
                "group by foo",
                "having foo <> 2",
                "order by foo",
                "limit 1 offset 1",
            ]
        )
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", type="text")],
                    data=[
                        {"foo": 1},
                        {"foo": 2},
                        {"foo": 3},
                        {"foo": 2},
                        {"foo": None},
                        {"foo": 3},
                        {"foo": 1},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"foo": 3, "count": 2}])
