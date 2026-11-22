import unittest
from datetime import datetime, timezone, timedelta

from mini_unix_timestamp_rounder import round_datetime, round_timestamp


class TestRoundTimestamp(unittest.TestCase):
    def test_second_is_identity(self):
        self.assertEqual(round_timestamp(1234567890, "second"), 1234567890)
        self.assertEqual(round_timestamp(0, "second"), 0)
        self.assertEqual(round_timestamp(-1, "second"), -1)

    def test_minute_rounds_down(self):
        self.assertEqual(round_timestamp(0, "minute"), 0)
        self.assertEqual(round_timestamp(59, "minute"), 0)
        self.assertEqual(round_timestamp(60, "minute"), 60)
        self.assertEqual(round_timestamp(61, "minute"), 60)
        self.assertEqual(round_timestamp(119, "minute"), 60)
        self.assertEqual(round_timestamp(120, "minute"), 120)

    def test_hour_rounds_down(self):
        self.assertEqual(round_timestamp(0, "hour"), 0)
        self.assertEqual(round_timestamp(3599, "hour"), 0)
        self.assertEqual(round_timestamp(3600, "hour"), 3600)
        self.assertEqual(round_timestamp(3601, "hour"), 3600)
        self.assertEqual(round_timestamp(7199, "hour"), 3600)
        self.assertEqual(round_timestamp(7200, "hour"), 7200)

    def test_negative_timestamps_floor(self):
        # -1 should floor to the start of the previous minute, i.e. -60.
        self.assertEqual(round_timestamp(-1, "minute"), -60)
        self.assertEqual(round_timestamp(-60, "minute"), -60)
        self.assertEqual(round_timestamp(-61, "minute"), -120)
        self.assertEqual(round_timestamp(-1, "hour"), -3600)
        self.assertEqual(round_timestamp(-3600, "hour"), -3600)
        self.assertEqual(round_timestamp(-3601, "hour"), -7200)

    def test_invalid_unit_raises(self):
        with self.assertRaises(ValueError):
            round_timestamp(0, "day")
        with self.assertRaises(ValueError):
            round_timestamp(0, "")
        with self.assertRaises(ValueError):
            round_timestamp(0, "SECOND")


class TestRoundDatetime(unittest.TestCase):
    def test_naive_utc(self):
        dt = datetime(2024, 1, 1, 12, 34, 56)
        self.assertEqual(round_datetime(dt, "second"), datetime(2024, 1, 1, 12, 34, 56))
        self.assertEqual(round_datetime(dt, "minute"), datetime(2024, 1, 1, 12, 34, 0))
        self.assertEqual(round_datetime(dt, "hour"), datetime(2024, 1, 1, 12, 0, 0))

    def test_aware_utc(self):
        dt = datetime(2024, 1, 1, 12, 34, 56, tzinfo=timezone.utc)
        self.assertEqual(
            round_datetime(dt, "minute"),
            datetime(2024, 1, 1, 12, 34, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(
            round_datetime(dt, "hour"),
            datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

    def test_aware_non_utc(self):
        tz = timezone(timedelta(hours=5, minutes=30))
        dt = datetime(2024, 1, 1, 12, 34, 56, tzinfo=tz)
        # 12:34:56+05:30 is 07:04:56 UTC.  Rounding to the hour should give
        # 07:00:00 UTC, which is 12:30:00+05:30.
        self.assertEqual(
            round_datetime(dt, "hour"),
            datetime(2024, 1, 1, 12, 30, 0, tzinfo=tz),
        )

    def test_rounding_preserves_tzinfo(self):
        tz = timezone(timedelta(hours=-8))
        dt = datetime(2024, 1, 1, 0, 0, 1, tzinfo=tz)
        rounded = round_datetime(dt, "minute")
        self.assertEqual(rounded.tzinfo, tz)
        self.assertEqual(rounded, datetime(2024, 1, 1, 0, 0, 0, tzinfo=tz))

    def test_invalid_unit_raises(self):
        dt = datetime(2024, 1, 1)
        with self.assertRaises(ValueError):
            round_datetime(dt, "day")


if __name__ == "__main__":
    unittest.main()
