"""Module containing main QC functions which could be applied on a DataBundle."""

from __future__ import annotations

import math
from datetime import datetime

from .astronomical_geometry import sunangle
from .external_clim import Climatology
from .qc import (
    climatology_check,
    climatology_plus_stdev_check,
    climatology_plus_stdev_with_lowbar_check,
    failed,
    hard_limit_check,
    isvalid,
    passed,
    sst_freeze_check,
    untestable,
)
from .time_control import dayinyear, get_month_lengths, split_date


def do_position_check(latitude: float, longitude: float) -> int:
    """
    Perform the positional QC check on the report. Simple check to make sure that the latitude and longitude are
    within the bounds specified by the ICOADS documentation. Latitude is between -90 and 90. Longitude is between
    -180 and 360

    Parameters
    ----------
    latitude : float
        latitude of observation to be checked in degrees
    longitude : float
        longitude of observation to be checked in degree

    Returns
    -------
    int
        1 if either latitude or longitude is invalid, 0 otherwise
    """
    if isvalid(latitude):
        return untestable
    if isvalid(longitude):
        return untestable

    if latitude < -90 or latitude > 90:
        return failed
    if longitude < -180 or longitude > 360:
        return failed

    return passed


def do_date_check(
    date: datetime | None = None,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
) -> int:
    """
    Perform the date QC check on the report. Check that the date is valid.

    Parameters
    ----------
    date: datetime-like, optional
        Date of observation to be checked
    year : int, optional
        Year of observation to be checked
    month : int, optional
        Month of observation (1-12) to be checked
    day : int, optional
        Day of observation to be checked

    Returns
    -------
    int
        1 if the date is invalid, 0 otherwise
    """
    if isinstance(date, datetime):
        date_ = split_date(date)
        if date_ is None:
            return untestable
        year = date_["year"]
        month = date_["month"]
        day = date_["day"]
    if isvalid(year) == failed:
        return untestable
    if isvalid(month) == failed:
        return untestable
    if isvalid(day) == failed:
        return untestable

    if year > 2025 or year < 1850:
        return failed

    if month < 1 or month > 12:
        return failed

    month_lengths = get_month_lengths(year)

    if day < 1 or day > month_lengths[month - 1]:
        return failed

    return passed


def do_time_check(date: datetime | None = None, hour: float | None = None) -> int:
    """
    Check that the time is valid i.e. in the range 0.0 to 23.99999...

    Parameters
    ----------
    date: datetime-like, optional
        Date of report
    hour : float, optional
        hour of the time to be checked

    Returns
    -------
    int
        Return 1 if hour is invalid, 0 otherwise
    """
    if isinstance(date, datetime):
        date_ = split_date(date)
        if date_ is None:
            return failed
        hour = date_["hour"]
    if isvalid(hour) == failed:
        return failed

    if hour >= 24 or hour < 0:
        return failed

    return passed


def do_day_check(
    date: datetime | None = None,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    hour: float | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    time_since_sun_above_horizon: float = 1.0,
) -> int:
    """Given year month day hour lat and long calculate if the sun was above the horizon an hour ago.

    This is the "day" test used to decide whether a Marine Air Temperature (MAT) measurement is
    a Night MAT (NMAT) or a Day (MAT). This is important because solar heating of the ship biases
    the MAT measurements. It uses the function sunangle to calculate the elevation of the sun.

    Parameters
    ----------
    date: datetime-like, optional
        Date of report
    year : int, optional
        Year of report
    month : int, optional
        Month of report
    day : int, optional
        Day of report
    hour : float, optional
        Hour of report with minutes as decimal part of hour
    latitude : float, optional
        Latitude of report in degrees
    longitude : float, optional
        Longitude of report in degrees
    time_since_sun_above_horizon : float, default: 1.0
        Maximum time sun can have been above horizon (or below) to still count as night. Original QC test had this set
        to 1.0 i.e. it was night between one hour after sundown and one hour after sunrise.

    Returns
    -------
    int
        Set to 0 if it is day, 1 otherwise.
    """
    if isinstance(date, datetime):
        date_ = split_date(date)
        if date_ is None:
            return failed
        year = date_["year"]
        month = date_["month"]
        day = date_["day"]
        hour = date_["hour"]

    # Defaults to FAIL if the location, date or time are bad
    if (
        do_position_check(latitude, longitude) == 1
        or do_date_check(year=year, month=month, day=day) == 1
        or do_time_check(hour=hour) == 1
    ):
        return failed

    year2 = year
    day2 = dayinyear(year, month, day)
    hour2 = math.floor(hour)
    minute2 = (hour - math.floor(hour)) * 60.0

    # go back one hour and test if the sun was above the horizon
    hour2 = hour2 - time_since_sun_above_horizon
    if hour2 < 0:
        hour2 = hour2 + 24.0
        day2 = day2 - 1
        if day2 <= 0:
            year2 = year2 - 1
            day2 = dayinyear(year2, 12, 31)

    lat2 = latitude
    lon2 = longitude
    if latitude == 0:
        lat2 = 0.0001
    if longitude == 0:
        lon2 = 0.0001

    azimuth, elevation, rta, hra, sid, dec = sunangle(
        year2, day2, hour2, minute2, 0, 0, 0, lat2, lon2
    )
    del azimuth
    del rta
    del hra
    del sid
    del dec

    if elevation > 0:
        return passed

    return failed


