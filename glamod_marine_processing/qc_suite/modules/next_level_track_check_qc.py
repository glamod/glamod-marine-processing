"""Module containing QC functions for track checking which could be applied on a DataBundle."""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

import numpy as np
import pandas as pd

from . import spherical_geometry as sg
from . import time_control as time_control
from . import track_check as tc
from .auxiliary import inspect_arrays, isvalid
from .qc import failed, passed

km_to_nm = 0.539957


@inspect_arrays(["value", "lat", "lon", "date"])
def do_spike_check(
    value: Sequence[float],
    lat: Sequence[float],
    lon: Sequence[float],
    date: Sequence[datetime],
    max_gradient_space: float = 0.5,
    max_gradient_time: float = 1.0,
    delta_t: float = 2.0,
    n_neighbours: int = 5,
) -> Sequence[int]:
    """Perform IQUAM like spike check.

    Parameters
    ----------
    value: array-like of float, shape (n,)
        1-dimensional value array.
    lat: array-like of float, shape (n,)
        1-dimensional latitude array in degrees.
    lon: array-like of float, shape (n,)
        1-dimensional longitude array in degrees.
    date: array-like of datetime, shape (n,)
        1-dimensional date array.
    max_gradient_space: float, default: 0.5
        Maximum gradient in space.
        The units is 'units of value' per kilometer.
    max_gradient_time: float, default: 1.0
        Maximum gradient in time.
        The units is 'units of value' per hour.
    delta_t: float, default 2.0
        Temperature delta.
        This should be 2.0 for ships and 1.0 for drifting buoys.
    n_neighbours: int, default: 5
        Number of neighbours.

    Returns
    -------
    array-like of int, shape (n,)
        1- dimensional array containing QC flags.
        1 if spike check fails, 0 otherwise.

    Raises
    ------
    ValueError
        If either input is not 1-dimensional or if their lengths do not match.
    """
    gradient_violations = []
    count_gradient_violations = []

    number_of_obs = len(value)

    spike_qc = np.asarray([passed] * number_of_obs)

    for t1 in range(number_of_obs):

        violations_for_this_report = []
        count_violations_this_report = 0.0

        lo = max(0, t1 - n_neighbours)
        hi = min(number_of_obs, t1 + n_neighbours + 1)

        for t2 in range(lo, hi):

            if not isvalid(value[t1]) or not isvalid(value[t2]):
                continue

            distance = sg.sphere_distance(lat[t1], lon[t1], lat[t2], lon[t2])
            delta = pd.Timestamp(date[t2]) - pd.Timestamp(date[t2])
            time_diff = abs(delta.days * 24 + delta.seconds / 3600.0)
            val_change = abs(value[t2] - value[t1])

            iquam_condition = max(
                [
                    delta_t,
                    abs(distance) * max_gradient_space,
                    abs(time_diff) * max_gradient_time,
                ]
            )

            if val_change > iquam_condition:
                violations_for_this_report.append(t2)
                count_violations_this_report += 1.0

        gradient_violations.append(violations_for_this_report)
        count_gradient_violations.append(count_violations_this_report)

    while np.sum(count_gradient_violations) > 0.0:
        most_fails = int(np.argmax(count_gradient_violations))
        spike_qc[most_fails] = failed

        for index in gradient_violations[most_fails]:
            if most_fails in gradient_violations[index]:
                gradient_violations[index].remove(most_fails)
                count_gradient_violations[index] -= 1.0

        count_gradient_violations[most_fails] = 0

    return spike_qc


def calculate_course_parameters(
    lat_later: float,
    lat_earlier: float,
    lon_later: float,
    lon_earlier: float,
    date_later: datetime,
    date_earlier: datetime,
) -> tuple[float, float, float, float]:
    """Calculate course parameters.

    Parameters
    ----------
    lat_later: float
        Latitude in degrees of later timestamp.
    lat_earlier:float
        Latitude in degrees of earlier timestamp.
    lon_later: float
        Longitude in degrees of later timestamp.
    lon_earlier: float
        Longitude in degrees of earlier timestamp.
    date_later: datetime
        Date of later timestamp.
    date_earlier: datetime
        Date of earlier timestamp.

    Returns
    -------
    tuple of float
        A tuple of four floats representing the speed, distance, course and time difference
    """
    distance = sg.sphere_distance(lat_later, lon_later, lat_earlier, lon_earlier)
    date_earlier = pd.Timestamp(date_earlier)
    date_later = pd.Timestamp(date_later)

    timediff = time_control.time_difference(
        date_earlier.year,
        date_earlier.month,
        date_earlier.day,
        date_earlier.hour,
        date_later.year,
        date_later.month,
        date_later.day,
        date_later.hour,
    )
    if timediff != 0 and isvalid(timediff):
        speed = distance / abs(timediff)
    else:
        timediff = 0.0
        speed = distance

    course = sg.course_between_points(lat_earlier, lon_earlier, lat_later, lon_later)

    return speed, distance, course, timediff


