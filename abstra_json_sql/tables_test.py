import pytest
import tempfile
import json
from pathlib import Path
from .tables import (
    Column,
    ColumnType,
    Table,
    ForeignKey,
    InMemoryTables,
    FileSystemJsonTables,
    FileSystemJsonLTables,
    ExtendedTables,
)
from unittest import TestCase
from tempfile import mkdtemp
from shutil import rmtree


class InMemoryTablesTest(TestCase):
    def test_insert(self):
        tables = InMemoryTables(tables=[Table(name="test_table", columns=[], data=[])])
        tables.insert("test_table", {"id": 1, "name": "Test"})
        self.assertEqual(len(tables.get_table("test_table").data), 1)

    def test_update(self):
        tables = InMemoryTables(
            tables=[
                {
                    "name": "test_table",
                    "columns": [],
                    "data": [{"id": 1, "name": "Test"}],
                }
            ]
        )
        tables.update("test_table", 0, {"name": "Updated Test"})
        self.assertEqual(tables.get_table("test_table").data[0]["name"], "Updated Test")

    def test_delete(self):
        tables = InMemoryTables(
            tables=[
                {
                    "name": "test_table",
                    "columns": [],
                    "data": [{"id": 1, "name": "Test"}],
                }
            ]
        )
        tables.delete("test_table", [0])
        self.assertEqual(len(tables.get_table("test_table").data), 0)


class FsTablesTest(TestCase):
    def setUp(self):
        self.path = Path(mkdtemp())
        self.path.mkdir(parents=True, exist_ok=True)

        # Create test table using the new UUID-based system
        test_table = Table(
            name="test_table",
            columns=[
                Column(name="id", type=ColumnType.int),
                Column(name="name", type=ColumnType.string),
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
                Column(name="id", type=ColumnType.int),
                Column(name="name", type=ColumnType.string),
            ],
            data=[],
        )
        tables_jsonl = FileSystemJsonLTables(workdir=self.path)
        tables_jsonl.add_table(test_table_l)

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


class TestColumnType:
    def test_from_value_int(self):
        assert ColumnType.from_value(42) == ColumnType.int

    def test_from_value_string(self):
        assert ColumnType.from_value("hello") == ColumnType.string

    def test_from_value_float(self):
        assert ColumnType.from_value(3.14) == ColumnType.float

    def test_from_value_bool(self):
        assert ColumnType.from_value(True) == ColumnType.bool

    def test_from_value_none(self):
        assert ColumnType.from_value(None) == ColumnType.null

    def test_from_value_unknown(self):
        assert ColumnType.from_value([1, 2, 3]) == ColumnType.unknown


class TestColumn:
    def test_column_creation(self):
        col = Column(name="id", type=ColumnType.int, is_primary_key=True)
        assert col.name == "id"
        assert col.type == ColumnType.int
        assert col.is_primary_key is True
        assert col.foreign_key is None
        assert col.default is None

    def test_column_with_foreign_key(self):
        fk = ForeignKey(table="users", column="id")
        col = Column(name="user_id", type=ColumnType.int, foreign_key=fk)
        assert col.foreign_key.table == "users"
        assert col.foreign_key.column == "id"

    def test_column_hash(self):
        col1 = Column(name="id", type=ColumnType.int)
        col2 = Column(name="id", type=ColumnType.int)
        assert hash(col1) == hash(col2)


class TestTable:
    def test_table_creation(self):
        columns = [
            Column(name="id", type=ColumnType.int, is_primary_key=True),
            Column(name="name", type=ColumnType.string),
        ]
        table = Table(name="users", columns=columns)
        assert table.name == "users"
        assert len(table.columns) == 2
        assert table.data == []

    def test_get_column(self):
        columns = [
            Column(name="id", type=ColumnType.int),
            Column(name="name", type=ColumnType.string),
        ]
        table = Table(name="users", columns=columns)

        col = table.get_column("id")
        assert col is not None
        assert col.name == "id"

        col = table.get_column("nonexistent")
        assert col is None