def do_missing_value_check(value: float) -> int:
    """
    Check that value is not None or NaN.

    Parameters
    ----------
    value : float
        Value to be checked

    Returns
    -------
    int
        1 if value is missing, 0 otherwise
    """
    return isvalid(value)


def do_missing_value_clim_check(climatology: float | Climatology, **kwargs) -> int:
    """
    Check that climatological value is present

    Parameters
    ----------
    climatology : float or Climatology
        Climatology value
        This could be a float value or Climatology object.

    Returns
    -------
    int
        1 if climatology value is missing, 0 otherwise

    Note
    ----
    If ``climatology`` is a Climatology object, pass ``lon`` and ``lat`` and ``date`` or ``month`` and ``day`` as keyword-arguments!
    """
    if isinstance(climatology, Climatology):
        climatology = climatology.get_value(**kwargs)
    return isvalid(climatology)


def do_hard_limit_check(value: float, hard_limits: list) -> int:
    """
    Check that value is within hard limits specified by "hard_limits".

    Parameters
    ----------
    value : float
        Value to be checked.
    hard_limits : list
        2-element list containing lower and upper hard limits for the QC check.

    Returns
    -------
    int
        1 if air temperature is outside hard limits, 0 otherwise
    """
    return hard_limit_check(value, hard_limits)


def do_climatology_check(
    value: float,
    climatology: float | Climatology,
    maximum_anomaly: float,
    **kwargs,
) -> int:
    """
    Check that the value is within the prescribed distance from climatology.

    Parameters
    ----------
    value : float
        Value to be checked
    climatology: float or Climatology
        Reference climatological value.
        This could be a float value or Climatology object.
    maximum_anomaly : float
        Maximum_anomaly allowed anomaly.

    Returns
    -------
    int
        1 if value anomaly is outside allowed bounds, 0 otherwise

    Note
    ----
    If ``climatology`` is a Climatology object, pass ``lon`` and ``lat`` and ``date`` or ``month`` and ``day`` as keyword-arguments!
    """
    if isinstance(climatology, Climatology):
        climatology = climatology.get_value(**kwargs)
    return climatology_check(value, climatology, maximum_anomaly)


