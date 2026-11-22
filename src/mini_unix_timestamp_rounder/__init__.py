"""Public API for mini-unix-timestamp-rounder.

Exports:
    round_datetime(dt, unit='second') -> datetime
    round_timestamp(ts, unit='second') -> int
"""

from .core import round_datetime, round_timestamp

__all__ = ["round_datetime", "round_timestamp"]
