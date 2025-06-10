"""Module containing main QC functions which could be applied on a DataBundle."""

from __future__ import annotations

import math
from datetime import datetime
from typing import Sequence

import numpy as np
import pandas as pd

from .astronomical_geometry import sunangle
from .auxiliary import failed, isvalid, passed, untestable
from .external_clim import Climatology, inspect_climatology
from .time_control import dayinyear, get_month_lengths, split_date


def climatology_check(
    value: float | None | Sequence[float | None] | np.ndarray,
    climate_normal: float | None | Sequence[float | None] | np.ndarray,
    maximum_anomaly: float,
    standard_deviation: float | None | Sequence[float | None] | np.ndarray = "default",
    standard_deviation_limits: tuple[float, float] | None = None,
    lowbar: float | None = None,
) -> int:
    """
    Climatology check to compare a value with a climatological average with some arbitrary limit on the difference.
    This check can be expanded with some optional parameters.

    Parameters
    ----------
    value: float
        Value to be compared to climatology
    climate_normal : float
        The climatological average to which it will be compared
    maximum_anomaly: float
        Largest allowed anomaly.
        If ``standard_deviation`` is provided, this is the largest allowed standardised anomaly.
    standard_deviation: float, default: "default"
        The standard deviation which will be used to standardize the anomaly
        If standard_deviation is "default", set standard_deviation to 1.0.
    standard_deviation_limits: tuple of float, optional
        A tuple of two floats representing the upper and lower limits for standard deviation used in check
    lowbar: float, optional
        The anomaly must be greater than lowbar to fail regardless of standard deviation.

    Returns
    -------
    int
        2 if stdev_limits[1] is equal or less than stdev_limits[0] or
        if limit is equal or less than 0 or
        if either value, climate_normal or standard_deviation is numerically invalid.
        1 if the difference is outside the specified range,
        0 otherwise.
    """
    value_arr = np.asarray(value, dtype=float)  # type: np.ndarray
    climate_normal_arr = np.asarray(climate_normal, dtype=float)  # type: np.ndarray

    if climate_normal_arr.ndim == 0:
        climate_normal_arr = np.full_like(
            value_arr, climate_normal_arr
        )  # type: np.ndarray

    if isinstance(standard_deviation, str) and standard_deviation == "default":
        standard_deviation = np.full(value_arr.shape, 1.0, dtype=float)
    standard_deviation_arr = np.asarray(
        standard_deviation, dtype=float
    )  # type: np.ndarray

    result = np.full(value_arr.shape, untestable, dtype=int)  # type: np.ndarray

    if maximum_anomaly is None or maximum_anomaly <= 0:
        return result

    if standard_deviation is None:
        standard_deviation_arr = np.full(value_arr.shape, 1.0)

    if standard_deviation_limits is None:
        standard_deviation_limits = (0, np.inf)
    elif standard_deviation_limits[1] <= standard_deviation_limits[0]:
        return result

    valid_indices = (
        isvalid(value)
        & isvalid(climate_normal)
        & isvalid(maximum_anomaly)
        & isvalid(standard_deviation)
    )

    standard_deviation_arr = np.clip(
        standard_deviation_arr,
        standard_deviation_limits[0],
        standard_deviation_limits[1],
    )

    climate_diff = np.zeros_like(value_arr)  # type: np.ndarray

    climate_diff[valid_indices] = np.abs(
        value_arr[valid_indices] - climate_normal_arr[valid_indices]
    )

    if lowbar is None:
        low_check = np.ones(value_arr.shape, dtype=bool)
    else:
        low_check = climate_diff > lowbar

    cond_failed = np.full(value_arr.shape, False, dtype=bool)
    cond_failed[valid_indices] = (
        climate_diff[valid_indices] / standard_deviation_arr[valid_indices]
        > maximum_anomaly
    ) & low_check[valid_indices]

    result[valid_indices & cond_failed] = failed
    result[valid_indices & ~cond_failed] = passed

    if np.isscalar(value):
        return int(result)

    if isinstance(value, pd.Series):
        return pd.Series(result, index=value.index)

    return result


def value_check(inval: float | None) -> int:
    """Check if a value is equal to None

    Parameters
    ----------
    inval : float or None
        The input value to be tested

    Returns
    -------
    int
        Returns 1 if the input value is numerically invalid or None, 0 otherwise
    """
    if isvalid(inval):
        return passed
    return failed


def hard_limit_check(val: float, limits: tuple[float, float]) -> int:
    """Check if a value is outside specified limits.

    Parameters
    ----------
    val: float
        Value to be tested.
    limits: tuple of float
        A tuple of two floats representing the lower and upper limit.

    Returns
    -------
    int
        2 if limits[1] is equal or less than limits[0] of if val is numerically invalid or None,
        1 if val is outside the limits,
        0 otherwise
    """
    if limits[1] <= limits[0]:
        return untestable

    if not isvalid(val):
        return untestable

    if limits[0] <= val <= limits[1]:
        return passed

    return failed


