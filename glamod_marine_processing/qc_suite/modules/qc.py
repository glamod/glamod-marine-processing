"""The QC module contains a set of functions for performing the basic QC checks on marine reports."""

from __future__ import annotations

import math

import numpy as np

passed = 0
failed = 1
untestable = 2
untested = 3


def climatology_plus_stdev_with_lowbar_check(
    value: float,
    climate_normal: float,
    standard_deviation: float,
    limit: float,
    lowbar: float,
) -> int:
    """
    Climatology check with standard deviation-based limits but with a minimum width

    Parameters
    ----------
    value : float
        Value to be compared to climatology
    climate_normal : float
        The climatological average to which it will be compared
    standard_deviation : float
        The standard deviation which will be used to test the anomaly
    limit : float
        Maximum standardised anomaly
    lowbar : float
        The anomaly must be greater than lowbar to fail regardless of standard deviation

    Returns
    -------
    int
        Return 1 if the difference is outside the specified range, 0 otherwise.

    Raises
    ------
    ValueError
        When limit is zero or negative
    """
    if limit <= 0:
        return untestable

    if value is None or climate_normal is None or standard_deviation is None:
        return failed

    if np.isnan(value) or np.isnan(climate_normal) or np.isnan(standard_deviation):
        return failed

    if (
        abs(value - climate_normal) / standard_deviation > limit
        and abs(value - climate_normal) > lowbar
    ):
        return failed

    return passed


def climatology_plus_stdev_check(
    value: float | None,
    climate_normal: float | None,
    standard_deviation: float | None,
    stdev_limits: list[float, float],
    limit: float,
) -> int:
    """
    Climatology check which uses standardised anomalies.
    Lower and upper limits can be specified for the standard deviation using
    stdev_limits. The value is converted to an anomaly by subtracting the climate normal and then standardised by
    dividing by the standard deviation. If the standardised anomaly is larger than the specified limit the test fails.

    Parameters
    ----------
    value : float or None
        Value to be compared to climatology
    climate_normal : float or None
        The climatological average to which the value will be compared
    standard_deviation : float or None
        The climatological standard deviation which will be used to standardise the anomaly
    stdev_limits : list[float, float]
        Upper and lower limits for standard deviation used in check
    limit : float
        The maximum allowed normalised anomaly

    Returns
    -------
    int
        Return 1 if the difference is outside the specified limit, 0 otherwise (or if any input is None)

    Raises
    ------
    ValueError
        When stdev_limits are in wrong order or limit is zero or negative.
    """
    if not (stdev_limits[1] > stdev_limits[0]):
        return untestable
    if limit <= 0:
        return untestable

    if (
        isvalid(value) == 1
        or isvalid(climate_normal) == 1
        or isvalid(standard_deviation) == 1
    ):
        return failed

    stdev = standard_deviation
    if stdev < stdev_limits[0]:
        stdev = stdev_limits[0]
    if stdev > stdev_limits[1]:
        stdev = stdev_limits[1]

    if abs(value - climate_normal) / stdev > limit:
        return failed

    return passed


def climatology_check(
    value: float | None, climate_normal: float | None, limit: float = 8.0
) -> int:
    """Simple function to compare a value with a climatological average with some arbitrary limit on the difference.
    This may be the second simplest function I have ever written (see blacklist)

    Parameters
    ----------
    value : float or None
        Value to be compared to climatology
    climate_normal : float or None
        The climatological average to which the value will be compared
    limit : float
        The maximum allowed difference between the two

    Returns
    -------
    int
        Return 1 if the difference is outside the specified limit, 0 otherwise
    """
    # if value is None or climate_normal is None or limit is None:
    if isvalid(value) == 1 or isvalid(climate_normal) == 1 or isvalid(limit) == 1:
        return failed

    if abs(value - climate_normal) > limit:
        return failed

    return passed


def isvalid(inval: float | None) -> int:
    """Check if a value is numerically valid.

    Parameters
    ----------
    inval : float or None
        The input value to be tested

    Returns
    -------
    int
        Returns 1 if the input value is numerically invalid, 0 otherwise
    """
    if inval is None or math.isnan(inval):
        return failed
    return passed


def value_check(inval: float | None) -> int:
    """Check if a value is equal to None

    Parameters
    ----------
    inval : float or None
        The input value to be tested

    Returns
    -------
    int
        Returns 1 if the input value is None, 0 otherwise.
    """
    if inval is None:
        return failed
    return passed


def no_normal_check(inclimav: float | None) -> int:
    """Check if a climatological average is equal to None.

    Parameters
    ----------
    inclimav: float or None
        The input value

    Returns
    -------
    int
        Returns 1 if the input value is None, 0 otherwise.
    """
    if inclimav is None:
        return failed
    return passed


def hard_limit_check(val: float | None, limits: list) -> int:
    """Check if a value is outside specified limits.

    Parameters
    ----------
    val: float or None
        Value to be tested.
    limits: list
        Two membered list of lower and upper limit.

    Returns
    -------
    int
        Returns 1 if the input is outside the limits, 0 otherwise

    Raises
    ------
    ValueError
        When limits are specified in wrong order. First element should be lower than second
    """
    if not (limits[1] > limits[0]):
        return untestable

    if isvalid(val) == failed:
        return failed

    if limits[0] <= val <= limits[1]:
        return passed

    return failed


def sst_freeze_check(
    insst: float | None,
    sst_uncertainty: float = 0.0,
    freezing_point: float = -1.80,
    n_sigma: float = 2.0,
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
    insst : float or None
        input SST to be checked
    sst_uncertainty : float
        the uncertainty in the SST value, defaults to zero, defaults to 0.0
    freezing_point : float
        the freezing point of the water, defaults to -1.8C
    n_sigma : float
        number of sigma to use in the check, defaults to 2.0

    Returns
    -------
    int
        1 if the input SST is below freezing point by more than twice the uncertainty, 0 otherwise

    Raises
    ------
    ValueError
        When sst_uncertainty or freezing_point is None
    """
    if sst_uncertainty is None:
        return untestable
    if freezing_point is None:
        return untestable

    # fail if SST below the freezing point by more than twice the uncertainty
    if isvalid(insst) == failed:
        return failed

    if insst < (freezing_point - n_sigma * sst_uncertainty):
        return failed

    return passed
