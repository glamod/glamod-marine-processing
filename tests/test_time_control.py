from __future__ import annotations

from datetime import datetime

import numpy as np
import pytest

from glamod_marine_processing.qc_suite.modules.time_control import (
    convert_date_to_hours,
    day_in_year,
    last_month_was,
    leap_year_correction,
    month_match,
    next_month_is,
    pentad_to_month_day,
    season,
    split_date,
    which_pentad,
    year_month_gen,
    yesterday,
)


@pytest.mark.parametrize(
    "date, expected_year, expected_month, expected_day, expected_hour",
    [
        (datetime(2002, 3, 27, 17, 30), 2002, 3, 27, 17.5),
    ],
)
def test_split_date(date, expected_year, expected_month, expected_day, expected_hour):
    result = split_date(date)
    expected = {
        "year": expected_year,
        "month": expected_month,
        "day": expected_day,
        "hour": expected_hour,
    }
    for key in expected:
        assert result[key] == expected[key]


@pytest.mark.parametrize(
    "y1, m1, y2, m2, expected",
    [
        (2024, 1, 2024, 1, True),
        (2023, 1, 2024, 1, False),
        (2024, 1, 2024, 2, False),
        (2021, 12, 2025, 3, False),
    ],
)
def test_month_match(y1, m1, y2, m2, expected):
    assert month_match(y1, m1, y2, m2) == expected


@pytest.mark.parametrize(
    "year, month, day, expected_year, expected_month, expected_day",
    [
        (2024, 1, 1, 2023, 12, 31),
        (2024, 3, 1, 2024, 2, 29),
        (2023, 3, 1, 2023, 2, 28),
        (2024, 12, 31, 2024, 12, 30),
        (2024, 2, 29, 2024, 2, 28),
    ],
)
def test_yesterday(year, month, day, expected_year, expected_month, expected_day):
    assert yesterday(year, month, day) == (
        expected_year,
        expected_month,
        expected_day,
    )


def test_yesterday_nan():
    year, month, day = yesterday(2025, 2, 29)
    assert np.isnan(year)
    assert np.isnan(month)
    assert np.isnan(day)


@pytest.mark.parametrize(
    "month, expected",
    [
        (1, "DJF"),
        (2, "DJF"),
        (3, "MAM"),
        (4, "MAM"),
        (5, "MAM"),
        (6, "JJA"),
        (7, "JJA"),
        (8, "JJA"),
        (9, "SON"),
        (10, "SON"),
        (11, "SON"),
        (12, "DJF"),
        (0, None),
        (-1, None),
        (13, None),
    ],
)
def test_seasons(month, expected):
    assert season(month) == expected


def test_pentad_to_mont():
    for p in range(1, 74):
        m, d = pentad_to_month_day(p)
        assert p == which_pentad(m, d)


@pytest.mark.parametrize(
    "month, day, expected",
    [
        (1, 6, 2),
        (1, 21, 5),
        (12, 26, 72),
        (1, 1, 1),
        (12, 31, 73),
        (2, 29, 12),
        (3, 1, 12),
    ],
)
def test_which_pentad(month, day, expected):
    assert which_pentad(month, day) == expected


def test_which_pentad_raises_value_error():
    with pytest.raises(ValueError):
        which_pentad(13, 1)
    with pytest.raises(ValueError):
        which_pentad(1, 41)


def test_day_in_year_leap_year():
    assert day_in_year(2, 29) == day_in_year(3, 1)

    # Just test all days
    month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    count = 1
    for month in range(1, 13):
        for day in range(1, month_lengths[month - 1] + 1):
            assert day_in_year(month, day) == count
            count += 1


def test_day_in_year_leap_year_test():
    with pytest.raises(ValueError):
        day_in_year(13, 1)
    with pytest.raises(ValueError):
        day_in_year(0, 1)
    with pytest.raises(ValueError):
        day_in_year(2, 30)
    with pytest.raises(ValueError):
        day_in_year(2, 0)


def test_leap_year_correction():
    assert leap_year_correction(24, 1, 0) == 0
    assert leap_year_correction(24, 1, 4) == 1461
    assert leap_year_correction(24, 1, -3) == -1096


def test_year_month_gen():
    years = [year for year, month in year_month_gen(2001, 1, 2001, 12)]
    months = [month for year, month in year_month_gen(2001, 1, 2001, 12)]
    for year in years:
        assert year == 2001
    assert months == list(range(1, 13))

    years = [year for year, month in year_month_gen(2000, 1, 2001, 12)]
    months = [month for year, month in year_month_gen(2000, 1, 2001, 12)]
    assert len(years) == 24
    for year in years:
        assert year in [2000, 2001]
    assert months == list(range(1, 13)) + list(range(1, 13))


def test_year_month_gen_raises():
    with pytest.raises(ValueError):
        list(year_month_gen(2000, 1, 1999, 2))
    with pytest.raises(ValueError):
        list(year_month_gen(1999, -1, 2000, 2))
    with pytest.raises(ValueError):
        list(year_month_gen(1999, 1, 2000, 13))


@pytest.mark.parametrize(
    "year, month, expected",
    [
        (1989, 12, (1989, 11)),
        (2010, 9, (2010, 8)),
        (2025, 1, (2024, 12)),
    ],
)
def test_last_month_was(year, month, expected):
    assert last_month_was(year, month) == expected


@pytest.mark.parametrize(
    "year, month, expected",
    [
        (1989, 12, (1990, 1)),
        (2010, 9, (2010, 10)),
        (2025, 1, (2025, 2)),
    ],
)
def test_next_month_is(year, month, expected):
    assert next_month_is(year, month) == expected


@pytest.mark.parametrize(
    "dates, expected",
    [
        ([datetime(2000, 1, 1, 0, 0), datetime(2000, 1, 1, 1, 0)], [0, 1]),
        ([datetime(1999, 12, 31, 23, 0), datetime(2000, 1, 1, 1, 0)], [0, 2]),
    ],
)
def test_convert_date_to_hour(dates, expected):
    assert (convert_date_to_hours(dates) == expected).all()
