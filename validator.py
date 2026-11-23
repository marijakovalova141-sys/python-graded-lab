"""Row validation: airport list loading, single-row checks, record building."""
import math
import re
from datetime import datetime

_FLIGHT_ID_RE = re.compile(r"[A-Za-z0-9]{2,8}")
_AIRPORT_CODE_RE = re.compile(r"[A-Z]{3}")
_DATETIME_RE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2})")

def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """
    codes = set()
    with open(path, encoding="utf-8-sig") as handle:
        for line in handle:
            code = line.strip()
            if code and not code.startswith("#"):
                codes.add(code)
    return codes

def parse_datetime(text) -> datetime | None:
    if not isinstance(text, str):
        return None
    match = _DATETIME_RE.fullmatch(text)
    if match is None:
        return None
    year, month, day, hour, minute = (int(part) for part in match.groups())
    try:
        return datetime(year, month, day, hour, minute)
    except ValueError:
        return None


def _is_airport(code: str, airports: set[str]) -> bool:
    return _AIRPORT_CODE_RE.fullmatch(code) is not None and code in airports

def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    flight_id, origin, destination, departure, arrival, price = (
        field.strip() for field in fields
    )

    if "" in (flight_id, origin, destination, departure, arrival, price):
        return "MISSING_FIELD"

    if _FLIGHT_ID_RE.fullmatch(flight_id) is None:
        return "INVALID_FLIGHT_ID"

    if not _is_airport(origin, airports):
        return "INVALID_ORIGIN"
    if not _is_airport(destination, airports):
        return "INVALID_DESTINATION"

    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    departure_dt = parse_datetime(departure)
    if departure_dt is None:
        return "INVALID_DEPARTURE"
    arrival_dt = parse_datetime(arrival)
    if arrival_dt is None:
        return "INVALID_ARRIVAL"

    if arrival_dt <= departure_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        value = float(price)
    except ValueError:
        return "INVALID_PRICE"
    if not math.isfinite(value):
        return "INVALID_PRICE"

    if value <= 0:
        return "NON_POSITIVE_PRICE"

    return None



def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    flight_id, origin, destination, departure, arrival, price = (
        field.strip() for field in fields
    )
    return {
        "flight_id": flight_id,
        "origin": origin,
        "destination": destination,
        "departure_datetime": departure,
        "arrival_datetime": arrival,
        "price": float(price),
    }
