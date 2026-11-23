"""Reading CSV files into flight records and error messages."""
import csv
import os

from validator import to_record, validate_row

def _printable(text: str) -> str:
    return "".join(ch if ch.isprintable() else " " for ch in text)

def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
                (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """
    records: list[dict] = []
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()

    for path in paths:
        file_name = os.path.basename(os.fspath(path))

        with open(path, encoding="utf-8-sig") as handle:
            for line_number, line in enumerate(handle, start=1):
                if line_number == 1:
                    continue

                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                text = line.rstrip("\r\n")
                try:
                    fields = next(csv.reader([text]))
                except (csv.Error, StopIteration):
                    error_code = "WRONG_FIELD_COUNT"
                else:
                    error_code = validate_row(fields, airports)

                if error_code is None:
                    record = to_record(fields)
                    key = (record["flight_id"], record["departure_datetime"])
                    if key in seen:
                        error_code = "DUPLICATE_FLIGHT"
                    else:
                        seen.add(key)
                        records.append(record)

                if error_code is not None:
                    errors.append(
                        f"{file_name}:{line_number}: {error_code} | {_printable(text)}"
                    )

    return records, errors
