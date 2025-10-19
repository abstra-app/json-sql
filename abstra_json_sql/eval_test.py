from unittest import TestCase

from .eval import eval_sql
from .persistence import InMemoryTables
from .tables import Column, ColumnType, Table


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

    def test_select_complete(self):
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
                    columns=[Column(name="foo", schema=ColumnType.string)],
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

    def test_lower(self):
        code = "select lower(foo) from bar"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", schema=ColumnType.string)],
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
                    columns=[Column(name="foo", schema=ColumnType.string)],
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
                    columns=[Column(name="foo", schema=ColumnType.string)],
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
                    columns=[Column(name="foo", schema=ColumnType.string)],
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
                    columns=[Column(name="foo", schema="int")],
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
                    columns=[Column(name="foo", schema="int")],
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
                    columns=[Column(name="foo", schema="int")],
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
                    columns=[Column(name="foo", schema="int")],
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
                    columns=[Column(name="foo", schema="bool")],
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
                    columns=[Column(name="foo", schema="bool")],
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
                    columns=[Column(name="foo", schema="bool")],
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
                    columns=[Column(name="foo", schema="int")],
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
                    columns=[Column(name="foo", schema="int")],
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
                    columns=[Column(name="foo", schema="int")],
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
                    columns=[Column(name="foo", schema=ColumnType.string)],
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
                    columns=[Column(name="foo", schema=ColumnType.string)],
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
                    columns=[Column(name="foo", schema=ColumnType.string)],
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
                    columns=[Column(name="foo", schema=ColumnType.string)],
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
                    columns=[Column(name="foo", schema=ColumnType.string)],
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
                    columns=[Column(name="foo", schema=ColumnType.string)],
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
                    columns=[Column(name="foo", schema=ColumnType.string)],
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
                    columns=[Column(name="foo", schema=ColumnType.string)],
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
                        Column(name="id", schema="int"),
                        Column(name="foo", schema=ColumnType.string),
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
                        Column(name="a_id", schema="int"),
                        Column(name="bar", schema=ColumnType.string),
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
                        Column(name="id", schema="int"),
                        Column(name="foo", schema=ColumnType.string),
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
                        Column(name="a_id", schema="int"),
                        Column(name="bar", schema=ColumnType.string),
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

    def test_right_join(self):
        code = "select a.foo, b.bar from a right outer join b on a.id = b.a_id"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="a",
                    columns=[
                        Column(name="id", schema="int"),
                        Column(name="foo", schema=ColumnType.string),
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
                        Column(name="a_id", schema="int"),
                        Column(name="bar", schema=ColumnType.string),
                    ],
                    data=[
                        {"a_id": 1, "bar": "b1"},
                        {"a_id": 2, "bar": "b2"},
                        {"a_id": 2, "bar": "b3"},
                        {"a_id": 4, "bar": "b4"},
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
                {"foo": None, "bar": "b4"},
            ],
        )

    def test_full_join(self):
        code = "select a.foo, b.bar from a full outer join b on a.id = b.a_id"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="a",
                    columns=[
                        Column(name="id", schema="int"),
                        Column(name="foo", schema=ColumnType.string),
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
                        Column(name="a_id", schema="int"),
                        Column(name="bar", schema=ColumnType.string),
                    ],
                    data=[
                        {"a_id": 1, "bar": "b1"},
                        {"a_id": 2, "bar": "b2"},
                        {"a_id": 2, "bar": "b3"},
                        {"a_id": 4, "bar": "b4"},
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
                {"foo": None, "bar": "b4"},
            ],
        )

    def test_with(self):
        code = "with t as (select foo from bar) select * from t"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", schema=ColumnType.string)],
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

    def test_multiple_with(self):
        code = "with t1 as (select foo from bar), t2 as (select * from t1) select * from t2"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", schema=ColumnType.string)],
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

    def test_insert(self):
        code = "insert into bar (foo) values ('a'), ('b'), ('c')"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", schema=ColumnType.string)],
                    data=[],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertIsNone(result)
        self.assertEqual(
            tables.get_table("bar").data,
            [
                {"foo": "a"},
                {"foo": "b"},
                {"foo": "c"},
            ],
        )

    def test_insert_returning(self):
        code = "insert into bar (foo) values ('a'), ('b'), ('c') returning foo"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", schema=ColumnType.string)],
                    data=[],
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
                {"foo": "c"},
            ],
        )
        self.assertEqual(
            tables.get_table("bar").data,
            [
                {"foo": "a"},
                {"foo": "b"},
                {"foo": "c"},
            ],
        )

    def test_insert_returning_wildcard(self):
        code = "insert into bar (foo) values ('a'), ('b'), ('c') returning *"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[Column(name="foo", schema=ColumnType.string)],
                    data=[],
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
                {"foo": "c"},
            ],
        )
        self.assertEqual(
            tables.get_table("bar").data,
            [
                {"foo": "a"},
                {"foo": "b"},
                {"foo": "c"},
            ],
        )

    def test_insert_default_values(self):
        code = "insert into bar (foo) default values"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[
                        Column(name="foo", schema=ColumnType.string, default="'lala'")
                    ],
                    data=[],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertIsNone(result)
        self.assertEqual(
            tables.get_table("bar").data,
            [
                {"foo": "lala"},
            ],
        )

    def test_insert_default_value_in_single_column(self):
        code = "insert into bar (foo) values (default)"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="bar",
                    columns=[
                        Column(name="foo", schema=ColumnType.string, default="'lala'")
                    ],
                    data=[],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertIsNone(result)
        self.assertEqual(
            tables.get_table("bar").data,
            [
                {"foo": "lala"},
            ],
        )

    def test_insert_omit_default_value(self):
        code = "insert into t (c1) values ('xpto')"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="t",
                    columns=[
                        Column(name="c1", schema=ColumnType.string),
                        Column(name="c2", schema=ColumnType.string, default="'lala'"),
                    ],
                    data=[],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertIsNone(result)
        self.assertEqual(
            tables.get_table("t").data,
            [
                {"c1": "xpto", "c2": "lala"},
            ],
        )

    def test_update(self):
        code = "update foo set b = 0 where a = 1"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="foo",
                    columns=[
                        Column(name="a", schema="int"),
                        Column(name="b", schema="int"),
                    ],
                    data=[{"a": 1, "b": 2}, {"a": 3, "b": 4}],
                )
            ]
        )

        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertIsNone(result)
        self.assertEqual(
            tables.get_table("foo").data, [{"a": 1, "b": 0}, {"a": 3, "b": 4}]
        )

    def test_update_expression_set(self):
        code = "update foo set a = b + 1"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="foo",
                    columns=[
                        Column(name="a", schema="int"),
                        Column(name="b", schema="int"),
                    ],
                    data=[{"a": 1, "b": 2}, {"a": 3, "b": 4}],
                )
            ]
        )

        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertIsNone(result)
        self.assertEqual(
            tables.get_table("foo").data, [{"a": 3, "b": 2}, {"a": 5, "b": 4}]
        )

    def test_update_expression_where(self):
        code = "update foo set a = 0 where a > b"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="foo",
                    columns=[
                        Column(name="a", schema="int"),
                        Column(name="b", schema="int"),
                    ],
                    data=[{"a": 10, "b": 2}, {"a": 3, "b": 4}],
                )
            ]
        )

        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertIsNone(result)
        self.assertEqual(
            tables.get_table("foo").data, [{"a": 0, "b": 2}, {"a": 3, "b": 4}]
        )

    def test_delete(self):
        code = "delete from foo where a = 1"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="foo",
                    columns=[
                        Column(name="a", schema="int"),
                        Column(name="b", schema="int"),
                    ],
                    data=[{"a": 1, "b": 2}, {"a": 3, "b": 4}],
                )
            ]
        )

        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertIsNone(result)
        self.assertEqual(tables.get_table("foo").data, [{"a": 3, "b": 4}])

    def test_delete_expression(self):
        code = "delete from foo where a > b"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="foo",
                    columns=[
                        Column(name="a", schema="int"),
                        Column(name="b", schema="int"),
                    ],
                    data=[{"a": 10, "b": 2}, {"a": 3, "b": 4}],
                )
            ]
        )

        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertIsNone(result)
        self.assertEqual(tables.get_table("foo").data, [{"a": 3, "b": 4}])

    def test_delete_all(self):
        code = "delete from foo"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="foo",
                    columns=[
                        Column(name="a", schema="int"),
                        Column(name="b", schema="int"),
                    ],
                    data=[{"a": 1, "b": 2}, {"a": 3, "b": 4}],
                )
            ]
        )

        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertIsNone(result)
        self.assertEqual(tables.get_table("foo").data, [])

    def test_reserved_keyword_as_column_name_select(self):
        """Test that SQL reserved keywords can be used as column names with quotes"""
        code = 'select "select", "update", "where" from data'
        tables = InMemoryTables(
            tables=[
                Table(
                    name="data",
                    columns=[
                        Column(name="select", schema=ColumnType.string),
                        Column(name="update", schema=ColumnType.string),
                        Column(name="where", schema=ColumnType.string),
                    ],
                    data=[
                        {"select": "val1", "update": "val2", "where": "val3"},
                        {"select": "val4", "update": "val5", "where": "val6"},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(
            result,
            [
                {"select": "val1", "update": "val2", "where": "val3"},
                {"select": "val4", "update": "val5", "where": "val6"},
            ],
        )

    def test_reserved_keyword_as_column_name_insert(self):
        """Test INSERT with reserved keywords as column names"""
        code = "insert into data (\"select\", \"update\", \"where\") values ('a', 'b', 'c')"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="data",
                    columns=[
                        Column(name="select", schema=ColumnType.string),
                        Column(name="update", schema=ColumnType.string),
                        Column(name="where", schema=ColumnType.string),
                    ],
                    data=[],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertIsNone(result)
        self.assertEqual(
            tables.get_table("data").data,
            [{"select": "a", "update": "b", "where": "c"}],
        )

    def test_reserved_keyword_as_column_name_update(self):
        """Test UPDATE with reserved keywords as column names"""
        code = "update data set \"update\" = 'new_value' where \"select\" = 'a'"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="data",
                    columns=[
                        Column(name="select", schema=ColumnType.string),
                        Column(name="update", schema=ColumnType.string),
                    ],
                    data=[
                        {"select": "a", "update": "old"},
                        {"select": "b", "update": "keep"},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertIsNone(result)
        self.assertEqual(
            tables.get_table("data").data,
            [
                {"select": "a", "update": "new_value"},
                {"select": "b", "update": "keep"},
            ],
        )

    def test_reserved_keyword_as_column_name_where(self):
        """Test WHERE clause with reserved keywords as column names"""
        code = "select * from data where \"select\" = 'test'"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="data",
                    columns=[
                        Column(name="select", schema=ColumnType.string),
                        Column(name="id", schema="int"),
                    ],
                    data=[
                        {"id": 1, "select": "test"},
                        {"id": 2, "select": "other"},
                        {"id": 3, "select": "test"},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(
            result,
            [
                {"id": 1, "select": "test"},
                {"id": 3, "select": "test"},
            ],
        )

    def test_reserved_keyword_without_quotes_should_fail(self):
        """Test that reserved keywords without quotes should fail during parsing"""
        code = "insert into data (select, update, where) values ('a', 'b', 'c')"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="data",
                    columns=[
                        Column(name="select", schema=ColumnType.string),
                        Column(name="update", schema=ColumnType.string),
                        Column(name="where", schema=ColumnType.string),
                    ],
                    data=[],
                )
            ],
        )
        ctx = {}
        # Should raise an assertion error because parser expects column name but gets keyword
        with self.assertRaises(AssertionError):
            eval_sql(code=code, tables=tables, ctx=ctx)

    def test_where_clause_with_column_reference(self):
        """Test WHERE clause can properly resolve column names from table data"""
        code = "select * from users where id = 'user_123'"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="users",
                    columns=[
                        Column(name="id", schema=ColumnType.string),
                        Column(name="name", schema=ColumnType.string),
                    ],
                    data=[
                        {"id": "user_123", "name": "Alice"},
                        {"id": "user_456", "name": "Bob"},
                        {"id": "user_789", "name": "Charlie"},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(result, [{"id": "user_123", "name": "Alice"}])

    def test_where_clause_with_multiple_conditions(self):
        """Test WHERE clause with multiple column references using AND"""
        code = "select * from products where price > 10 and stock > 0"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="products",
                    columns=[
                        Column(name="id", schema="int"),
                        Column(name="price", schema="int"),
                        Column(name="stock", schema="int"),
                    ],
                    data=[
                        {"id": 1, "price": 5, "stock": 10},
                        {"id": 2, "price": 15, "stock": 5},
                        {"id": 3, "price": 20, "stock": 0},
                        {"id": 4, "price": 12, "stock": 3},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(
            result,
            [
                {"id": 2, "price": 15, "stock": 5},
                {"id": 4, "price": 12, "stock": 3},
            ],
        )

    def test_where_clause_column_comparison(self):
        """Test WHERE clause comparing two columns"""
        code = "select * from inventory where quantity < min_quantity"
        tables = InMemoryTables(
            tables=[
                Table(
                    name="inventory",
                    columns=[
                        Column(name="item", schema=ColumnType.string),
                        Column(name="quantity", schema="int"),
                        Column(name="min_quantity", schema="int"),
                    ],
                    data=[
                        {"item": "A", "quantity": 5, "min_quantity": 10},
                        {"item": "B", "quantity": 20, "min_quantity": 15},
                        {"item": "C", "quantity": 3, "min_quantity": 5},
                    ],
                )
            ],
        )
        ctx = {}
        result = eval_sql(code=code, tables=tables, ctx=ctx)
        self.assertEqual(
            result,
            [
                {"item": "A", "quantity": 5, "min_quantity": 10},
                {"item": "C", "quantity": 3, "min_quantity": 5},
            ],
        )
