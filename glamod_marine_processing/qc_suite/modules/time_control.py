"""Some generally helpful time control functions for base QC."""

from __future__ import annotations

import calendar
import math
from datetime import datetime, timedelta

import numpy as np


def split_date(date):
    """Split datetime date into year, month, day and hour.

    Parameters
    ----------
    date: datetime
        Date to split

    Returns
    -------
    dict
        Dictionary containing year, month, day and hour.
    """
    try:
        year = int(date.year)
        month = int(date.month)
        day = int(date.day)
        hour = date.hour + date.minute / 60.0 + date.second / 3600.0
    except ValueError:
        return None
    return {"year": year, "month": month, "day": day, "hour": hour}


def month_match(
    y1: int,
    m1: int,
    y2: int,
    m2: int,
) -> int:
    """Check whether month matches.

    Parameters
    ----------
    y1: int
        First year to check.
    m1: int
        First month to check.
    y2: int
        Second year to check.
    m2: int
        Second month to check.

    Returns
    -------
    int
        Returns True if both `y1` and `y2` and `m1` and `m2` match, else False.
    """
    if y1 == y2 and m1 == m2:
        return True
    return False


def yesterday(
    year: int,
    month: int,
    day: int,
) -> (int, int, int) | (None, None, None):
    """For specified year, month and day return the year, month and day of the day before.

    Parameters
    ----------
    year: int
        Current year.
    month: int
        Current month.
    day: int
        Current day.

    Returns
    -------
    (int, int, int, int) or (None, None, None, None)
        year, month and day of the day before, returns a tuple of ``None`` values if the input day does not exist (e.g. Feb 30th).
    """
    try:
        dt = datetime(year, month, day)
        delta = timedelta(-1)
        dt = dt + delta
        return dt.year, dt.month, dt.day
    except Exception:
        return None, None, None


def season(month: int) -> str | None:
    """Return short season name for given month, ``None`` for months like 13 that do not exist.

    Parameters
    ----------
    month: int
        Current month.

    Returns
    -------
    str or None
        Name of the season with includes `month` (DJF, MAM, JJA, or SON) or ``None`` if the input month is non-existent (e.g. 13).
    """
    if month < 1 or month > 12:
        return None
    ssnlist = [
        "DJF",
        "DJF",
        "MAM",
        "MAM",
        "MAM",
        "JJA",
        "JJA",
        "JJA",
        "SON",
        "SON",
        "SON",
        "DJF",
    ]
    return ssnlist[month - 1]


def pentad_to_month_day(p: int) -> (int, int):
    """Given a pentad number, return the month and day of the first day in the pentad.

    Parameters
    ----------
    p: int
        Pentad number from 1 to 73

    Returns
    -------
    (int, int)
        Month and day of the first day of the pentad.
    """
    assert 0 < p < 74, "p outside allowed range 1-73 " + str(p)
    m = [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        2,
        2,
        2,
        2,
        2,
        3,
        3,
        3,
        3,
        3,
        3,
        4,
        4,
        4,
        4,
        4,
        4,
        5,
        5,
        5,
        5,
        5,
        5,
        5,
        6,
        6,
        6,
        6,
        6,
        6,
        7,
        7,
        7,
        7,
        7,
        7,
        8,
        8,
        8,
        8,
        8,
        8,
        9,
        9,
        9,
        9,
        9,
        9,
        10,
        10,
        10,
        10,
        10,
        10,
        11,
        11,
        11,
        11,
        11,
        11,
        12,
        12,
        12,
        12,
        12,
        12,
    ]
    d = [
        1,
        6,
        11,
        16,
        21,
        26,
        31,
        5,
        10,
        15,
        20,
        25,
        2,
        7,
        12,
        17,
        22,
        27,
        1,
        6,
        11,
        16,
        21,
        26,
        1,
        6,
        11,
        16,
        21,
        26,
        31,
        5,
        10,
        15,
        20,
        25,
        30,
        5,
        10,
        15,
        20,
        25,
        30,
        4,
        9,
        14,
        19,
        24,
        29,
        3,
        8,
        13,
        18,
        23,
        28,
        3,
        8,
        13,
        18,
        23,
        28,
        2,
        7,
        12,
        17,
        22,
        27,
        2,
        7,
        12,
        17,
        22,
        27,
    ]
    return m[p - 1], d[p - 1]


