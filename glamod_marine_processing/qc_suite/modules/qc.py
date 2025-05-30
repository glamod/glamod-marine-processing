"""The QC module contains a set of functions for performing the basic QC checks on marine reports."""

from __future__ import annotations

from .auxiliary import isvalid

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
        Maximum standardised anomaly.
    lowbar : float
        The anomaly must be greater than lowbar to fail regardless of standard deviation.

    Returns
    -------
    int
        2 if limit is equal or less than 0 or if either value, climate_normal or standard_deviation is numerically invalid or None
        1 if the difference is outside the specified range,
        0 otherwise.

    Raises
    ------
    ValueError
        When limit is zero or negative
    """
    if (
        not isvalid(value)
        or not isvalid(climate_normal)
        or not isvalid(standard_deviation)
    ):
        return untestable

    if limit <= 0:
        return untestable

    if (
        abs(value - climate_normal) / standard_deviation > limit
        and abs(value - climate_normal) > lowbar
    ):
        return failed

    return passed


def climatology_plus_stdev_check(
    value: float,
    climate_normal: float,
    standard_deviation: float,
    stdev_limits: tuple[float, float],
    limit: float,
) -> int:
    """
    Climatology check which uses standardised anomalies.
    Lower and upper limits can be specified for the standard deviation using
    stdev_limits. The value is converted to an anomaly by subtracting the climate normal and then standardised by
    dividing by the standard deviation. If the standardised anomaly is larger than the specified limit the test fails.

    Parameters
    ----------
    value : float
        Value to be compared to climatology
    climate_normal : float
        The climatological average to which the value will be compared
    standard_deviation : float
        The climatological standard deviation which will be used to standardise the anomaly
    stdev_limits : tuple of float
        A tuple of two floats representing the upper and lower limits for standard deviation used in check
    limit : float
        The maximum allowed normalised anomaly

    Returns
    -------
    int
        2 if stdev_limits[1] is equal or less than stdev_limits[0], if limit is equal or less than 0 or
        if either value, climatE_normal or standard_deviation is numerically invalid or None,
        1 if the difference is outside the specified limit,
        0 otherwise (or if any input is None)

    Raises
    ------
    ValueError
        When stdev_limits are in wrong order or limit is zero or negative.
    """
    if (
        not isvalid(value)
        or not isvalid(climate_normal)
        or not isvalid(standard_deviation)
    ):
        return untestable

    if stdev_limits[1] <= stdev_limits[0]:
        return untestable
    if limit <= 0:
        return untestable

    if standard_deviation < stdev_limits[0]:
        standard_deviation = stdev_limits[0]
    if standard_deviation > stdev_limits[1]:
        standard_deviation = stdev_limits[1]

    if abs(value - climate_normal) / standard_deviation > limit:
        return failed

    return passed


def climatology_check(value: float, climate_normal: float, limit: float) -> int:
    """Simple function to compare a value with a climatological average with some arbitrary limit on the difference.
    This may be the second simplest function I have ever written (see blacklist)

    Parameters
    ----------
    value : float
        Value to be compared to climatology
    climate_normal : float
        The climatological average to which the value will be compared
    limit : float
        The maximum allowed difference between the ``value`` and ``climate_normal``.

    Returns
    -------
    int
        2 if limit is equal or less than 0 or if either value or climate_normal is numerically invalid or None,
        1 if the difference is outside the specified limit,
        0 otherwise

    Note
    ----
    In previous versions, ``limit`` had the default value 8.0.
    """
    if not isvalid(value) or not isvalid(climate_normal) or not isvalid(limit):
        return untestable

    if limit <= 0:
        return untestable

    if abs(value - climate_normal) > limit:
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
    insst: float,
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
    if not isvalid(insst):
        return untestable
    if not isvalid(sst_uncertainty):
        return untestable
    if not isvalid(freezing_point):
        return untestable
    if not isvalid(n_sigma):
        return untestable

    # fail if SST below the freezing point by more than twice the uncertainty
    if insst < (freezing_point - n_sigma * sst_uncertainty):
        return failed

    return passed