@inspect_arrays(["lat", "lon", "date"])
def calculate_speed_course_distance_time_difference(
    lat: Sequence[float],
    lon: Sequence[float],
    date: Sequence[datetime],
    alternating: bool = False,
) -> tuple[Sequence[float], Sequence[float], Sequence[float], Sequence[float]]:
    """
    Calculates speeds, courses, distances and time differences using consecutive reports.

    Parameters
    ----------
    lat: array-like of float, shape (n,)
        1-dimensional latitude array in degrees.
    lon: array-like of float, shape (n,)
        1-dimensional longitude array in degrees.
    date: array-like of datetime, shape (n,)
        1-dimensional date array.
    alternating: bool, default: False
        Use alternating reports for calculation

    Returns
    -------
    tuple of array-like of float, shape (n,)
        A tuple of four 1-dimensional arrays of floats representing speed, distance, course and time difference.

    Raises
    ------
    ValueError
        If either input is not 1-dimensional or if their lengths do not match.
    """
    number_of_obs = len(lat)

    speed = np.empty(number_of_obs)  # type: np.ndarray
    course = np.empty(number_of_obs)  # type: np.ndarray
    distance = np.empty(number_of_obs)  # type: np.ndarray
    timediff = np.empty(number_of_obs)  # type: np.ndarray

    speed.fill(np.nan)
    course.fill(np.nan)
    distance.fill(np.nan)
    timediff.fill(np.nan)

    if number_of_obs == 1:
        return speed, distance, course, timediff

    range_end = number_of_obs
    first_entry = "i"
    second_entry = "i - 1"
    if alternating is True:
        range_end = number_of_obs - 1
        first_entry = "i + 1"
        second_entry = "i - 1"

    for i in range(1, range_end):
        fe = eval(first_entry)  # noqa
        se = eval(second_entry)  # noqa
        ship_speed, ship_distance, ship_direction, ship_time_difference = (
            calculate_course_parameters(
                lat[fe], lat[se], lon[fe], lon[se], date[fe], date[se]
            )
        )

        speed[i] = ship_speed
        course[i] = ship_direction
        distance[i] = ship_distance
        timediff[i] = ship_time_difference

    return speed, distance, course, timediff


