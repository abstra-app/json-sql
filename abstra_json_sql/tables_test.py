from unittest import TestCase
from .tables import InMemoryTables, FileSystemJsonTables, FileSystemJsonLTables, Table
from pathlib import Path
from tempfile import mkdtemp
from shutil import rmtree
from json import dumps

class InMemoryTablesTest(TestCase):
    def test_insert(self):
        tables = InMemoryTables(tables=[
            Table(name="test_table", columns=[], data=[])
        ])
        tables.insert("test_table", {"id": 1, "name": "Test"})
        self.assertEqual(len(tables.get_table("test_table").data), 1)

    def test_update(self):
        tables = InMemoryTables(tables=[{"name": "test_table", "columns": [], "data": [{"id": 1, "name": "Test"}]}])
        tables.update("test_table", 0, {"name": "Updated Test"})
        self.assertEqual(tables.get_table("test_table").data[0]["name"], "Updated Test")

    def test_delete(self):
        tables = InMemoryTables(tables=[{"name": "test_table", "columns": [], "data": [{"id": 1, "name": "Test"}]}])
        tables.delete("test_table", [0])
        self.assertEqual(len(tables.get_table("test_table").data), 0)

class FsTablesTest(TestCase):
    def setUp(self):
        self.path = Path(mkdtemp())
        self.path.mkdir(parents=True, exist_ok=True)
        self.path.joinpath("test_table.json").write_text(dumps([]))
        self.path.joinpath("test_table.jsonl").touch()

    def tearDown(self):
        rmtree(self.path)


class FileSystemJsonTablesTest(FsTablesTest):
    def test_insert(self):
        tables = FileSystemJsonTables(workdir=self.path)
        tables.insert("test_table", {"id": 1, "name": "Test"})
        self.assertEqual(len(tables.get_table("test_table").data), 1)

    def test_update(self):
        tables = FileSystemJsonTables(workdir=self.path)
        tables.insert("test_table", {"id": 1, "name": "Test"})
        tables.update("test_table", 0, {"name": "Updated Test"})
        self.assertEqual(tables.get_table("test_table").data[0]["name"], "Updated Test")

    def test_delete(self):
        tables = FileSystemJsonTables(workdir=self.path)
        tables.insert("test_table", {"id": 1, "name": "Test"})
        tables.delete("test_table", [0])
        self.assertEqual(len(tables.get_table("test_table").data), 0)

class FileSystemJsonLTablesTest(FsTablesTest):
    def test_insert(self):
        # Assuming FileSystemJsonLTables is implemented correctly
        self.path.mkdir(parents=True, exist_ok=True)
        self.path.joinpath("test_table.jsonl").touch()
        tables = FileSystemJsonLTables(workdir=self.path)
        tables.insert("test_table", {"id": 1, "name": "Test"})
        self.assertEqual(len(tables.get_table("test_table").data), 1)

    def test_update(self):
        tables = FileSystemJsonLTables(workdir=self.path)
        tables.insert("test_table", {"id": 1, "name": "Test"})
        tables.update("test_table", 0, {"name": "Updated Test"})
        self.assertEqual(tables.get_table("test_table").data[0]["name"], "Updated Test")

    def test_delete(self):
        tables = FileSystemJsonLTables(workdir=self.path)
        tables.insert("test_table", {"id": 1, "name": "Test"})
        tables.delete("test_table", [0])
        self.assertEqual(len(tables.get_table("test_table").data), 0)