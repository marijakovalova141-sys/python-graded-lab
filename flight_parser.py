"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import argparse
import contextlib
import json
import logging
import os
import sys
from datetime import datetime

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "241RWC028"
FIRST_NAME = "Marija"
LAST_NAME = "Kovalova"

class RuntimeProblem(Exception):
    pass


def _one_line(text) -> str:
    return " ".join(str(text).split())


def _describe(exc: Exception) -> str:
    if isinstance(exc, OSError):
        reason = exc.strerror or str(exc)
        return f"{reason}: '{exc.filename}'" if exc.filename else reason
    return str(exc)


@contextlib.contextmanager
def _runtime_guard(action: str):
    try:
        yield
    except (OSError, UnicodeError) as exc:
        raise RuntimeProblem(f"cannot {action}: {_describe(exc)}") from exc


def _say(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "backslashreplace").decode("ascii"))


def _write_json(path: str, data) -> None:
    with _runtime_guard(f"write '{path}'"):
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")


def _read_json(path: str, what: str):
    try:
        with open(path, encoding="utf-8-sig") as handle:
            return json.load(handle)
    except OSError as exc:
        raise RuntimeProblem(f"cannot read {what} '{path}': {_describe(exc)}") from exc
    except ValueError as exc:
        raise RuntimeProblem(f"{what} '{path}' is not valid JSON: {_one_line(exc)}") from exc


def _load_database(path: str) -> list[dict]:
    data = _read_json(path, "database file")
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise RuntimeProblem(f"database file '{path}' must be a JSON array of objects")
    return data


def _load_queries(path: str):
    data = _read_json(path, "query file")
    if not isinstance(data, (dict, list)):
        raise RuntimeProblem(
            f"query file '{path}' must contain a query object or an array of query objects"
        )
    return data


def _collect_csv_files(folder: str) -> list[str]:
    with _runtime_guard(f"read folder '{folder}'"):
        names = sorted(os.listdir(folder))
    paths = [
        os.path.join(folder, name)
        for name in names
        if name.endswith(".csv") and os.path.isfile(os.path.join(folder, name))
    ]
    if not paths:
        raise RuntimeProblem(f"no .csv files found in folder '{folder}'")
    return paths


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flight_parser.py",
        description="Validate flight schedule CSV files, store the valid flights "
                    "as a JSON database and answer queries against it. "
                    "Exactly one data source (-i, -d or -j) is required.",
        epilog="examples:\n"
               "  python flight_parser.py -i data/db.csv -a data/airports.txt\n"
               "  python flight_parser.py -d data/flights -a data/airports.txt -o out/db.json\n"
               "  python flight_parser.py -j out/db.json -q data/query.json -r out/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-i", metavar="FILE", help="parse a single CSV file")
    parser.add_argument("-d", metavar="FOLDER",
                        help="parse every .csv file in the folder (sorted by name, no sub-folders)")
    parser.add_argument("-j", metavar="FILE",
                        help="load an existing JSON database instead of parsing CSV files")
    parser.add_argument("-a", metavar="FILE",
                        help="airport list file (required with -i and -d, ignored with -j)")
    parser.add_argument("-o", metavar="FILE",
                        help="output path of the JSON database (default: db.json); only with -i or -d")
    parser.add_argument("-q", metavar="FILE", help="run the queries in this JSON file")
    parser.add_argument("-r", metavar="FOLDER",
                        help="folder for the query response file (default: current directory)")
    return parser


def _parse_args(argv):
    parser = _build_parser()
    args = parser.parse_args(None if argv is None else [str(item) for item in argv])

    sources = [name for name in ("i", "d", "j") if getattr(args, name) is not None]
    if len(sources) != 1:
        parser.error("exactly one data source is required: -i, -d or -j")
    if args.j is None and args.a is None:
        parser.error("-a is required with -i and -d")
    if args.j is not None and args.o is not None:
        parser.error("-o cannot be used with -j")
    return args


def _exit_code(exc: SystemExit) -> int:
    if exc.code is None:
        return 0
    return exc.code if isinstance(exc.code, int) else 1


def _build_database_from_csv(args) -> list[dict]:
    db_path = args.o if args.o is not None else "db.json"
    log_path = os.path.join(os.path.dirname(db_path), "errors.log")

    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    handler = None
    try:
        with _runtime_guard(f"create log file '{log_path}'"):
            handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)

        try:
            with _runtime_guard(f"read airport file '{args.a}'"):
                airports = load_airports(args.a)
            paths = [args.i] if args.i is not None else _collect_csv_files(args.d)
            with _runtime_guard("read the CSV data"):
                records, errors = parse_files(paths, airports)
        except RuntimeProblem as exc:
            logger.error("%s", _one_line(exc))
            raise

        for message in errors:
            logger.warning("%s", message)
        logger.info("Processed %d file(s): %d valid row(s), %d invalid row(s)",
                    len(paths), len(records), len(errors))

        _write_json(db_path, records)
        _say(f"{len(records)} valid flight(s), {len(errors)} invalid row(s).")
        return records
    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


def _write_response(results: list[dict], folder: str) -> None:
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    name = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{stamp}.json"
    _write_json(os.path.join(folder, name), results)
    _say(f"Query results written for {len(results)} query(ies).")


def _run(args) -> int:
    queries = _load_queries(args.q) if args.q is not None else None

    if args.j is not None:
        records = _load_database(args.j)
    else:
        records = _build_database_from_csv(args)

    if queries is not None:
        results = run_queries(records, queries)
        _write_response(results, args.r if args.r is not None else ".")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    # TODO: parse arguments with argparse (-i, -d, -j, -a, -o, -q, -r).
    # TODO: load or parse the data, write the database and errors.log.
    # TODO: run the queries and write the response file.
    # Remember: remove and close the logging handler before returning,
    # also when returning early because of an error (use try/finally).
    try:
        args = _parse_args(argv)
    except SystemExit as exc:
        return _exit_code(exc)

    try:
        return _run(args)
    except RuntimeProblem as exc:
        print(f"Error: {_one_line(exc)}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: unexpected problem ({type(exc).__name__}: {_one_line(exc)})",
              file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
