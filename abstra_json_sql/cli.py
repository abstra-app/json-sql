from argparse import ArgumentParser
from csv import DictWriter
from json import dumps
from pathlib import Path
from sys import stdout
from typing import List, Literal

from .eval import eval_sql
from .persistence import FileSystemJsonLTables
from .tables import Column, ColumnType, Table


def query(code: str, workdir: Path, ctx: dict):
    tables = FileSystemJsonLTables(workdir=workdir)
    result = eval_sql(code=code, tables=tables, ctx=ctx)
    return result


def print_result(result: List[dict], format: Literal["json", "csv"]):
    if format == "json":
        print(dumps(result, indent=2))
    elif format == "csv":
        if len(result) == 0:
            print("No results to write to CSV.")
        else:
            keys = result[0].keys()
            writer = DictWriter(stdout, fieldnames=keys)
            writer.writeheader()
            for row in result:
                writer.writerow(row)


def interactive_create_table(workdir: Path):
    """Create a table interactively by asking user for table name, columns, etc."""
    try:
        tables = FileSystemJsonLTables(workdir=workdir)

        # Get table name
        print("Creating a new table...")
        while True:
            table_name = input("Table name: ").strip()
            if not table_name:
                print("Table name cannot be empty. Please try again.")
                continue
            try:
                # Check if table already exists
                existing_table = tables.get_table(table_name)
                if existing_table:
                    print(
                        f"Table '{table_name}' already exists. Please choose a different name."
                    )
                    continue
                break
            except FileNotFoundError:
                # Table doesn't exist, which is what we want
                break

        # Get columns
        columns = []
        print(f"\nNow let's add columns to the '{table_name}' table.")
        print("Available column types: int, string, float, bool")
        print("Press Enter with empty column name to finish adding columns.\n")

        while True:
            column_name = input("Column name: ").strip()
            if not column_name:
                if len(columns) == 0:
                    print("At least one column is required. Please add a column.")
                    continue
                break

            # Check if column name already exists
            if any(col.name == column_name for col in columns):
                print(
                    f"Column '{column_name}' already exists. Please choose a different name."
                )
                continue

            # Get column type
            while True:
                column_type_str = (
                    input(f"Column type for '{column_name}' (int/string/float/bool): ")
                    .strip()
                    .lower()
                )
                if column_type_str in ["int", "string", "float", "bool"]:
                    column_type = ColumnType(column_type_str)
                    break
                else:
                    print(
                        "Invalid column type. Please enter: int, string, float, or bool"
                    )

            # Ask if it's a primary key
            is_primary = (
                input(f"Is '{column_name}' a primary key? (y/N): ").strip().lower()
            )
            is_primary_key = is_primary in ["y", "yes"]

            # Ask for default value
            default_value = None
            has_default = (
                input(f"Does '{column_name}' have a default value? (y/N): ")
                .strip()
                .lower()
            )
            if has_default in ["y", "yes"]:
                while True:
                    default_str = input(f"Default value for '{column_name}': ").strip()
                    try:
                        # Convert default value to the appropriate type
                        if column_type == ColumnType.int:
                            default_value = int(default_str) if default_str else None
                        elif column_type == ColumnType.float:
                            default_value = float(default_str) if default_str else None
                        elif column_type == ColumnType.bool:
                            if default_str.lower() in ["true", "1", "yes", "y"]:
                                default_value = True
                            elif default_str.lower() in ["false", "0", "no", "n"]:
                                default_value = False
                            elif default_str == "":
                                default_value = None
                            else:
                                raise ValueError("Invalid boolean value")
                        else:  # string
                            default_value = default_str if default_str else None
                        break
                    except ValueError:
                        print(
                            f"Invalid default value for {column_type.value} type. Please try again."
                        )

            # Create column
            column = Column(
                name=column_name,
                schema=column_type,
                is_primary_key=is_primary_key,
                default=default_value,
            )
            columns.append(column)
            print(f"✓ Added column '{column_name}' ({column_type.value})")

        # Create and add the table
        table = Table(name=table_name, columns=columns, data=[])
        tables.add_table(table)

        print(f"\n✓ Table '{table_name}' created successfully!")
        print("Columns:")
        for col in columns:
            pk_indicator = " (PRIMARY KEY)" if col.is_primary_key else ""
            default_indicator = (
                f" (default: {col.default})" if col.default is not None else ""
            )
            print(f"  - {col.name}: {col.type.value}{pk_indicator}{default_indicator}")

    except KeyboardInterrupt:
        print("\n\nTable creation cancelled.")
    except Exception as e:
        print(f"\nError creating table: {e}")


def main():
    parser = ArgumentParser(description="Run SQL queries on JSON files.")

    # Add top-level arguments for backward compatibility
    parser.add_argument("--code", type=str, help="SQL query to execute", default=None)
    parser.add_argument(
        "--workdir",
        type=Path,
        default=Path.cwd(),
        help="Directory containing JSON files",
    )
    parser.add_argument(
        "--ctx",
        type=str,
        default="{}",
        help="Context for the query (default: empty dictionary)",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="json",
        choices=["json", "csv"],
        help="Output format (default: json)",
    )

    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Query command
    query_parser = subparsers.add_parser("query", help="Run SQL queries")
    query_parser.add_argument(
        "--code", type=str, help="SQL query to execute", default=None
    )
    query_parser.add_argument(
        "--workdir",
        type=Path,
        default=Path.cwd(),
        help="Directory containing JSON files",
    )
    query_parser.add_argument(
        "--ctx",
        type=str,
        default="{}",
        help="Context for the query (default: empty dictionary)",
    )
    query_parser.add_argument(
        "--format",
        type=str,
        default="json",
        choices=["json", "csv"],
        help="Output format (default: json)",
    )

    # Create table command
    create_parser = subparsers.add_parser("create", help="Create database objects")
    create_subparsers = create_parser.add_subparsers(
        dest="create_command", help="Create commands"
    )

    table_parser = create_subparsers.add_parser("table", help="Create a table")
    table_parser.add_argument(
        "--interactive", action="store_true", help="Create table interactively"
    )
    table_parser.add_argument(
        "--workdir",
        type=Path,
        default=Path.cwd(),
        help="Directory to create the table in",
    )

    args = parser.parse_args()

    # Handle commands
    if args.command == "create" and args.create_command == "table":
        if args.interactive:
            interactive_create_table(args.workdir)
        else:
            print("Please use --interactive flag to create a table interactively.")
            print("Usage: abstra-json-sql create table --interactive")
    elif args.command == "query":
        # Query subcommand
        if args.code:
            result = query(code=args.code, workdir=args.workdir, ctx={})
            print_result(result=result, format=args.format)
        else:
            print("JSON SQL CLI")
            print("Type 'exit' to quit.")
            while True:
                try:
                    code = input("> ")
                    if code.lower() == "exit":
                        break
                    result = query(code=code, workdir=args.workdir, ctx={})
                    print_result(result=result, format=args.format)
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
                except SystemExit:
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    continue
    elif args.command is None:
        # Backward compatibility: if no command specified, use top-level arguments
        if args.code:
            result = query(code=args.code, workdir=args.workdir, ctx={})
            print_result(result=result, format=args.format)
        else:
            print("JSON SQL CLI")
            print("Type 'exit' to quit.")
            print(
                "Tip: Use 'abstra-json-sql create table --interactive' to create tables."
            )
            while True:
                try:
                    code = input("> ")
                    if code.lower() == "exit":
                        break
                    result = query(code=code, workdir=args.workdir, ctx={})
                    print_result(result=result, format=args.format)
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
                except SystemExit:
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    continue
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