@inspect_arrays(["vsi", "dsi", "lat", "lon", "date"])
def forward_discrepancy(
    vsi: Sequence[float],
    dsi: Sequence[float],
    lat: Sequence[float],
    lon: Sequence[float],
    date: Sequence[datetime],
) -> Sequence[float]:
    """Calculate what the distance is between the projected position (based on the reported
    speed and heading at the current and previous time steps) and the actual position. The
    observations are taken in time order.

    This takes the speed and direction reported by the ship and projects it forwards half a
    time step, it then projects it forwards another half time-step using the speed and
    direction for the next report, to which the projected location
    is then compared. The distances between the projected and actual locations is returned

    Parameters
    ----------
    vsi: array-like of float, shape (n,)
        1-dimensional reported speed array in knots.
    dsi: array-like of float, shape (n,)
        1-dimensional reported heading array.
    lat: array-like of float, shape (n,)
        1-dimensional latitude array in degrees.
    lon: array-like of float, shape (n,)
        1-dimensional longitude array in degrees.
    date: array-like of datetime, shape (n,)
        1-dimensional date array.

    Returns
    -------
    array-like of float, shape (n,)
        1-dimensional array containing distances from estimated positions.

    Raises
    ------
    ValueError
        If either input is not 1-dimensional or if their lengths do not match.
    """
    number_of_obs = len(lat)

    distance_from_est_location = np.asarray([np.nan] * number_of_obs)

    for i in range(1, number_of_obs):

        vsi_current = vsi[i]
        vsi_previous = vsi[i - 1]
        dsi_current = dsi[i]
        dsi_previous = dsi[i - 1]
        tsi_current = pd.Timestamp(date[i])
        tsi_previous = pd.Timestamp(date[i - 1])
        lat_current = lat[i]
        lat_previous = lat[i - 1]
        lon_current = lon[i]
        lon_previous = lon[i - 1]

        if (
            not isvalid(vsi_current)
            or not isvalid(vsi_previous)
            or not isvalid(dsi_current)
            or not isvalid(dsi_previous)
            or not isvalid(tsi_current)
            or not isvalid(tsi_previous)
            or not isvalid(lat_current)
            or not isvalid(lat_previous)
            or not isvalid(lon_current)
            or not isvalid(lon_previous)
        ):
            continue

        timediff = (tsi_current - tsi_previous).total_seconds() / 3600
        # get increment from initial position
        lat1, lon1 = tc.increment_position(
            lat_previous,
            lon_previous,
            vsi_previous,
            dsi_current,
            timediff,
        )

        lat2, lon2 = tc.increment_position(
            lat_current,
            lon_current,
            vsi_current,
            dsi_current,
            timediff,
        )

        # apply increments to the lat and lon at i-1
        updated_latitude = lat_previous + lat1 + lat2
        updated_longitude = lon_previous + lon1 + lon2

        # calculate distance between calculated position and the second reported position
        discrepancy = sg.sphere_distance(
            lat_current, lon_current, updated_latitude, updated_longitude
        )

        distance_from_est_location[i] = discrepancy

    return distance_from_est_location


@inspect_arrays(["vsi", "dsi", "lat", "lon", "date"])
def backward_discrepancy(
    lat: Sequence[float],
    lon: Sequence[float],
    date: Sequence[datetime],
    vsi: Sequence[float],
    dsi: Sequence[float],
) -> Sequence[float]:
    """Calculate what the distance is between the projected position (based on the reported speed and
    heading at the current and previous time steps) and the actual position. The calculation proceeds from the
    final, later observation to the first (in contrast to distr1 which runs in time order)

    This takes the speed and direction reported by the ship and projects it forwards half a time step, it then
    projects it forwards another half time step using the speed and direction for the next report, to which the
    projected location is then compared. The distances between the projected and actual locations is returned

    Parameters
    ----------
    vsi: array-like of float, shape (n,)
        1-dimensional reported speed array in knots.
    dsi: array-like of float, shape (n,)
        1-dimensional reported heading array.
    lat: array-like of float, shape (n,)
        1-dimensional latitude array in degrees.
    lon: array-like of float, shape (n,)
        1-dimensional longitude array in degrees.
    date: array-like of datetime, shape (n,)
        1-dimensional date array.

    Returns
    -------
    array-like of float, shape (n,)
        1-dimensional array containing distances from estimated positions.

    Raises
    ------
    ValueError
        If either input is not 1-dimensional or if their lengths do not match.
    """
    number_of_obs = len(lat)

    distance_from_est_location = np.asarray([np.nan] * number_of_obs)

    for i in range(number_of_obs - 1, 0, -1):

        vsi_current = vsi[i]
        vsi_previous = vsi[i - 1]
        dsi_current = dsi[i]
        dsi_previous = dsi[i - 1]
        tsi_current = pd.Timestamp(date[i])
        tsi_previous = pd.Timestamp(date[i - 1])
        lat_current = lat[i]
        lat_previous = lat[i - 1]
        lon_current = lon[i]
        lon_previous = lon[i - 1]

        if (
            not isvalid(vsi_current)
            or not isvalid(vsi_previous)
            or not isvalid(dsi_current)
            or not isvalid(dsi_previous)
            or not isvalid(tsi_current)
            or not isvalid(tsi_previous)
            or not isvalid(lat_current)
            or not isvalid(lat_previous)
            or not isvalid(lon_current)
            or not isvalid(lon_previous)
        ):
            continue

        timediff = (tsi_current - tsi_previous).total_seconds() / 3600
        # get increment from initial position - backwards in time
        # means reversing the direction by 180 degrees
        lat1, lon1 = tc.increment_position(
            lat_current,
            lon_current,
            vsi_current,
            dsi_current,
            timediff,
        )

        lat2, lon2 = tc.increment_position(
            lat_previous,
            lon_previous,
            vsi_previous,
            dsi_previous,
            timediff,
        )

        # apply increments to the lat and lon at i-1
        updated_latitude = lat_current + lat1 + lat2
        updated_longitude = lon_previous + lon1 + lon2

        # calculate distance between calculated position and the second reported position
        discrepancy = sg.sphere_distance(
            lat_previous, lon_previous, updated_latitude, updated_longitude
        )
        distance_from_est_location[i] = discrepancy

    # that fancy bit at the end reverses the array
    return distance_from_est_location[::-1]


