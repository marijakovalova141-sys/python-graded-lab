"""Running queries against the flight database."""
from validator import parse_datetime

RECORD_KEYS = (
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
)
_TEXT_KEYS = ("flight_id", "origin", "destination")
_DATETIME_KEYS = ("departure_datetime", "arrival_datetime")
_ALLOWED_KEYS = set(RECORD_KEYS) | {"min_price", "sort_by", "order", "limit"}

def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_valid_query(query) -> bool:
    if not isinstance(query, dict):
        return False

    for key, value in query.items():
        if key not in _ALLOWED_KEYS:
            return False
        if key in _TEXT_KEYS:
            if not isinstance(value, str):
                return False
        elif key in _DATETIME_KEYS:
            if parse_datetime(value) is None:
                return False
        elif key in ("price", "min_price"):
            if not _is_number(value):
                return False
        elif key == "sort_by":
            if not isinstance(value, str) or value not in RECORD_KEYS:
                return False
        elif key == "order":
            if not isinstance(value, str) or value not in ("asc", "desc"):
                return False
        elif key == "limit":
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                return False

    if "order" in query and "sort_by" not in query:
        return False
    return True


def _matches(record: dict, query: dict) -> bool:
    for key in _TEXT_KEYS:
        if key in query and record.get(key) != query[key]:
            return False

    if "departure_datetime" in query:
        departure = record.get("departure_datetime")
        if not isinstance(departure, str) or departure < query["departure_datetime"]:
            return False
    if "arrival_datetime" in query:
        arrival = record.get("arrival_datetime")
        if not isinstance(arrival, str) or arrival > query["arrival_datetime"]:
            return False

    if "price" in query or "min_price" in query:
        price = record.get("price")
        if not _is_number(price):
            return False
        if "price" in query and not price <= query["price"]:
            return False
        if "min_price" in query and not price >= query["min_price"]:
            return False

    return True

def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    if not is_valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = [record for record in db if _matches(record, query)]

    sort_by = query.get("sort_by")
    if sort_by is not None:
        matches = sorted(
            matches,
            key=lambda record: record[sort_by],
            reverse=query.get("order", "asc") == "desc",
        )

    if "limit" in query:
        matches = matches[: query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, list):
        return [run_query(db, query) for query in queries]
    return [run_query(db, queries)]

