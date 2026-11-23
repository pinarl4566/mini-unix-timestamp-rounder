# mini-unix-timestamp-rounder

Round UNIX timestamps and `datetime` objects down to the nearest second, minute, or hour.

```python
from datetime import datetime, timezone
from mini_unix_timestamp_rounder import round_timestamp, round_datetime

# Timestamps
round_timestamp(1234567890, "minute")  # 1234567860
round_timestamp(-1, "hour")            # -3600

# Datetimes (naive or aware)
dt = datetime(2024, 1, 1, 12, 34, 56, tzinfo=timezone.utc)
round_datetime(dt, "minute")            # datetime(2024, 1, 1, 12, 34, tzinfo=timezone.utc)
round_datetime(dt, "hour")              # datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
```

## Why this exists

Rounding timestamps to a coarser granularity is a common operation when bucketing
events for aggregation.  The standard library offers no direct way to do it, and the
naive approach of dividing and multiplying by the unit size silently breaks for times
before the UNIX epoch.

The trade-off is deliberate: this library always rounds **down** (floors) rather than
to the nearest boundary.  Flooring is the only rule that behaves consistently for
negative timestamps; a "nearest" rule would need a tie-breaking convention that is
not obvious for dates before 1970.  If you need nearest-boundary rounding, you can
add half the unit size before flooring, but be aware of overflow and negative-number
semantics.

## Edge cases

- **Naive datetimes are treated as UTC.**  There is no way to know the intended
timezone of a naive `datetime`, so the library assumes UTC.  This keeps results
deterministic and independent of the host's local timezone.
- **Negative timestamps floor correctly.**  `round_timestamp(-1, "minute")` returns
  `-60`, not `0`, because `-1` is one second before the epoch and the start of that
  minute is `-60`.
- **Timezone-aware inputs keep their timezone.**  The rounding is performed on the
  absolute UNIX timestamp, then the result is converted back to the original
  timezone.

## API

- `round_timestamp(ts: int, unit: str = "second") -> int`
- `round_datetime(dt: datetime, unit: str = "second") -> datetime`

Supported units: `"second"`, `"minute"`, `"hour"`.