def sst_freeze_check(
    insst: float | None | Sequence[float | None] | np.ndarray,
    sst_uncertainty: float,
    freezing_point: float,
    n_sigma: float,
) -> int:
    """Compare an input SST to see if it is above freezing.

    This is a simple freezing point check made slightly more complex. We want to check if a
    measurement of SST is above freezing, but there are two problems. First, the freezing point
    can vary from place to place depending on the salinity of the water. Second, there is uncertainty
    in SST measurements. If we place a hard cut-off at -1.8, then we are likely to bias the average
    of many measurements too high when they are near the freezing point - observational error will
    push the measurements randomly higher and lower, and this test will trim out the lower tail, thus
    biasing the result. The inclusion of an SST uncertainty parameter *might* mitigate that and we allow
    that possibility here.

    Parameters
    ----------
    insst : float
        input SST to be checked
    sst_uncertainty : float
        the uncertainty in the SST value, defaults to zero
    freezing_point : float
        the freezing point of the water
    n_sigma : float
        number of sigma to use in the check

    Returns
    -------
    int
        2 if either insst, sst_uncertainty, freezing_point or n_sigma is numerically invalid or None,
        1 if the insst is below freezing point by more than twice the uncertainty,
        0 otherwise

    Note
    ----
    In previous versions, some parameters had default values:

        * ``sst_uncertainty``: 0.0
        * ``freezing_point``: -1.80
        * ``n_sigma``: 2.0
    """
    insst_arr = np.asarray(insst, dtype=float)  # type: np.ndarray
    result = np.full(insst_arr.shape, untestable, dtype=int)  # type: np.ndarray

    if (
        not isvalid(sst_uncertainty)
        or not isvalid(freezing_point)
        or not isvalid(n_sigma)
    ):
        return result

    valid_sst = isvalid(insst)

    cond_failed = insst_arr < (freezing_point - n_sigma * sst_uncertainty)

    result[valid_sst & cond_failed] = failed
    result[valid_sst & ~cond_failed] = passed

    if np.isscalar(insst):
        return int(result)

    if isinstance(insst, pd.Series):
        return pd.Series(result, index=insst.index)

    return result


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
        2 if either latitude or longitude is numerically invalid or None,
        1 if either latitude or longitude is not in valid range,
        0 otherwise
    """
    if not isvalid(latitude):
        return untestable
    if not isvalid(longitude):
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
        2 if either year, month or day is numerically invalid or None,
        1 if the date is not a valid date,
        0 otherwise
    """
    if isinstance(date, datetime):
        date_ = split_date(date)
        year = date_["year"]
        month = date_["month"]
        day = date_["day"]
    if not isvalid(year):
        return untestable
    if not isvalid(month):
        return untestable
    if not isvalid(day):
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
        2 if hour is numerically invalid or None,
        1 if hour is not a valid hour,
        0 otherwise
    """
    if isinstance(date, datetime):
        date_ = split_date(date)
        hour = date_["hour"]
    if not isvalid(hour):
        return untestable

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
    time_since_sun_above_horizon: float | None = None,
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
    time_since_sun_above_horizon : float
        Maximum time sun can have been above horizon (or below) to still count as night. Original QC test had this set
        to 1.0 i.e. it was night between one hour after sundown and one hour after sunrise.

    Returns
    -------
    int
        Set to 0 if it is day, 1 otherwise.

    Note
    ----
    In previous versions, ``time_since_sun_above_horizon`` has the default value 1.0 as one hour is used as a
    definition of "day" for marine air temperature QC. Solar heating biases were considered to be negligible mmore
    than one hour after sunset and up to one hour after sunrise.
    """
    if isinstance(date, datetime):
        date_ = split_date(date)
        year = date_["year"]
        month = date_["month"]
        day = date_["day"]
        hour = date_["hour"]

    p_check = do_position_check(latitude, longitude)
    d_check = do_date_check(year=year, month=month, day=day)
    t_check = do_time_check(hour=hour)

    # Defaults to FAIL if the location, date or time are bad
    if failed in [p_check, d_check, t_check]:
        return failed

    # Defaults to FAIL if the location, date or time are bad
    if untestable in [p_check, d_check, t_check]:
        return untestable

    year2 = year
    day2 = dayinyear(year, month, day)
    hour2 = math.floor(hour)
    minute2 = (hour - math.floor(hour)) * 60.0

    # go back one hour and test if the sun was above the horizon
    if time_since_sun_above_horizon is not None:
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
    return value_check(value)


