"""Core rounding logic for UNIX timestamps and datetimes.

This module intentionally keeps the API small: two functions that round down to the
nearest whole unit boundary.  Rounding *down* is chosen because it is the only rule
that is unambiguous for negative timestamps (before the epoch).  A "nearest" rule
would need a tie-breaking convention, and that convention is not obvious for times
before 1970.  By always flooring, we keep the behaviour predictable and testable.
"""

from datetime import datetime, timezone

_VALID_UNITS = {"second", "minute", "hour"}
_UNIT_SECONDS = {
    "second": 1,
    "minute": 60,
    "hour": 3600,
}


def _floor_div(a: int, b: int) -> int:
    """Integer floor division that works for negative numbers.

    Python's ``//`` already floors, but being explicit documents the intent and
    avoids accidental reliance on a detail that is easy to forget.
    """
    return a // b


def round_timestamp(ts: int, unit: str = "second") -> int:
    """Round a UNIX timestamp down to the nearest whole *unit*.

    Args:
        ts: Seconds since the UNIX epoch.  May be negative (before 1970).
        unit: One of ``"second"``, ``"minute"``, or ``"hour"``.

    Returns:
        The timestamp floored to the start of the unit.

    Raises:
        ValueError: If *unit* is not one of the supported units.
    """
    if unit not in _VALID_UNITS:
        raise ValueError(f"unsupported unit: {unit!r}")
    step = _UNIT_SECONDS[unit]
    if step == 1:
        return ts
    return _floor_div(ts, step) * step


def round_datetime(dt: datetime, unit: str = "second") -> datetime:
    """Round a datetime down to the nearest whole *unit*.

    The returned datetime has the same timezone information as the input.  For
    timezone-aware inputs the rounding is done on the absolute UNIX timestamp, so
    the result is independent of the local timezone offset.  For naive inputs the
    timestamp is computed assuming UTC, and the result is a naive datetime, which
    matches the kind of object the caller passed in.

    Args:
        dt: A datetime object (naive or aware).
        unit: One of ``"second"``, ``"minute"``, or ``"hour"``.

    Returns:
        A new datetime floored to the start of the unit.

    Raises:
        ValueError: If *unit* is not one of the supported units.
    """
    if unit not in _VALID_UNITS:
        raise ValueError(f"unsupported unit: {unit!r}")

    if dt.tzinfo is None:
        # Treat naive datetimes as UTC.  This avoids depending on the host's
        # local timezone, which would make tests non-deterministic.
        aware = dt.replace(tzinfo=timezone.utc)
    else:
        aware = dt

    ts = int(aware.timestamp())
    rounded_ts = round_timestamp(ts, unit)
    # Reconstruct with the original timezone so the caller gets back the same
    # kind of object they passed in.  Naive inputs stay naive.
    return datetime.fromtimestamp(rounded_ts, tz=aware.tzinfo).replace(tzinfo=dt.tzinfo)