@inspect_arrays(["lat", "lon", "timediff"])
def calculate_midpoint(
    lat: Sequence[float],
    lon: Sequence[float],
    timediff: Sequence[pd.Timestamp],
) -> Sequence[float]:
    """Interpolate between alternate reports and compare the interpolated location to the actual location. e.g.
    take difference between reports 2 and 4 and interpolate to get an estimate for the position at the time
    of report 3. Then compare the estimated and actual positions at the time of report 3.

    The calculation linearly interpolates the latitudes and longitudes (allowing for wrapping around the
    dateline and so on).

    Parameters
    ----------
    lat: array-like of float, shape (n,)
        1-dimensional latitude array in degrees.
    lon: array-like of float, shape (n,)
        1-dimensional longitude array in degrees.
    timediff: array-like of datetime, shape (n,)
        1-dimensional time difference array.

    Returns
    -------
    array-like of float, shape (n,)
        1-dimensional array containing distances from estimated positions in km

    Raises
    ------
    ValueError
        If either input is not 1-dimensional or if their lengths do not match.
    """
    number_of_obs = len(lat)

    midpoint_discrepancies = np.asarray([np.nan] * number_of_obs)

    for i in range(1, number_of_obs - 1):
        t0 = timediff[i]
        t1 = timediff[i + 1]

        if t0 is not None and t1 is not None:
            if t0 + t1 != 0:
                fraction_of_time_diff = t0 / (t0 + t1)
            else:
                fraction_of_time_diff = 0.0
        else:
            fraction_of_time_diff = 0.0

        estimated_lat_at_midpoint, estimated_lon_at_midpoint = sg.intermediate_point(
            lat[i - 1],
            lon[i - 1],
            lat[i + 1],
            lon[i + 1],
            fraction_of_time_diff,
        )

        discrepancy = sg.sphere_distance(
            lat[i],
            lon[i],
            estimated_lat_at_midpoint,
            estimated_lon_at_midpoint,
        )

        midpoint_discrepancies[i] = discrepancy

    midpoint_discrepancies[i + 1] = np.nan

    return midpoint_discrepancies


