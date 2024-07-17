"""Unit test file for nexthink_api"""
from pydantic import ValidationError
import pytest

from nexthink_api import NxtDateTime


class TestNxtDateTime:

    #  valid 4-digit year within range 1000-9999
    def test_valid_4_digit_year(self):
        dt = NxtDateTime(year=2023, month=5, day=15, hour=10, minute=30, second=45)
        assert dt.year == 2023

    #  valid 2-digit year converted to 2000+ format
    def test_valid_2_digit_year_conversion(self):
        dt = NxtDateTime(year=23, month=5, day=15, hour=10, minute=30, second=45)
        assert dt.year == 2023

    #  2-digit year at boundary (e.g., 99, 00)
    def test_2_digit_year_boundary(self):
        dt = NxtDateTime(year=99, month=5, day=15, hour=10, minute=30, second=45)
        assert dt.year == 2099
        dt = NxtDateTime(year=0, month=5, day=15, hour=10, minute=30, second=45)
        assert dt.year == 2000

    #  4-digit year at boundary (e.g., 1000, 9999)
    def test_4_digit_year_boundary(self):
        dt = NxtDateTime(year=1000, month=5, day=15, hour=10, minute=30, second=45)
        assert dt.year == 1000
        dt = NxtDateTime(year=9999, month=5, day=15, hour=10, minute=30, second=45)
        assert dt.year == 9999

    #  valid month within range 1-12
    def test_valid_month_range(self):
        dt = NxtDateTime(year=2023, month=7, day=15, hour=10, minute=30, second=45)
        assert dt.month == 7

    #  month at boundary (e.g., 1, 12)
    def test_month_boundary(self):
        dt = NxtDateTime(year=2023, month=1, day=15, hour=10, minute=30, second=45)
        assert dt.month == 1
        dt = NxtDateTime(year=2023, month=12, day=15, hour=10, minute=30, second=45)
        assert dt.month == 12

    #  day at boundary (e.g., 1, 31)
    def test_day_boundary(self):
        dt = NxtDateTime(year=2023, month=5, day=1, hour=10, minute=30, second=45)
        assert dt.day == 1
        dt = NxtDateTime(year=2023, month=5, day=31, hour=10, minute=30, second=45)
        assert dt.day == 31

    def test_hour_boundary(self):
        dt = NxtDateTime(year=2023, month=5, day=15, hour=0, minute=30, second=45)
        assert dt.hour == 0
        dt = NxtDateTime(year=2023, month=5, day=15, hour=23, minute=30, second=45)
        assert dt.hour == 23

    def test_minute_boundary(self):
        dt = NxtDateTime(year=2023, month=5, day=15, hour=10, minute=0, second=45)
        assert dt.minute == 0
        dt = NxtDateTime(year=2023, month=5, day=15, hour=10, minute=59, second=45)
        assert dt.minute == 59

    def test_second_boundary(self):
        dt = NxtDateTime(year=2023, month=5, day=15, hour=10, minute=30, second=0)
        assert dt.second == 0
        dt = NxtDateTime(year=2023, month=5, day=15, hour=10, minute=30, second=59)
        assert dt.second == 59

    def test_invalid_year(self):
        with pytest.raises(ValueError):
            NxtDateTime(year=20232, month=5, day=15, hour=10, minute=30, second=45)

    def test_invalid_month(self):
        with pytest.raises(ValueError):
            NxtDateTime(year=2023, month=13, day=15, hour=10, minute=30, second=45)

    def test_invalid_day(self):
        with pytest.raises(ValueError):
            NxtDateTime(year=2023, month=5, day=32, hour=10, minute=30, second=45)

    def test_invalid_hour(self):
        with pytest.raises(ValueError):
            NxtDateTime(year=2023, month=5, day=15, hour=24, minute=30, second=45)

    def test_invalid_minute(self):
        with pytest.raises(ValueError):
            NxtDateTime(year=2023, month=5, day=15, hour=10, minute=60, second=45)

    def test_invalid_second(self):
        with pytest.raises(ValueError):
            NxtDateTime(year=2023, month=5, day=15, hour=10, minute=30, second=60)

    #  invalid date (e.g., 2/30/2023)
    def test_invalid_date(self):
        with pytest.raises(ValidationError):
            NxtDateTime(year=2023, month=2, day=30, hour=10, minute=30, second=45)

    def test_json_serialization(self):
        dt = NxtDateTime(year=2023, month=5, day=15, hour=10, minute=30, second=45)
        assert dt.model_dump() == {"year": 2023, "month": 5, "day": 15, "hour": 10, "minute": 30, "second": 45}

    def test_json_deserialization(self):
        dt = NxtDateTime.model_validate({"year": 2023, "month": 5, "day": 15, "hour": 10, "minute": 30, "second": 45})
        assert dt.year == 2023
        assert dt.month == 5
        assert dt.day == 15
        assert dt.hour == 10
        assert dt.minute == 30
        assert dt.second == 45
