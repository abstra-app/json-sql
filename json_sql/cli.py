from pathlib import Path
from .tables import FileSystemTables
from .eval import eval_sql
from argparse import ArgumentParser
from csv import DictWriter
from sys import stdout
from json import dumps


def query(code: str, workdir: Path, ctx: dict):
    tables = FileSystemTables(workdir=workdir)
    result = eval_sql(code=code, tables=tables, ctx=ctx)
    return result


if __name__ == "__main__":
    parser = ArgumentParser(description="Run SQL queries on JSON files.")
    parser.add_argument("code", type=str, help="SQL query to execute")
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
    args = parser.parse_args()

    result = query(code=args.code, workdir=args.workdir, ctx={})

    if args.format == "json":
        print(dumps(result, indent=2))
    elif args.format == "csv":
        if len(result) == 0:
            print("No results to write to CSV.")
        else:
            keys = result[0].keys()
            writer = DictWriter(stdout, fieldnames=keys)
            writer.writeheader()
            for row in result:
                writer.writerow(row)