@inspect_arrays(["vsi", "dsi", "lat", "lon", "date"])
def do_track_check(
    vsi: Sequence[float],
    dsi: Sequence[float],
    lat: Sequence[float],
    lon: Sequence[float],
    date: Sequence[datetime],
    max_direction_change: float = 60.0,
    max_speed_change: float = 10.0,
    max_absolute_speed: float = 40.0,
    max_midpoint_discrepancy: float = 150.0,
) -> Sequence[int]:
    """Perform one pass of the track check.  This is an implementation of the MDS track check code
    which was originally written in the 1990s. I don't know why this piece of historic trivia so exercises
    my mind, but it does: the 1990s! I wish my code would last so long.

    Parameters
    ----------
    vsi: array-like of float, shape (n,)
        1-dimensional reported speed array in knots.
    dsi: array-like of float, shape (n,)
        1-dimensional reported heading array.
    lat: array-like of float, shape (n,)
        1-dimensional latitude array in degrees.
    lon: array-like of float, shape (n,)
        1-dimensional longitude array in degrees.
    date: array-like of datetime, shape (n,)
        1-dimensional date array.
    max_direction_change: float, default: 60.0
        Maximum valid direction change in ???.
    max_speed_change: float, default: 10.0
        Maximum valid speed change in ???.
    max_absolute_speed: float, default: 40.0
        Maximum valid absolute speed in ???.
    max_midpoint_discrepancy: float, default: 150.0
        Maximum valid midpoint discrepancy in ???.

    Returns
    -------
    array-like of int, shape (n,)
        1-dimensional arrays of ints representing track check QC flags.
        1 if track check fails, 0 otherwise.

    Raises
    ------
    ValueError
        If either input is not 1-dimensional or if their lengths do not match.

    Note
    ----
    If number of observations is less than three, the track check always passes.
    """
    number_of_obs = len(lat)

    # no obs in, no qc outcomes out
    if number_of_obs == 0:
        return

    # fewer than three obs - set the fewsome flag
    if number_of_obs < 3:
        return np.asarray([passed] * number_of_obs)

    # work out speeds and distances between alternating points
    speed_alt, _distance_alt, _course_alt, _timediff_alt = (
        calculate_speed_course_distance_time_difference(
            lat=lat,
            lon=lon,
            date=date,
            alternating=True,
        )
    )
    speed, _distance, course, timediff = (
        calculate_speed_course_distance_time_difference(
            lat=lat,
            lon=lon,
            date=date,
        )
    )

    # what are the mean and mode speeds?
    modal_speed = tc.modesp(speed)

    # set speed limits based on modal speed
    amax, _amaxx, _amin = tc.set_speed_limits(modal_speed)

    # compare reported speeds and positions if we have them
    forward_diff_from_estimated = forward_discrepancy(
        lat=lat,
        lon=lon,
        date=date,
        vsi=vsi,
        dsi=dsi,
    )
    reverse_diff_from_estimated = backward_discrepancy(
        lat=lat,
        lon=lon,
        date=date,
        vsi=vsi,
        dsi=dsi,
    )

    midpoint_diff_from_estimated = calculate_midpoint(
        lat=lat,
        lon=lon,
        timediff=timediff,
    )

    # do QC
    trk = np.asarray([passed] * number_of_obs)

    for i in range(1, number_of_obs - 1):
        thisqc_a = 0
        thisqc_b = 0

        # together these cover the speeds calculate from point i
        if (
            isvalid(speed[i])
            and speed[i] > amax
            and isvalid(speed_alt[i - 1])
            and speed_alt[i - 1] > amax
        ):
            thisqc_a += 1.00
        elif (
            isvalid(speed[i + 1])
            and speed[i + 1] > amax
            and isvalid(speed_alt[i + 1])
            and speed_alt[i + 1] > amax
        ):
            thisqc_a += 2.00
        elif (
            isvalid(speed[i])
            and speed[i] > amax
            and isvalid(speed[i + 1])
            and speed[i + 1] > amax
        ):
            thisqc_a += 3.00

        # Quality-control by examining the distance
        # between the calculated and reported second position.
        thisqc_b += tc.check_distance_from_estimate(
            vsi[i],
            vsi[i - 1],
            timediff[i],
            forward_diff_from_estimated[i],
            reverse_diff_from_estimated[i],
        )
        # Check for continuity of direction
        thisqc_b += tc.direction_continuity(
            dsi[i],
            dsi[i - 1],
            course[i],
            max_direction_change,
        )
        # Check for continuity of speed.
        thisqc_b += tc.speed_continuity(
            vsi[i],
            vsi[i - 1],
            speed[i],
            max_speed_change,
        )

        # check for speeds in excess of 40.00 knots
        if speed[i] > max_absolute_speed / km_to_nm:
            thisqc_b += 10.0

        # make the final decision
        if (
            midpoint_diff_from_estimated[i] > max_midpoint_discrepancy / km_to_nm
            and thisqc_a > 0
            and thisqc_b > 0
        ):
            trk[i] = failed

    return trk


@inspect_arrays(["value"])
def do_few_check(
    value: Sequence[float],
) -> Sequence[int]:
    """Checks if number of observations is less than 3.

    Parameters
    ----------
    value: array-like of float, shape (n,)
        1-dimensional value array.

    Returns
    -------
    array-like of int, shape (n,)
        A 1-dimensional arrays of ints containing QC flags.
        1 if number of observations is less than 3, 0 otherwise.

    Raises
    ------
    ValueError
        If either input is not 1-dimensional.
    """
    number_of_obs = len(value)

    # no obs in, no qc outcomes out
    if number_of_obs == 0:
        return

    # fewer than three obs - set the fewsome flag
    if number_of_obs < 3:
        return np.asarray([failed] * number_of_obs)

    return np.asarray([passed] * number_of_obs)