def do_climatology_plus_stdev_check(
    value: float,
    climatology: float | Climatology,
    stdev: float | Climatology,
    minmax_standard_deviation: list,
    maximum_standardised_anomaly: float,
    **kwargs,
) -> int:
    """Check that standardised value anomaly is within specified range.

    Value is converted into a standardised anomaly by subtracting the climatological normal and dividing by
    the climatological standard deviation. If the climatological standard deviation is outside the range specified by
    "minmax_standard_deviation" then the standard deviation is set to whichever of the lower or upper limits is
    closest. The test fails if the standardised anomaly is larger than the "maximum_standardised_anomaly".

    Parameters
    ----------
    value : float
        Value to be checked.
    climatology : float or Climatology
        Climatological normal.
        This could be a float value or Climatology object.
    stdev : float or Climatology
        Climatological standard deviation.
        This could be a float value or Climatology object.
    minmax_standard_deviation : list
        2-element list containing lower and upper limits for standard deviation. If the stdev is outside these
        limits, at_stdev will be set to the nearest limit.
    maximum_standardised_anomaly : float
        Largest allowed standardised anomaly

    Returns
    -------
    int
        Returns 1 if standardised value anomaly is outside specified range, 0 otherwise.

    Note
    ----
    If ``climatology`` and/or ``stdev`` is a Climatology object, pass ``lon`` and ``lat`` and ``date`` or ``month`` and ``day`` as keyword-arguments!
    """
    if isinstance(climatology, Climatology):
        climatology = climatology.get_value(**kwargs)
    if isinstance(stdev, Climatology):
        stdev = stdev.get_value(**kwargs)

    return climatology_plus_stdev_check(
        value,
        climatology,
        stdev,
        minmax_standard_deviation,
        maximum_standardised_anomaly,
    )


def do_climatology_plus_stdev_with_lowbar_check(
    value: float,
    climatology: float | Climatology,
    stdev: float | Climatology,
    limit: float | str,
    lowbar: float | str,
    **kwargs,
) -> int:
    """Check that standardised value anomaly is within standard deviation-based limits but with a minimum width.

    Value is converted into a standardised anomaly by subtracting the climatological normal and dividing by
    the climatological standard deviation.


    More Documentation.

    Parameters
    ----------
    value : float or Climatology
        Value or climatology to be checked.
    climatology : float or Climatology
        Climatological normal.
        This could be a float value or Climatology object.
    stdev : float or Climatology
        Climatological standard deviation.
        This could be a float value or Climatology object.
    limit : float
        Maximum standardised anomaly.
    lowbar: float
        The anomaly must be greater than lowbar to fail regardless of standard deviation.

    Returns
    -------
    int
        Returns 1 if standardised value anomaly is outside specified range, 0 otherwise.

    Note
    ----
    If ``climatology`` and/or ``stdev`` is a Climatology object, pass ``lon`` and ``lat`` and ``date`` or ``month`` and ``day`` as keyword-arguments!
    """
    if isinstance(climatology, Climatology):
        climatology = climatology.get_value(**kwargs)
    if isinstance(stdev, Climatology):
        stdev = stdev.get_value(**kwargs)

    return climatology_plus_stdev_with_lowbar_check(
        value,
        climatology,
        stdev,
        limit,
        lowbar,
    )


def do_supersaturation_check(dpt: float, at2: float) -> int:
    """
    Perform the super saturation check. Check if a valid dewpoint temperature is greater than a valid air temperature

    Parameters
    ----------
    dpt : float
        Dewpoint temperature
    at2 : float
        Air temperature

    Returns
    -------
    int
        Set to 1 if supersaturation is detected, 0 otherwise
    """
    if isvalid(dpt) == failed or isvalid(at2) == failed:
        return failed
    elif dpt > at2:
        return failed

    return passed


def do_sst_freeze_check(
    sst: float, freezing_point: float, freeze_check_n_sigma: float
) -> int:
    """
    Check that sea surface temperature is above freezing

    Parameters
    ----------
    sst : float
        Sea surface temperature to be checked
    freezing_point : float
        Freezing point of seawater to be used in check
    freeze_check_n_sigma : float
        Number of uncertainty standard deviations that sea surface temperature can be below the freezing point
        before the QC check fails.

    Returns
    -------
    int
        Return 1 if SST below freezing, 0 otherwise
    """
    return sst_freeze_check(sst, 0.0, freezing_point, freeze_check_n_sigma)


def do_wind_consistency_check(
    wind_speed: float | None,
    wind_direction: int | None,
) -> int:
    """
    Test to compare windspeed to winddirection.

    Parameters
    ----------
    wind_speed : float, optional
        Wind speed
    wind_direction : int, optional
        Wind direction

    Returns
    -------
    int
        1 if windspeed and direction are inconsistent, 0 otherwise
    """
    if isvalid(wind_speed) == failed or isvalid(wind_direction) == failed:
        return failed
    if wind_speed == 0.0 and wind_direction != 0:
        return failed

    if wind_speed != 0.0 and wind_direction == 0:
        return failed

    return passed
