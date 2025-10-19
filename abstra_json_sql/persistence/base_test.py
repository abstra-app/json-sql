from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

from ..tables import Column, ColumnType, Table
from .json import FileSystemJsonTables
from .jsonl import FileSystemJsonLTables


class FsTablesTest(TestCase):
    def setUp(self):
        self.path = Path(mkdtemp())
        self.path.mkdir(parents=True, exist_ok=True)

        # Create test table using the new UUID-based system
        test_table = Table(
            name="test_table",
            columns=[
                Column(name="id", schema=ColumnType.int),
                Column(name="name", schema=ColumnType.string),
            ],
            data=[],
        )

        # For FileSystemJsonTables
        tables_json = FileSystemJsonTables(workdir=self.path)
        tables_json.add_table(test_table)

        # For FileSystemJsonLTables
        test_table_l = Table(
            name="test_table",
            columns=[
                Column(name="id", schema=ColumnType.int),
                Column(name="name", schema=ColumnType.string),
            ],
            data=[],
        )
        tables_jsonl = FileSystemJsonLTables(workdir=self.path)
        tables_jsonl.add_table(test_table_l)

    def tearDown(self):
        rmtree(self.path)
