"""
The trackqc module contains a set of functions for performing the tracking QC
first described in Atkinson et al. [2013]. The general procedures described
in Atkinson et al. [2013] were later revised and improved for the SST CCI 2 project.
Documentation and IDL code for the revised (and original) procedures can be found
in the CMA FCM code repository. The code in this module represents a port of the
revised IDL code into the python marine QC suite. New versions of the aground
and speed checks have also been added.

These functions perform tracking QC checks on a class`.Voyage`

References:

Atkinson, C.P., N.A. Rayner, J. Roberts-Jones, R.O. Smith, 2013:
Assessing the quality of sea surface temperature observations from
drifting buoys and ships on a platform-by-platform basis (doi:10.1002/jgrc.20257).
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

import glamod_marine_processing.qc_suite.modules.spherical_geometry as sg

from .astronomical_geometry import sunangle
from .time_control import dayinyear


def track_day_test(
    year: int,
    month: int,
    day: int,
    hour: float,
    lat: float,
    lon: float,
    elevdlim: float = -2.5,
) -> bool:
    """Given date, time, lat and lon calculate if the sun elevation is > elevdlim. If so return True

    This is the "day" test used by tracking QC to decide whether an SST measurement is night or day.
    This is important because daytime diurnal heating can affect comparison with an SST background.
    It uses the function sunangle to calculate the elevation of the sun. A default solar_zenith angle
    of 92.5 degrees (elevation of -2.5 degrees) delimits night from day.

    Parameters
    ----------
    year : int
        Year
    month : int
        Month
    day : int
        Day
    hour : float
        Hour expressed as decimal fraction (e.g. 20.75 = 20:45 pm)
    lat : float
        Latitude in degrees
    lon : float
        Longitude in degrees
    elevdlim : float
        Elevation day/night delimiter in degrees above horizon

    Returns
    -------
    bool
        True if daytime, else False.
    """
    if year is None:
        raise ValueError("year is missing")
    if month is None:
        raise ValueError("month is missing")
    if day is None:
        raise ValueError("day is missing")
    if hour is None:
        raise ValueError("hour is missing")
    if lat is None:
        raise ValueError("lat is missing")
    if lon is None:
        raise ValueError("lon is missing")
    if not (1 <= month <= 12):
        raise ValueError("Month not in range 1-12")
    if not (1 <= day <= 31):
        raise ValueError("Day not in range 1-31")
    if not (0 <= hour <= 24):
        raise ValueError("Hour not in range 0-24")
    if not (90 >= lat >= -90):
        raise ValueError("Latitude not in range -90 to 90")

    daytime = False

    year2 = year
    day2 = dayinyear(year, month, day)
    hour2 = math.floor(hour)
    minute2 = (hour - math.floor(hour)) * 60.0
    lat2 = lat
    lon2 = lon
    if lat == 0:
        lat2 = 0.0001
    if lon == 0:
        lon2 = 0.0001

    azimuth, elevation, rta, hra, sid, dec = sunangle(
        year2, day2, hour2, minute2, 0, 0, 0, lat2, lon2
    )
    del azimuth
    del rta
    del hra
    del sid
    del dec

    if elevation > elevdlim:
        daytime = True

    return daytime


def trim_mean(inarr: list, trim: float) -> float:
    """Calculate a resistant (aka robust) mean of an input array given a trimming criteria.

    Parameters
    ----------
    inarr : list
        array of numbers
    trim : float
        trimming criteria. A value of 10 trims one tenth of the values off each end of the sorted array
        before calculating the mean.

    Returns
    -------
    float
        Returns trimmed mean
    """
    arr = np.array(inarr)  # type: np.ndarray
    if trim == 0:
        return np.mean(arr)

    length = len(arr)
    arr.sort()

    index1 = int(length / trim)

    trim = np.mean(arr[index1 : length - index1])

    return trim


def trim_std(inarr: list, trim: float) -> float:
    """Calculate a resistant (aka robust) standard deviation of an input array given a trimming criteria.

    Parameters
    ----------
    inarr : list
        array of numbers
    trim : float
        trimming criteria. A value of 10 trims one tenth of the values off each end of the sorted array before
        calculating the standard deviation.

    Returns
    -------
    float
        trimmed standard deviation
    """
    arr = np.array(inarr)  # type: np.ndarray
    if trim == 0:
        return np.std(arr)

    length = len(arr)
    arr.sort()

    index1 = int(length / trim)

    trim = np.std(arr[index1 : length - index1])

    return trim


def assert_window_and_periods(
    smooth_win=1, min_win_period=1, max_win_period=None
) -> (int, int, int):
    """Assert smooth window and window periods

    Parameters
    ----------
    smooth_win: int
        Smoothing window, must be >= 1 and odd, defaults to 1
    min_win_period : int
        maximum window period must be >=1 and less than max_win_period, defaults to 1
    max_win_period
        minimum window period must be >=1 and greater than min_win_period, defaults to None

    Returns
    -------
    int, int, int
        Return the smoothing window, minimum window period and maximum window period
    """
    smooth_win = int(smooth_win)
    assert smooth_win >= 1, "smooth_win must be >= 1"
    assert smooth_win % 2 != 0, "smooth_win must be an odd number"
    min_win_period = int(min_win_period)
    assert min_win_period >= 1, "min_win_period must be >= 1"
    if max_win_period is not None:
        max_win_period = int(max_win_period)
        assert max_win_period >= 1, "max_win_period must be >= 1"
        assert (
            max_win_period >= min_win_period
        ), "max_win_period must be >= min_win_period"
    return smooth_win, min_win_period, max_win_period


def assert_limit_periods(
    speed_limit: float = 2.5,
    min_win_period: float = 1,
    max_win_period: float = None,
) -> (float, float, float):
    """Assert speed limit and window periods.

    Parameters
    ----------
    speed_limit : float
        Speed limit
    min_win_period : float
        Minimum window period
    max_win_period : float
        Maximum window period

    Returns
    -------
    float, float, float
        Returns speed_limit, min_win_period, max_win_period
    """
    """"""
    speed_limit = float(speed_limit)
    assert speed_limit >= 0, "speed_limit must be >= 0"
    min_win_period = float(min_win_period)
    assert min_win_period >= 0, "min_win_period must be >= 0"
    if max_win_period is not None:
        max_win_period = float(max_win_period)
        assert max_win_period >= 0, "max_win_period must be >= 0"
        assert (
            max_win_period >= min_win_period
        ), "max_win_period must be >= min_win_period"
    return speed_limit, min_win_period, max_win_period


def assert_drifters(
    n_eval=1,
    bias_lim=1.10,
    drif_intra=1.0,
    drif_inter=0.29,
    err_std_n=3.0,
    n_bad=2,
    background_err_lim=0.3,
):
    """Assert drifter sea surface temperature record."""
    n_eval = int(n_eval)
    bias_lim = float(bias_lim)
    drif_intra = float(drif_intra)
    drif_inter = float(drif_inter)
    err_std_n = float(err_std_n)
    n_bad = int(n_bad)
    background_err_lim = float(background_err_lim)
    assert n_eval > 0, "n_eval must be > 0"
    assert bias_lim >= 0, "bias_lim must be >= 0"
    assert drif_intra >= 0, "drif_intra must be >= 0"
    assert drif_inter >= 0, "drif_inter must be >= 0"
    assert err_std_n >= 0, "err_std_n must be >= 0"
    assert n_bad >= 1, "n_bad must be >= 1"
    assert background_err_lim >= 0, "background_err_lim must be >= 0"
    return (
        n_eval,
        bias_lim,
        drif_intra,
        drif_inter,
        err_std_n,
        n_bad,
        background_err_lim,
    )


def assert_window_drifters(
    long_win_len=1,
    long_err_std_n=3.0,
    short_win_len=1,
    short_err_std_n=3.0,
    short_win_n_bad=1,
    drif_inter=0.29,
    drif_intra=1.00,
    background_err_lim=0.3,
):
    """Assert drifter and window parameters."""
    long_win_len = int(long_win_len)
    long_err_std_n = float(long_err_std_n)
    short_win_len = int(short_win_len)
    short_err_std_n = float(short_err_std_n)
    short_win_n_bad = int(short_win_n_bad)
    drif_inter = float(drif_inter)
    drif_intra = float(drif_intra)
    background_err_lim = float(background_err_lim)
    assert long_win_len >= 1, "long_win_len must be >= 1"
    assert long_win_len % 2 != 0, "long_win_len must be an odd number"
    assert long_err_std_n >= 0, "long_err_std_n must be >= 0"
    assert short_win_len >= 1, "short_win_len must be >= 1"
    assert short_err_std_n >= 0, "short_err_std_n must be >= 0"
    assert short_win_n_bad >= 1, "short_win_n_bad must be >= 1"
    assert drif_inter >= 0, "drif_inter must be >= 0"
    assert drif_intra >= 0, "drif_intra must be >= 0"
    assert background_err_lim >= 0, "background_err_lim must be >= 0"
    return (
        long_win_len,
        long_err_std_n,
        short_win_len,
        short_err_std_n,
        short_win_n_bad,
        drif_inter,
        drif_intra,
        background_err_lim,
    )


def retrieve_lon_lat_hrs(df):
    """Retrieve lon/lat/time_diff variables from DataFrame."""
    nrep = len(df)
    lon = np.array(nrep * [np.nan])  # type: np.ndarray
    lat = np.array(nrep * [np.nan])  # type: np.ndarray
    hrs = np.array(nrep * [np.nan])  # type: np.ndarray
    for i in range(nrep):
        row = df.iloc[i]
        lon[i] = row.lat  # returns None if missing
        lat[i] = row.lon  # returns None if missing
        if i == 0:
            hrs[i] = 0
        else:
            hrs[i] = row.time_diff  # raises assertion error if 'time_diff' not found
    assert not any(np.isnan(lon)), "Nan(s) found in longitude"
    assert not any(np.isnan(lat)), "Nan(s) found in latitude"
    assert not any(np.isnan(hrs)), "Nan(s) found in time differences"
    assert not any(hrs < 0), "times are not sorted"
    hrs = np.cumsum(hrs)
    return lon, lat, hrs


def create_smoothed_lon_lat_hrs(
    lon: np.ndarray = np.array([np.nan]),
    lat: np.ndarray = np.array([np.nan]),
    hrs: np.ndarray = np.array([np.nan]),
    nrep: int = 1,
    smooth_win: int = 1,
    half_win: int = 0,
):
    """Create smoothed lon/lat timeseries."""
    lon_smooth = np.array(nrep * [np.nan])  # type: np.ndarray
    lat_smooth = np.array(nrep * [np.nan])  # type: np.ndarray
    hrs_smooth = np.array(nrep * [np.nan])  # type: np.ndarray

    nrep_smooth = nrep - smooth_win + 1
    for i in range(0, nrep_smooth):
        lon_smooth[i] = np.median(lon[i : i + smooth_win])
        lat_smooth[i] = np.median(lat[i : i + smooth_win])
        hrs_smooth[i] = hrs[i + half_win]
    assert not any(np.isnan(lon_smooth)), "Nan(s) found in smoothed longitude"
    assert not any(np.isnan(lat_smooth)), "Nan(s) found in smoothed latitude"
    assert not any(np.isnan(hrs_smooth)), "Nan(s) found in smoothed time differences"
    return lon_smooth, lat_smooth, hrs_smooth


def check_drifter_aground(
    lon_smooth: np.ndarray = np.array([np.nan]),
    lat_smooth: np.ndarray = np.array([np.nan]),
    hrs_smooth: np.ndarray = np.array([np.nan]),
    min_win_period: int = 1,
    max_win_period: int | None = None,
):
    """Check whether drifter has run aground."""
    i = 0
    is_aground = False  # keeps track of whether drifter is deemed aground
    i_aground = np.nan  # keeps track of index when drifter first ran aground
    min_win_period_hours = min_win_period * 24.0
    if max_win_period is None:
        max_win_period_hours = None
    else:
        max_win_period_hours = max_win_period * 24.0
    tolerance = sg.sphere_distance(0, 0, 0.01, 0.01)

    time_to_end = hrs_smooth[-1] - hrs_smooth[i]
    while time_to_end >= min_win_period_hours:
        if max_win_period_hours is not None:
            f_win = hrs_smooth <= hrs_smooth[i] + max_win_period_hours
            win_len = hrs_smooth[f_win][-1] - hrs_smooth[i]
            if win_len < min_win_period_hours:
                i += 1
                time_to_end = hrs_smooth[-1] - hrs_smooth[i]
                continue

        displace = sg.sphere_distance(
            lat_smooth[i], lon_smooth[i], lat_smooth[f_win][-1], lon_smooth[f_win][-1]
        )
        if displace <= tolerance:
            if is_aground:
                i += 1
                time_to_end = hrs_smooth[-1] - hrs_smooth[i]
                continue
            else:
                is_aground = True
                i_aground = i
                i += 1
                time_to_end = hrs_smooth[-1] - hrs_smooth[i]
        else:
            is_aground = False
            i_aground = np.nan
            i += 1
            time_to_end = hrs_smooth[-1] - hrs_smooth[i]
    return is_aground, i_aground


def check_drifter_speed(
    df: pd.DataFrame,
    lon: np.ndarray = np.array([np.nan]),
    lat: np.ndarray = np.array([np.nan]),
    hrs: np.ndarray = np.array([np.nan]),
    speed_limit: float = 2.5,
    min_win_period: int = 1,
    max_win_period: float | int | None = None,
    iquam_track_ship=None,
):
    """Check whether drifter is moving too fast and flag any occurrences."""
    nrep = len(df)
    drf_speed = np.zeros(nrep)  # type: np.ndarray

    index_arr = np.array(range(0, nrep))
    i = 0
    time_to_end = hrs[-1] - hrs[i]
    min_win_period_hours = min_win_period * 24.0
    if max_win_period is None:
        max_win_period_hours = None
    else:
        max_win_period_hours = max_win_period * 24.0
    while time_to_end >= min_win_period_hours:
        if iquam_track_ship is not None:
            if iquam_track_ship[i] == 1:
                i += 1
                time_to_end = hrs[-1] - hrs[i]
                continue
            f_win = (hrs >= hrs[i] + min_win_period_hours) & (iquam_track_ship == 0)
            if not any(f_win):
                i += 1
                time_to_end = hrs[-1] - hrs[i]
                continue
            win_len = hrs[f_win][0] - hrs[i]
            ind = 0
        else:
            f_win = hrs <= hrs[i] + max_win_period_hours
            win_len = hrs[f_win][-1] - hrs[i]
            ind = -1
            if win_len < min_win_period_hours:
                i += 1
                time_to_end = hrs[-1] - hrs[i]
                continue

        displace = sg.sphere_distance(lat[i], lon[i], lat[f_win][ind], lon[f_win][ind])
        speed = displace / win_len  # km per hr
        speed = speed * 1000.0 / (60.0 * 60)  # metres per sec

        if speed > speed_limit:
            for ix in range(i, index_arr[f_win][ind] + 1):
                drf_speed[ix] = 1
            i += 1
            time_to_end = hrs[-1] - hrs[i]
        else:
            i += 1
            time_to_end = hrs[-1] - hrs[i]

    df["drf_speed"] = drf_speed

    return df


def filter_unsuitable_backgrounds(
    df,
    background_err_lim=0.3,
):
    """Test and filter out obs with unsuitable background matches."""
    reps_ind = []
    sst_anom = []
    bgvar = []
    bgvar_is_masked = False

    nreps = len(df)

    for ind in range(nreps):
        row = df.iloc[ind]
        try:
            bg_val = row.OSTIA  # raises assertion error if not found
            ice_val = row.ICE  # raises assertion error if not found
            bgvar_val = row.BGVAR  # raises assertion error if not found
        except AssertionError as error:
            raise AssertionError("matched report value is missing: " + str(error))

        if ice_val is None:
            ice_val = 0.0
        assert (
            ice_val is not None and 0.0 <= ice_val <= 1.0
        ), "matched ice proportion is invalid"

        try:
            daytime = track_day_test(
                row.date.year,
                row.date.month,
                row.date.day,
                row.date.hour,
                row.lat,
                row.lon,
                -2.5,
            )
        except AssertionError as error:
            raise AssertionError("problem with report value: " + str(error))

        if ind > 0:
            try:
                time_diff = (
                    row.time_diff
                )  # raises assertion error if 'time_diff' not found
                assert time_diff >= 0, "times are not sorted"
            except AssertionError as error:
                raise AssertionError("problem with report value: " + str(error))

        land_match = True if bg_val is None else False
        ice_match = True if ice_val > 0.15 else False
        bgvar_mask = (
            True if bgvar_val is not None and bgvar_val > background_err_lim else False
        )
        if bgvar_mask:
            bgvar_is_masked = True
        if daytime or land_match or ice_match or bgvar_mask:
            pass
        else:
            assert (
                bg_val is not None and -5.0 <= bg_val <= 45.0
            ), "matched background sst is invalid"
            assert (
                bgvar_val is not None and 0.0 <= bgvar_val <= 10
            ), "matched background error variance is invalid"
            reps_ind.append(ind)
            sst_anom.append(row.sst - bg_val)
            bgvar.append(bgvar_val)

    reps_ind = np.array(reps_ind)
    sst_anom = np.array(sst_anom)
    bgerr = np.sqrt(np.array(bgvar))
    return sst_anom, bgerr, bgvar_is_masked, reps_ind


def long_tail_check(
    nrep,
    sst_anom=np.array([np.nan]),
    bgerr=np.array([np.nan]),
    drif_inter=0.29,
    drif_intra=1.00,
    long_win_len=1,
    long_err_std_n=1,
    background_err_lim=0.3,
):
    """Do long tail check."""
    start_tail_ind = -1  # keeps track of index where start tail stops
    end_tail_ind = nrep  # keeps track of index where end tail starts
    mid_win_ind = (long_win_len - 1) / 2

    if nrep >= long_win_len:
        for forward in [True, False]:  # run forwards then backwards over timeseries
            if forward:
                sst_anom_temp = sst_anom
                bgerr_temp = bgerr
            else:
                sst_anom_temp = np.flipud(sst_anom)
                bgerr_temp = np.flipud(bgerr)
            # this is the long tail check
            for ix in range(0, nrep - long_win_len + 1):
                sst_anom_winvals = sst_anom_temp[ix : ix + long_win_len]
                bgerr_winvals = bgerr_temp[ix : ix + long_win_len]
                if np.any(bgerr_winvals > np.sqrt(background_err_lim)):
                    break
                sst_anom_avg = trim_mean(sst_anom_winvals, 100)
                sst_anom_stdev = trim_std(sst_anom_winvals, 100)
                bgerr_avg = np.mean(bgerr_winvals)
                bgerr_rms = np.sqrt(np.mean(bgerr_winvals**2))
                if (
                    abs(sst_anom_avg)
                    > long_err_std_n * np.sqrt(drif_inter**2 + bgerr_avg**2)
                ) or (sst_anom_stdev > np.sqrt(drif_intra**2 + bgerr_rms**2)):
                    if forward:
                        start_tail_ind = ix + mid_win_ind
                    else:
                        end_tail_ind = (nrep - 1) - ix - mid_win_ind
                else:
                    break

    return start_tail_ind, end_tail_ind


def short_tail_check(
    start_tail_ind,
    end_tail_ind,
    sst_anom=np.array([np.nan]),
    bgerr=np.array([np.nan]),
    drif_inter=0.29,
    drif_intra=1.00,
    short_win_len=1,
    short_err_std_n=3.0,
    short_win_n_bad=1,
    background_err_lim=0.3,
):
    """Do short tail check."""
    # do short tail check on records that pass long tail check
    if start_tail_ind < end_tail_ind:  # whole record already failed long tail check
        first_pass_ind = start_tail_ind + 1  # first index passing long tail check
        last_pass_ind = end_tail_ind - 1  # last index passing long tail check
        npass = last_pass_ind - first_pass_ind + 1
        assert npass > 0, "short tail check: npass not > 0"

        if npass >= short_win_len:
            for forward in [True, False]:  # run forwards then backwards over timeseries
                if forward:
                    sst_anom_temp = sst_anom[first_pass_ind : last_pass_ind + 1]
                    bgerr_temp = bgerr[first_pass_ind : last_pass_ind + 1]
                else:
                    sst_anom_temp = np.flipud(
                        sst_anom[first_pass_ind : last_pass_ind + 1]
                    )
                    bgerr_temp = np.flipud(bgerr[first_pass_ind : last_pass_ind + 1])
                # this is the short tail check
                for ix in range(0, npass - short_win_len + 1):
                    sst_anom_winvals = sst_anom_temp[ix : ix + short_win_len]
                    bgerr_winvals = bgerr_temp[ix : ix + short_win_len]
                    if np.any(bgerr_winvals > np.sqrt(background_err_lim)):
                        break
                    limit = short_err_std_n * np.sqrt(
                        bgerr_winvals**2 + drif_inter**2 + drif_intra**2
                    )
                    exceed_limit = np.logical_or(
                        sst_anom_winvals > limit, sst_anom_winvals < -limit
                    )
                    if np.sum(exceed_limit) >= short_win_n_bad:
                        if forward:
                            if ix == (
                                npass - short_win_len
                            ):  # if all windows have failed, flag everything
                                start_tail_ind += short_win_len
                            else:
                                start_tail_ind += 1
                        else:
                            if ix == (
                                npass - short_win_len
                            ):  # if all windows have failed, flag everything
                                end_tail_ind -= short_win_len
                            else:
                                end_tail_ind -= 1
                    else:
                        break

    return start_tail_ind, end_tail_ind


def aground_check(df, smooth_win=41, min_win_period=8, max_win_period=10):
    """
    Check to see whether a drifter has run aground based on 1/100th degree precision positions.
    A flag 'drf_agr' is set for each input report: flag=1 for reports deemed aground, else flag=0.

    Positional errors introduced by lon/lat 'jitter' and data precision can be of order several km's.
    Longitude and latitude timeseries are smoothed prior to assessment to reduce position 'jitter'.
    Some post-smoothing position 'jitter' may remain and its expected magnitude is set within the
    function by the 'tolerance' parameter. A drifter is deemed aground when, after a period of time,
    the distance between reports is less than the 'tolerance'. The minimum period of time over which this
    assessment is made is set by 'min_win_period'. This period must be long enough such that slow moving
    drifters are not falsely flagged as aground given errors in position (e.g. a buoy drifting at around
    1 cm/s will travel around 1 km/day; given 'tolerance' and precision errors of a few km's the 'min_win_period'
    needs to be several days to ensure distance-travelled exceeds the error so that motion is reliably
    detected and the buoy is not falsely flagged as aground). However, min_win_period should not be longer
    than necessary as buoys that run aground for less than min_win_period will not be detected.

    Because temporal sampling can be erratic the time period over which an assessment is made is specified
    as a range (bound by 'min_win_period' and 'max_win_period') - assessment uses the longest time separation
    available within this range. If a drifter is deemed aground and subsequently starts moving (e.g. if a drifter
    has moved very slowly for a prolonged period) incorrectly flagged reports will be reinstated.

    :param df: a time-sorted list of drifter observations in format class`.Voyage`,
      each report must have a valid longitude, latitude and time-difference
    :param smooth_win: length of window (odd number) in datapoints used for smoothing lon/lat
    :param min_win_period: minimum period of time in days over which position is assessed for no movement (see description)
    :param max_win_period: maximum period of time in days over which position is assessed for no movement (this should be
      greater than min_win_period and allow for erratic temporal sampling e.g. min_win_period+2 to allow for gaps of up to 2-days in sampling).
    :type reps: a class`.Voyage`
    :type smooth_win: integer
    :type min_win_period: integer
    :type max_win_period: integer, optional
    """
    try:
        smooth_win, min_win_period, max_win_period = assert_window_and_periods(
            smooth_win=smooth_win,
            min_win_period=min_win_period,
            max_win_period=max_win_period,
        )
    except AssertionError as error:
        raise AssertionError("invalid input parameter: " + str(error))

    half_win = int((smooth_win - 1) / 2)

    nrep = len(df)
    if nrep <= smooth_win:  # records shorter than smoothing-window can't be evaluated
        print("Voyage too short for QC, setting flags to pass")
        df["drf_agr"] = np.zeros(nrep)
        return df

    try:
        lon, lat, hrs = retrieve_lon_lat_hrs(df)
    except AssertionError as error:
        raise AssertionError("problem with report values: " + str(error))

    try:
        lon_smooth, lat_smooth, hrs_smooth = create_smoothed_lon_lat_hrs(
            lon=lon,
            lat=lat,
            hrs=hrs,
            nrep=nrep,
            smooth_win=smooth_win,
            half_win=half_win,
        )
    except AssertionError as error:
        raise AssertionError("problem with smoothed report values: " + str(error))

    is_aground, i_aground = check_drifter_aground(
        lon_smooth=lon_smooth,
        lat_smooth=lat_smooth,
        hrs_smooth=hrs_smooth,
        min_win_period=min_win_period,
        max_win_period=max_win_period,
    )

    drf_agr = np.zeros(nrep)  # type: np.ndarray

    if is_aground:
        if i_aground > 0:
            i_aground += half_win
        # this gets the first index the drifter is deemed aground for the original (un-smoothed) timeseries
        # n.b. if i_aground=0 then the entire drifter record is deemed aground and flagged as such
    for ind in range(nrep):
        if is_aground:
            if ind < i_aground:
                drf_agr[ind] = 0  # rep.set_qc("POS", "drf_agr", 0)
            else:
                drf_agr[ind] = 1  # rep.set_qc("POS", "drf_agr", 1)
        else:
            drf_agr[ind] = 0  # rep.set_qc("POS", "drf_agr", 0)

    df["drf_agr"] = drf_agr

    return df