def which_pentad(inmonth: int, inday: int) -> int:
    """Take month and day as inputs and return pentad in range 1-73.

    Parameters
    ----------
    inmonth: int
        Month containing the day for which we want to calculate the pentad.
    inday: int
        Day for the day for which we want to calculate the pentad.

    Returns
    -------
    int
        Pentad (5-day period) containing input day, from 1 (1 Jan-5 Jan) to 73 (27-31 Dec).

    Note
    ----
    The calculation is rather simple. It just loops through the year and adds up days till it reaches
    the day we are interested in. February 29th is treated as though it were March 1st in a regular year.
    """
    if not (12 >= inmonth >= 1):
        raise ValueError(f"Month {inmonth} not in range 1-12")
    if not (31 >= inday >= 1):
        raise ValueError(f"Day {inday} not in range 1-31")

    pentad = int((day_in_year(inmonth, inday) - 1) / 5)
    pentad = pentad + 1

    assert pentad >= 1
    assert pentad <= 73

    return pentad


def day_in_year(month: int, day: int) -> int:
    """
    Find the day number of a particular day from Jan 1st which is 1 to Dec 31st which is 365.

    29 February is treated as 1 March

    Parameters
    ----------
    month : int
        Month to be processed
    day : int
        Day in the month

    Returns
    -------
    int
        Day number in year 1-365

    Raises
    ------
    ValueError
        When month not in range 1-12 or day not in range 1-31
    """
    if month < 1 or month > 12:
        raise ValueError("Month not in range 1-12")
    month_lengths = get_month_lengths(2004)
    if day < 1 or day > month_lengths[month - 1]:
        raise ValueError(f"Day not in range 1-{month_lengths[month - 1]}")

    month_lengths = get_month_lengths(2003)

    if month == 1:
        dindex = day
    elif month == 2 and day == 29:
        dindex = day_in_year(3, 1)
    else:
        dindex = np.sum(month_lengths[0 : month - 1]) + day

    return dindex


def relative_year_number(year: int, reference: int = 1979) -> int:
    """Get number of year relative to reference year (1979 by default).

    Parameters
    ----------
    year : int
        Year
    reference : int
        Reference year, defaults to 1979

    Returns
    -------
    int
        Number of year relateive to reference year.
    """
    return year - (reference + 1)


def convert_time_in_hours(
    hour: int, minute: int, sec: int, zone: int | float, dasvtm: float
) -> float:
    """Convert integer hour, minute, and second to time in decimal hours

    Parameters
    ----------
    hour : int
        Hour
    minute : int
        Minute
    sec : int
        Second
    zone : int or float
        Correction for timezone
    dasvtm : float
        Unknown

    Returns
    -------
    float
        Time converted to decimal hour in day
    """
    return hour + (minute + sec / 60.0) / 60.0 + zone - dasvtm


def leap_year(delyear: int) -> int:
    """Get leap year.

    Parameters
    ----------
    delyear: int

    Returns
    -------
    int
        Get previous leap year.
    """
    return math.floor(delyear / 4.0)


def time_in_whole_days(time_in_hours: int, day: int, delyear: int, leap: int) -> float:
    """Calculate from time in hours to time in whole days.

    Parameters
    ----------
    time_in_hours: int
    day: int
    delyear: int
    leap: int

    Returns
    -------
    float
        Time in whole days.
    """
    return delyear * 365 + leap + day - 1.0 + time_in_hours / 24.0


def leap_year_correction(time_in_hours: int, day: int, delyear: int) -> float:
    """Make leap year correction.

    Parameters
    ----------
    time_in_hours: int
    day: int
    delyear: int

    Returns
    -------
    float
        Leap year corrected time.
    """
    leap = leap_year(delyear)
    time = time_in_whole_days(time_in_hours, day, delyear, leap)
    if delyear == leap * 4.0:
        time = time - 1.0
    if delyear < 0 and delyear != leap * 4.0:
        time = time - 1.0
    return time


def dayinyear(year: int, month: int, day: int) -> int:
    """Calculate the day in year, running from 1 for Jan 1st to 365 (or 366) for Dec 31st.

    Parameters
    ----------
    year: int
        Year.
    month: int
        Month.
    day: int
        Day.

    Returns
    -------
    int
        Day in year, between 1 and 366.
    """
    assert 1 <= month <= 12
    assert day >= 1

    month_lengths = get_month_lengths(year)

    assert day <= month_lengths[month - 1], "Day out of range " + str(day)

    result = day
    if month > 1:
        result = result + sum(month_lengths[0 : month - 1])

    assert 1 <= result <= 366
    return result