class TestInMemoryTables:
    @pytest.fixture
    def sample_table(self):
        return Table(
            name="users",
            columns=[
                Column(name="id", type=ColumnType.int, is_primary_key=True),
                Column(name="name", type=ColumnType.string),
                Column(name="age", type=ColumnType.int),
            ],
            data=[
                {"id": 1, "name": "Alice", "age": 30},
                {"id": 2, "name": "Bob", "age": 25},
            ],
        )

    @pytest.fixture
    def tables(self):
        return InMemoryTables(tables=[])

    def test_add_table(self, tables, sample_table):
        tables.add_table(sample_table)
        assert len(tables.tables) == 1
        assert tables.tables[0].name == "users"

    def test_add_duplicate_table(self, tables, sample_table):
        tables.add_table(sample_table)
        with pytest.raises(ValueError, match="Table users already exists"):
            tables.add_table(sample_table)

    def test_get_table(self, tables, sample_table):
        tables.add_table(sample_table)
        retrieved = tables.get_table("users")
        assert retrieved is not None
        assert retrieved.name == "users"
        assert len(retrieved.data) == 2

    def test_get_nonexistent_table(self, tables):
        assert tables.get_table("nonexistent") is None

    def test_remove_table(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.remove_table("users")
        assert len(tables.tables) == 0

    def test_rename_table(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.rename_table("users", "people")
        assert tables.get_table("users") is None
        assert tables.get_table("people") is not None

    def test_rename_nonexistent_table(self, tables):
        with pytest.raises(ValueError, match="Table nonexistent not found"):
            tables.rename_table("nonexistent", "new_name")

    def test_rename_to_existing_table(self, tables, sample_table):
        tables.add_table(sample_table)
        other_table = Table(name="other", columns=[], data=[])
        tables.add_table(other_table)
        with pytest.raises(ValueError, match="Table other already exists"):
            tables.rename_table("users", "other")

    def test_add_column(self, tables, sample_table):
        tables.add_table(sample_table)
        new_column = Column(name="email", type=ColumnType.string)
        tables.add_column("users", new_column)

        table = tables.get_table("users")
        assert len(table.columns) == 4
        assert table.get_column("email") is not None

    def test_add_duplicate_column(self, tables, sample_table):
        tables.add_table(sample_table)
        duplicate_column = Column(name="name", type=ColumnType.string)
        with pytest.raises(ValueError, match="Column name already exists"):
            tables.add_column("users", duplicate_column)

    def test_remove_column(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.remove_column("users", "age")

        table = tables.get_table("users")
        assert len(table.columns) == 2
        assert table.get_column("age") is None

    def test_change_column_type(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.change_column_type("users", "age", ColumnType.string)

        table = tables.get_table("users")
        age_col = table.get_column("age")
        assert age_col.type == ColumnType.string

    def test_insert(self, tables, sample_table):
        tables.add_table(sample_table)
        new_row = {"id": 3, "name": "Charlie", "age": 35}
        tables.insert("users", new_row)

        table = tables.get_table("users")
        assert len(table.data) == 3
        assert table.data[2] == new_row

    def test_update(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.update("users", 0, {"name": "Alice Updated"})

        table = tables.get_table("users")
        assert table.data[0]["name"] == "Alice Updated"

    def test_delete(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.delete("users", [0])

        table = tables.get_table("users")
        assert len(table.data) == 1
        assert table.data[0]["name"] == "Bob"


class TestFileSystemJsonTables:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def tables(self, temp_dir):
        return FileSystemJsonTables(temp_dir)

    @pytest.fixture
    def sample_table(self):
        return Table(
            name="users",
            columns=[
                Column(name="id", type=ColumnType.int, is_primary_key=True),
                Column(name="name", type=ColumnType.string),
                Column(name="age", type=ColumnType.int),
            ],
            data=[
                {"id": 1, "name": "Alice", "age": 30},
                {"id": 2, "name": "Bob", "age": 25},
            ],
        )

    def test_metadata_table_creation(self, tables, temp_dir):
        assert (temp_dir / "__schema__.json").exists()
        metadata = json.loads((temp_dir / "__schema__.json").read_text())
        assert metadata == {}

    def test_add_table(self, tables, sample_table, temp_dir):
        tables.add_table(sample_table)

        # Check data file exists with UUID name
        table_id = sample_table.table_id
        assert (temp_dir / f"{table_id}.json").exists()

        # Check metadata is saved
        metadata = json.loads((temp_dir / "__schema__.json").read_text())
        assert table_id in metadata
        assert metadata[table_id]["table_name"] == "users"
        assert len(metadata[table_id]["columns"]) == 3

    def test_add_duplicate_table(self, tables, sample_table, temp_dir):
        tables.add_table(sample_table)
        with pytest.raises(ValueError, match="Table users already exists"):
            tables.add_table(sample_table)

    def test_get_table(self, tables, sample_table):
        tables.add_table(sample_table)
        retrieved = tables.get_table("users")
        assert retrieved.name == "users"
        assert len(retrieved.data) == 2
        assert len(retrieved.columns) == 3

    def test_get_nonexistent_table(self, tables):
        with pytest.raises(FileNotFoundError):
            tables.get_table("nonexistent")

    def test_remove_table(self, tables, sample_table, temp_dir):
        tables.add_table(sample_table)
        table_id = sample_table.table_id

        # Verify file exists before removal
        assert (temp_dir / f"{table_id}.json").exists()

        tables.remove_table("users")

        # File should be removed
        assert not (temp_dir / f"{table_id}.json").exists()

        # Metadata should be removed
        metadata = json.loads((temp_dir / "__schema__.json").read_text())
        assert table_id not in metadata

    def test_rename_table(self, tables, sample_table, temp_dir):
        tables.add_table(sample_table)
        table_id = sample_table.table_id

        tables.rename_table("users", "people")

        # File name should stay the same (UUID-based)
        assert (temp_dir / f"{table_id}.json").exists()

        # Metadata should reflect the new table name
        metadata = json.loads((temp_dir / "__schema__.json").read_text())
        assert table_id in metadata
        assert metadata[table_id]["table_name"] == "people"

    def test_add_column(self, tables, sample_table):
        tables.add_table(sample_table)
        new_column = Column(
            name="email", type=ColumnType.string, default="test@example.com"
        )
        tables.add_column("users", new_column)

        table = tables.get_table("users")
        assert len(table.columns) == 4
        assert table.get_column("email") is not None
        # Check that default value was added to existing rows
        assert all(row["email"] == "test@example.com" for row in table.data)

    def test_remove_column(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.remove_column("users", "age")

        table = tables.get_table("users")
        assert len(table.columns) == 2
        assert table.get_column("age") is None
        # Check that column was removed from data
        assert all("age" not in row for row in table.data)

    def test_rename_column(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.rename_column("users", "age", "years")

        table = tables.get_table("users")
        assert table.get_column("age") is None
        assert table.get_column("years") is not None
        # Check that column was renamed in data
        assert all("age" not in row and "years" in row for row in table.data)

    def test_change_column_type(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.change_column_type("users", "age", ColumnType.string)

        table = tables.get_table("users")
        age_col = table.get_column("age")
        assert age_col.type == ColumnType.string

    def test_insert(self, tables, sample_table):
        tables.add_table(sample_table)
        new_row = {"id": 3, "name": "Charlie", "age": 35}
        tables.insert("users", new_row)

        table = tables.get_table("users")
        assert len(table.data) == 3
        assert table.data[2] == new_row

    def test_update(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.update("users", 0, {"name": "Alice Updated"})

        table = tables.get_table("users")
        assert table.data[0]["name"] == "Alice Updated"

    def test_delete(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.delete("users", [0])

        table = tables.get_table("users")
        assert len(table.data) == 1
        assert table.data[0]["name"] == "Bob"


class TestFileSystemJsonLTables:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def tables(self, temp_dir):
        return FileSystemJsonLTables(temp_dir)

    @pytest.fixture
    def sample_table(self):
        return Table(
            name="users",
            columns=[
                Column(name="id", type=ColumnType.int, is_primary_key=True),
                Column(name="name", type=ColumnType.string),
                Column(name="age", type=ColumnType.int),
            ],
            data=[
                {"id": 1, "name": "Alice", "age": 30},
                {"id": 2, "name": "Bob", "age": 25},
            ],
        )

    def test_metadata_table_creation(self, tables, temp_dir):
        assert (temp_dir / "__schema__.jsonl").exists()

    def test_add_table(self, tables, sample_table, temp_dir):
        tables.add_table(sample_table)

        # Check data file exists with UUID name
        table_id = sample_table.table_id
        assert (temp_dir / f"{table_id}.jsonl").exists()

        # Check metadata is saved
        with (temp_dir / "__schema__.jsonl").open("r") as f:
            metadata_line = f.readline().strip()
            metadata = json.loads(metadata_line)
            assert metadata["table_id"] == table_id
            assert metadata["table_name"] == "users"
            assert len(metadata["columns"]) == 3

    def test_get_table(self, tables, sample_table):
        tables.add_table(sample_table)
        retrieved = tables.get_table("users")
        assert retrieved.name == "users"
        assert len(retrieved.data) == 2
        assert len(retrieved.columns) == 3

    def test_get_nonexistent_table(self, tables):
        with pytest.raises(FileNotFoundError):
            tables.get_table("nonexistent")

    def test_remove_table(self, tables, sample_table, temp_dir):
        tables.add_table(sample_table)
        table_id = sample_table.table_id

        # Verify file exists before removal
        assert (temp_dir / f"{table_id}.jsonl").exists()

        tables.remove_table("users")

        # File should be removed
        assert not (temp_dir / f"{table_id}.jsonl").exists()

        # Check metadata is removed
        with (temp_dir / "__schema__.jsonl").open("r") as f:
            content = f.read().strip()
            assert not content  # Should be empty

    def test_rename_table(self, tables, sample_table, temp_dir):
        tables.add_table(sample_table)
        table_id = sample_table.table_id

        tables.rename_table("users", "people")

        # File name should stay the same (UUID-based)
        assert (temp_dir / f"{table_id}.jsonl").exists()

        # Check metadata is updated
        with (temp_dir / "__schema__.jsonl").open("r") as f:
            metadata_line = f.readline().strip()
            metadata = json.loads(metadata_line)
            assert metadata["table_name"] == "people"

    def test_add_column(self, tables, sample_table):
        tables.add_table(sample_table)
        new_column = Column(
            name="email", type=ColumnType.string, default="test@example.com"
        )
        tables.add_column("users", new_column)

        table = tables.get_table("users")
        assert len(table.columns) == 4
        assert table.get_column("email") is not None
        # Check that default value was added to existing rows
        assert all(row["email"] == "test@example.com" for row in table.data)

    def test_remove_column(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.remove_column("users", "age")

        table = tables.get_table("users")
        assert len(table.columns) == 2
        assert table.get_column("age") is None
        # Check that column was removed from data
        assert all("age" not in row for row in table.data)

    def test_rename_column(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.rename_column("users", "age", "years")

        table = tables.get_table("users")
        assert table.get_column("age") is None
        assert table.get_column("years") is not None
        # Check that column was renamed in data
        assert all("age" not in row and "years" in row for row in table.data)

    def test_change_column_type(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.change_column_type("users", "age", ColumnType.string)

        table = tables.get_table("users")
        age_col = table.get_column("age")
        assert age_col.type == ColumnType.string

    def test_insert(self, tables, sample_table):
        tables.add_table(sample_table)
        new_row = {"id": 3, "name": "Charlie", "age": 35}
        tables.insert("users", new_row)

        table = tables.get_table("users")
        assert len(table.data) == 3
        assert table.data[2] == new_row

    def test_update(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.update("users", 0, {"name": "Alice Updated"})

        table = tables.get_table("users")
        assert table.data[0]["name"] == "Alice Updated"

    def test_delete(self, tables, sample_table):
        tables.add_table(sample_table)
        tables.delete("users", [0])

        table = tables.get_table("users")
        assert len(table.data) == 1
        assert table.data[0]["name"] == "Bob"


class TestExtendedTables:
    @pytest.fixture
    def base_tables(self):
        return InMemoryTables(tables=[])

    @pytest.fixture
    def extra_table(self):
        return Table(
            name="extra",
            columns=[Column(name="id", type=ColumnType.int)],
            data=[{"id": 1}],
        )

    def test_extended_tables_creation(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        assert extended.snapshot == base_tables
        assert len(extended.extra_tables) == 1

    def test_get_table_from_base(self, base_tables, extra_table):
        base_table = Table(
            name="base", columns=[Column(name="id", type=ColumnType.int)], data=[]
        )
        base_tables.add_table(base_table)

        extended = ExtendedTables(base_tables, [extra_table])
        retrieved = extended.get_table("base")
        assert retrieved is not None
        assert retrieved.name == "base"

    def test_get_table_from_extra(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        retrieved = extended.get_table("extra")
        assert retrieved is not None
        assert retrieved.name == "extra"

    def test_get_nonexistent_table(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        assert extended.get_table("nonexistent") is None

    def test_add_table(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        new_table = Table(
            name="new", columns=[Column(name="id", type=ColumnType.int)], data=[]
        )
        extended.add_table(new_table)

        assert len(extended.extra_tables) == 2
        assert extended.get_table("new") is not None

    def test_remove_table(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        extended.remove_table("extra")

        assert len(extended.extra_tables) == 0
        assert extended.get_table("extra") is None

    def test_insert_extra_table(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        extended.insert("extra", {"id": 2})

        table = extended.get_table("extra")
        assert len(table.data) == 2

    def test_update_extra_table(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        extended.update("extra", 0, {"id": 999})

        table = extended.get_table("extra")
        assert table.data[0]["id"] == 999

    def test_delete_extra_table(self, base_tables, extra_table):
        extended = ExtendedTables(base_tables, [extra_table])
        extended.delete("extra", [0])

        table = extended.get_table("extra")
        assert len(table.data) == 0


def test_new_uuid_implementation():
    """Test the new UUID-based file naming implementation"""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create tables instance
        tables = FileSystemJsonTables(workdir=temp_path)

        # Create a sample table
        table = Table(
            name="users",
            columns=[
                Column(name="id", type=ColumnType.int, is_primary_key=True),
                Column(name="name", type=ColumnType.string),
            ],
            data=[
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ],
        )

        # Add the table
        tables.add_table(table)

        # Check that the UUID-named file exists
        table_file = temp_path / f"{table.table_id}.json"
        assert table_file.exists()

        # Check schema file
        schema_file = temp_path / "__schema__.json"
        assert schema_file.exists()

        schema_content = json.loads(schema_file.read_text())
        assert table.table_id in schema_content
        assert schema_content[table.table_id]["table_name"] == "users"

        # Try to retrieve the table
        retrieved_table = tables.get_table("users")
        assert retrieved_table.name == "users"
        assert retrieved_table.table_id == table.table_id
        assert retrieved_table.data == [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]

        # Test insert
        tables.insert("users", {"id": 3, "name": "Charlie"})

        # Retrieve again
        updated_table = tables.get_table("users")
        assert len(updated_table.data) == 3
        assert updated_table.data[2] == {"id": 3, "name": "Charlie"}


def test_uuid_file_names_and_rename():
    """Test UUID-based file naming and table rename behavior"""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create tables instance
        tables = FileSystemJsonTables(workdir=temp_path)

        # Create a sample table
        table = Table(
            name="users",
            columns=[
                Column(name="id", type=ColumnType.int, is_primary_key=True),
                Column(name="name", type=ColumnType.string),
            ],
            data=[
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ],
        )

        # Add the table
        tables.add_table(table)

        # Verify initial files
        uuid_file = temp_path / f"{table.table_id}.json"
        schema_file = temp_path / "__schema__.json"

        assert uuid_file.exists()
        assert schema_file.exists()

        # Check schema content
        schema_content = json.loads(schema_file.read_text())
        assert table.table_id in schema_content
        assert schema_content[table.table_id]["table_name"] == "users"
        assert len(schema_content[table.table_id]["columns"]) == 2

        # Test rename
        tables.rename_table("users", "people")

        # File name should stay the same (UUID-based)
        assert uuid_file.exists()

        # Schema content should reflect the new table name
        schema_content_after = json.loads(schema_file.read_text())
        assert table.table_id in schema_content_after
        assert schema_content_after[table.table_id]["table_name"] == "people"

        # Should be able to retrieve by new name
        retrieved_table = tables.get_table("people")
        assert retrieved_table.name == "people"
        assert retrieved_table.table_id == table.table_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