@inspect_climatology("climatology")
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
    return value_check(climatology)


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
        1 if value is outside hard limits, 0 otherwise
    """
    return hard_limit_check(value, hard_limits)


@inspect_climatology("climatology", optional="standard_deviation")
def do_climatology_check(
    value: float | None | Sequence[float | None] | np.ndarray,
    climatology: float | None | Sequence[float | None] | np.ndarray | Climatology,
    maximum_anomaly: float,
    standard_deviation: (
        float | None | Sequence[float | None] | np.ndarray | Climatology
    ) = "default",
    standard_deviation_limits: list | None = None,
    lowbar: float | None = None,
    **kwargs,
) -> int | np.ndarray:
    """
    Check that the value is within the prescribed distance from climatology.

    If ``standard_deviation`` is provided, the value is converted into a standardised anomaly. Optionally,
    if ``standard deviation`` is outside the range specified by ``standard_deviation_limits`` then ``standard_deviation``
    is set to whichever of the lower or upper limits is closest.
    If ``lowbar`` is provided, the anomaly must be greater than ``lowbar`` to fail regardless of ``standard_deviation``.


    Parameters
    ----------
    value : float
        Value to be checked
    climatology: float or Climatology
        Reference climatological value.
        This could be a float value or Climatology object.
        If it is a Climatology object, pass ``lon`` and ``lat`` and ``date`` or ``month`` and ``day`` as keyword-arguments!
    maximum_anomaly : float
        Largest allowed anomaly.
        If ``standard_deviation`` is provided, this is the largest allowed standardised anomaly.
    standard_deviation : float or Climatology, default: "default"
        Climatological standard deviation.
        This could be a float value or Climatology object.
        If it is a Climatology object, pass ``lon`` and ``lat`` and ``date`` or ``month`` and ``day`` as keyword-arguments!
    standard_deviation_limits : list, optional
        2-element list containing lower and upper limits for standard deviation. If the stdev is outside these
        limits, at_stdev will be set to the nearest limit.
    lowbar: float, optional
        The anomaly must be greater than lowbar to fail regardless of standard deviation.

    Returns
    -------
    int
        2 if either value, climatology, maximum_anomaly or standard_deviation is numerically invalid or None.
        1 if value anomaly is outside allowed bounds
        0 otherwise

    Note
    ----
    If either ``climatology`` or ``standard_deviation`` is a Climatology object,
    pass ``lon`` and ``lat`` and ``date`` or ``month`` and ``day`` as keyword-arguments!
    """
    return climatology_check(
        value,
        climatology,
        maximum_anomaly=maximum_anomaly,
        standard_deviation=standard_deviation,
        standard_deviation_limits=standard_deviation_limits,
        lowbar=lowbar,
    )


def do_supersaturation_check(
    dpt: float | None | Sequence[float | None] | np.ndarray,
    at2: float | None | Sequence[float | None] | np.ndarray,
) -> int | np.ndarray:
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
        2 if either dpt or at2 is numerically invalid or None,
        1 if supersaturation is detected,
        0 otherwise
    """
    dpt_arr = np.asarray(dpt, dtype=float)  # type: np.ndarray
    at2_arr = np.asarray(at2, dtype=float)  # type: np.ndarray

    result = np.full(dpt_arr.shape, untestable, dtype=int)  # type: np.ndarray

    valid_indices = isvalid(dpt) & isvalid(at2)

    cond_failed = dpt_arr > at2_arr

    result[valid_indices & cond_failed] = failed
    result[valid_indices & ~cond_failed] = passed

    if np.isscalar(dpt) and np.isscalar(at2):
        return int(result)

    if isinstance(dpt, pd.Series):
        return pd.Series(result, index=dpt.index)

    if isinstance(at2, pd.Series):
        return pd.Series(result, index=at2.index)

    return result


def do_sst_freeze_check(
    sst: float | None | Sequence[float | None] | np.ndarray,
    freezing_point: float,
    freeze_check_n_sigma: float,
) -> int | np.ndarray:
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

    Note
    ----
    Freezing point of sea water is typically -1.8 degC or 271.35 K
    """
    return sst_freeze_check(sst, 0.0, freezing_point, freeze_check_n_sigma)


def do_wind_consistency_check(
    wind_speed: float | None | Sequence[float | None] | np.ndarray,
    wind_direction: float | None | Sequence[float | None] | np.ndarray,
) -> int | np.ndarray:
    """
    Test to compare windspeed to winddirection.

    Parameters
    ----------
    wind_speed : float, None, array-like of float or None
        Wind speed values to be tested
    wind_direction : float, None, array-like of float or None
        Wind direction values to be tested

    Returns
    -------
    int or np.ndarray of int
        2 if either wind_speed or wind_direction is numerically invalid or None,
        1 if windspeed and direction are inconsistent,
        0 otherwise
        Returns a integer scalar if input is scalar, else a integer array.
    """
    wind_speed_arr = np.asarray(wind_speed, dtype=float)  # type: np.ndarray
    wind_direction_arr = np.asarray(wind_direction, dtype=float)  # type: np.ndarray

    result = np.full(wind_speed_arr.shape, untestable, dtype=int)  # type: np.ndarray

    valid_indices = isvalid(wind_speed) & isvalid(wind_direction)

    cond_failed = ((wind_speed_arr == 0) & (wind_direction_arr != 0)) | (
        (wind_speed_arr != 0) & (wind_direction_arr == 0)
    )

    result[valid_indices & cond_failed] = failed
    result[valid_indices & ~cond_failed] = passed

    if np.isscalar(wind_speed) and np.isscalar(wind_direction):
        return int(result)

    if isinstance(wind_speed, pd.Series):
        return pd.Series(result, index=wind_speed.index)

    if isinstance(wind_direction, pd.Series):
        return pd.Series(result, index=wind_speed.index)

    return result