@inspect_arrays(["at", "dpt", "lat", "lon", "date"])
def find_saturated_runs(
    at: Sequence[float],
    dpt: Sequence[float],
    lat: Sequence[float],
    lon: Sequence[float],
    date: Sequence[datetime],
    min_time_threshold: float = 48.0,
    shortest_run: int = 4,
) -> Sequence[int]:
    """Perform checks on persistence of 100% rh while going through the voyage.
    While going through the voyage repeated strings of 100 %rh (AT == DPT) are noted.
    If a string extends beyond 20 reports and two days/48 hrs in time then all values are set to
    fail the repsat qc flag.

    Parameters
    ----------
    at: array-like of float, shape (n,)
        1-dimensional air temperature array.
    dpt: array-like of float, shape (n,)
        1-dimensional dew point temperature array in.
    lat: array-like of float, shape (n,)
        1-dimensional latitude array in degrees.
    lon: array-like of float, shape (n,)
        1-dimensional longitude array in degrees.
    date: array-like of datetime, shape (n,)
        1-dimensional date array.
    min_time_threshold: float, default: 48,0
        Minimum time thresholf in hours.
    shortest_run: int, default: 4
        Shortest number of observations.

    Returns
    -------
    array-like of int, shape (n,)
        1-dimensional array containing repsat QC flags.
        1 if saturated run found, 0 otherwise.

    Raises
    ------
    ValueError
        If either input is not 1-dimensional or if their lengths do not match.
    """
    satcount = []

    repsat = np.asarray([passed] * len(lat))

    for i in range(len(repsat)):

        saturated = dpt[i] == at[i]

        if saturated:
            satcount.append(i)
        elif not saturated and len(satcount) > shortest_run:
            later = satcount[len(satcount) - 1]
            earlier = satcount[0]
            _, _, _, tdiff = calculate_course_parameters(
                lat_later=lat[later],
                lat_earlier=lat[earlier],
                lon_later=lon[later],
                lon_earlier=lon[earlier],
                date_later=date[later],
                date_earlier=date[earlier],
            )

            if tdiff >= min_time_threshold:
                for loc in satcount:
                    repsat[loc] = failed
                satcount = []
            else:
                satcount = []

        else:
            satcount = []

    if len(satcount) > shortest_run:
        later = satcount[len(satcount) - 1]
        earlier = satcount[0]
        _, _, _, tdiff = calculate_course_parameters(
            lat_later=lat[later],
            lat_earlier=lat[earlier],
            lon_later=lon[later],
            lon_earlier=lon[earlier],
            date_later=date[later],
            date_earlier=date[earlier],
        )

        if tdiff >= min_time_threshold:
            for loc in satcount:
                repsat[loc] = failed

    return repsat


@inspect_arrays(["value"])
def find_multiple_rounded_values(
    value: Sequence[float], min_count: int = 20, threshold: float = 0.5
) -> Sequence[int]:
    """Find instances when more than "threshold" of the observations are
    whole numbers and set the 'round' flag. Used in the humidity QC
    where there are times when the values are rounded and this may
    have caused a bias.

    Parameters
    ----------
    value: array-like of float, shape (n,)
        1-dimensional array.
    min_count: int, default: 20
        ???
    threshold: float, default: 0.5
        ???

    Returns
    -------
    array-like of int, shape (n,)
        1-dimensional array containing rounded QC flag.
        1 if value is whole number, otherwise 0.
    """
    assert 0.0 <= threshold <= 1.0

    number_of_obs = len(value)
    rounded = np.asarray([passed] * number_of_obs)

    valcount = {}
    allcount = 0

    for i in range(number_of_obs):
        v = value[i]
        if isvalid(v):
            allcount += 1
            if str(v) in valcount:
                valcount[str(v)].append(i)
            else:
                valcount[str(v)] = [i]

    if allcount > min_count:
        wholenums = 0
        for key in valcount:
            if float(key).is_integer():
                wholenums = wholenums + len(valcount[key])

        if float(wholenums) / float(allcount) >= threshold:
            for key in valcount:
                if float(key).is_integer():
                    for i in valcount[key]:
                        rounded[i] = failed

    return rounded