def jul_day(year: int, month: int, day: int) -> int:
    """Routine to calculate julian day. This is the weird Astronomical thing which counts from 1 Jan 4713 BC.

    Parameters
    ----------
    year: int
        Year.
    month: int
        Month.
    day: int
        Day.

    Returns
    -------
    int
        Julian day.

    Note
    ----
    This is one of those routines that looks baffling but works. No one is sure exactly how. It gets
    written once and then remains untouched for centuries, mysteriously working.
    """
    assert 1 <= month <= 12
    assert 1 <= day <= 31
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + ((153 * m + 2) // 5) + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def time_difference(
    year1: int,
    month1: int,
    day1: int,
    hour1: int,
    year2: int,
    month2: int,
    day2: int,
    hour2: int,
) -> float:
    """Calculate time difference in hours between any two times.

    Parameters
    ----------
    year1: int
        Year of first time point.
    month1: int
        Month of first time point.
    day1: int
        Day of first time point.
    hour1: int
        Hour of first time point.
    year2: int
        Year of second time point.
    month2: int
        Month of second time point.
    day2: int
        Day of second time point.
    hour2: int
        Hour of second time point.

    Returns
    -------
    float
        Difference in hours between the two times.
    """
    # return time difference in hours
    if None in [year1, year2, month1, month2, day1, day2, hour1, hour2]:
        return

    assert 0 <= hour1 < 24 and 0 <= hour2 < 24

    if (
        (year1 > year2)
        or (year1 == year2 and month1 > month2)
        or (year1 == year2 and month1 == month2 and day1 > day2)
        or (year1 == year2 and month1 == month2 and day1 == day2 and hour1 > hour2)
    ):
        return -1 * time_difference(
            year2, month2, day2, hour2, year1, month1, day1, hour1
        )

    first_day = jul_day(year1, month1, day1) + hour1 / 24.0
    last_day = jul_day(year2, month2, day2) + hour2 / 24.0

    timdif = 24.0 * (last_day - first_day)

    return timdif


def last_month_was(year: int, month: int) -> (int, int):
    """Short function to get the previous month given a particular month of interest

    Parameters
    ----------
    year : int
        Year of interest
    month : int
        Month of interest

    Returns
    -------
    (int, int)
        Year and month of previous month

    """
    last_year = year
    last_month = month - 1
    if last_month == 0:
        last_month = 12
        last_year = year - 1

    return last_year, last_month


def next_month_is(year: int, month: int) -> (int, int):
    """Short function to get the next month given a particular month of interest

    Parameters
    ----------
    year : int
        Year of interest
    month : int
        Month of interest

    Returns
    -------
    (int, int)
        Year and month of next month
    """
    next_year = year
    next_month = month + 1
    if next_month > 12:
        next_month = 1
        next_year = year + 1

    return next_year, next_month


def year_month_gen(year1: int, month1: int, year2: int, month2: int) -> (int, int):
    """A generator to loop one month at a time between year1 month1 and year2 month2

    Parameters
    ----------
    year1 : int
        Year of start month
    month1 : int
        Month of start month
    year2 : int
        Year of end month
    month2 : int
        Month of end month

    Returns
    -------
    (int, int)
        Return an iterator that yields tuples of a year and month
    """
    if year2 < year1:
        raise ValueError(
            f"year1 is greater than year2: year1 = {year1}, year2 = {year2}."
        )
    if not (0 < month1 <= 12):
        raise ValueError(f"month1 is not in valid range (1 to 12): month1 = {month1}.")
    if not (0 < month2 <= 12):
        raise ValueError(f"month2 is not in valid range (1 to 12): month2 = {month2}.")

    year = year1
    month = month1

    while not (year == year2 and month == month2):
        yield year, month
        month += 1
        if month > 12:
            month = 1
            year += 1

    yield year, month


def get_month_lengths(year: int) -> list[int]:
    """Return a list holding the lengths of the months in a given year

    Parameters
    ----------
    year : int
        Year for which you want month lengths

    Returns
    -------
    list[int]
        list of month lengths
    """
    if calendar.isleap(year):
        month_lengths = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    return month_lengths