@inspect_arrays(["value"])
def find_repeated_values(
    value: Sequence[float], min_count: int = 20, threshold: float = 0.7
) -> pd.DataFrame:
    """Find cases where more than a given proportion of SSTs have the same value

    This function goes through a voyage and finds any cases where more than a threshold fraction of
    the observations have the same values for a specified variable.


    Parameters
    ----------
    value: array-like of float, shape (n,)
        1-dimensional array.
    min_count: int, default: 20
        ???
    threshold: float, default: 0.7
        ???

    Returns
    -------
    array-like of int, shape (n,)
        1-dimensional array containing repeated QC flag.
        1 if value is repeated, otherwise 0.
    """
    assert 0.0 <= threshold <= 1.0

    number_of_obs = len(value)
    rep = np.asarray([passed] * number_of_obs)

    valcount = {}
    allcount = 0

    for i in range(number_of_obs):
        v = value[i]
        if isvalid(v):
            allcount += 1
            if str(v) in valcount:
                valcount[str(v)].append(i)
            else:
                valcount[str(v)] = [i]

    if allcount > min_count:
        for key in valcount:
            if float(len(valcount[key])) / float(allcount) > threshold:
                for i in valcount[key]:
                    rep[i] = 1

    return rep


@inspect_arrays(["lat", "lon", "date"])
def do_iquam_track_check(
    lat: Sequence[float],
    lon: Sequence[float],
    date: Sequence[datetime],
    speed_limit: float = 60.0,
    delta_d: float = 1.11,
    delta_t: float = 0.01,
    n_neighbours: int = 5,
) -> Sequence[int]:
    """Perform the IQUAM track check as detailed in Xu and Ignatov 2013

    The track check calculates speeds between pairs of observations and
    counts how many exceed a threshold speed. The ob with the most
    violations of this limit is flagged as bad and removed from the
    calculation. Then the next worst is found and removed until no
    violatios remain.

    Parameters
    ----------
    lat: array-like of float, shape (n,)
        1-dimensional latitude array in degrees.
    lon: array-like of float, shape (n,)
        1-dimensional longitude array in degrees.
    date: array-like of datetime, shape (n,)
        1-dimensional date array.
    speed_limit: float, default: 60.0
        Speed limit of platform in km/h.
        This should be 60.0 for ships and 15.0 for drifting buoys.
    delta_d: float, default: 1.11
        ??? degrees of latitude
    delta_t: float, default: 0.01
        ??? one hundredth of an hour
    n_neighbours: int, default: 5
        Number of neighbours.

    Returns
    -------
    array-like of int, shape (n,)
        1-dimensional array containing IQUAM QC flags.
        1 if IQUAM QC failed, 0 otherwise.

    Raises
    ------
    ValueError
        If either input is not 1-dimensional or if their lengths do not match.
    """
    number_of_obs = len(lat)

    if number_of_obs == 0:
        return

    speed_violations = []
    count_speed_violations = []

    iquam_track = np.asarray([passed] * number_of_obs)

    for t1 in range(0, number_of_obs):
        violations_for_this_report = []
        count_violations_this_report = 0.0

        lo = max(0, t1 - n_neighbours)
        hi = min(number_of_obs, t1 + n_neighbours + 1)

        for t2 in range(lo, hi):

            _, distance, _, timediff = calculate_course_parameters(
                lat_later=lat[t2],
                lat_earlier=lat[t1],
                lon_later=lon[t2],
                lon_earlier=lon[t1],
                date_later=date[t2],
                date_earlier=date[t1],
            )

            iquam_condition = max([abs(distance) - delta_d, 0.0]) / (
                abs(timediff) + delta_t
            )

            if iquam_condition > speed_limit:
                violations_for_this_report.append(t2)
                count_violations_this_report += 1.0

        speed_violations.append(violations_for_this_report)
        count_speed_violations.append(count_violations_this_report)

    while np.sum(count_speed_violations) > 0.0:
        most_fails = int(np.argmax(count_speed_violations))
        iquam_track[most_fails] = failed

        for index in speed_violations[most_fails]:
            if most_fails in speed_violations[index]:
                speed_violations[index].remove(most_fails)
                count_speed_violations[index] -= 1.0

        count_speed_violations[most_fails] = passed

    return iquam_track
