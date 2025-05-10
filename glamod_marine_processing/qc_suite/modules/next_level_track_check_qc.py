"""Module containing QC functions for track checking which could be applied on a DataBundle."""

from __future__ import annotations

import numpy as np
import pandas as pd

import glamod_marine_processing.qc_suite.modules.icoads_identify as icoads_identify
import glamod_marine_processing.qc_suite.modules.spherical_geometry as sg
import glamod_marine_processing.qc_suite.modules.time_control as time_control
import glamod_marine_processing.qc_suite.modules.track_check as tc

km_to_nm = 0.539957


def spike_check(df: pd.DataFrame) -> pd.DataFrame:
    """Perform IQUAM like spike check.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the data, must have columns 'sst', 'lat', 'lon', 'pt', 'date'

    Returns
    -------
    pd.DataFrame
        DataFrame as original but with 'spike' column added containing the spike check flags

    Raises
    ------
    KeyError
        Raised when one of the required columns is missing from the DataFrame
    """
    for key in ["sst", "lat", "lon", "pt", "date"]:
        if key not in df:
            raise KeyError(f"{key} not in dataframe")

    max_gradient_space = 0.5  # K/km
    max_gradient_time = 1.0  # K/hr

    ship_delta_t = 2.0  # K
    buoy_delta_t = 1.0  # K

    n_neighbours = 5

    number_of_obs = len(df)

    if df.iloc[0].pt in [6, 7]:
        delta_t = buoy_delta_t
    else:
        delta_t = ship_delta_t

    gradient_violations = []
    count_gradient_violations = []

    spike_qc = np.zeros(number_of_obs)  # type: np.ndarray

    for t1 in range(number_of_obs):

        violations_for_this_report = []
        count_violations_this_report = 0.0

        lo = max(0, t1 - n_neighbours)
        hi = min(number_of_obs, t1 + n_neighbours + 1)

        for t2 in range(lo, hi):

            row1 = df.iloc[t1]
            row2 = df.iloc[t2]

            if row1.sst is not None and row2.sst is not None:

                distance = sg.sphere_distance(row1.lat, row1.lon, row2.lat, row2.lon)
                time_diff = abs(
                    (row2.date - row1.date).days * 24
                    + (row2.date - row1.date).seconds / 3600.0
                )
                val_change = abs(row2.sst - row1.sst)

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

    count = 0
    while np.sum(count_gradient_violations) > 0.0:
        most_fails = int(np.argmax(count_gradient_violations))
        spike_qc[most_fails] = 1

        for index in gradient_violations[most_fails]:
            if most_fails in gradient_violations[index]:
                gradient_violations[index].remove(most_fails)
                count_gradient_violations[index] -= 1.0

        count_gradient_violations[most_fails] = 0
        count += 1

    df["spike"] = spike_qc

    return df


def row_difference(
    later_row: pd.DataFrame, earlier_row: pd.DataFrame
) -> (float, float, float, float):
    """Subtracting one row from another to return the speed, distance, course and the time difference between the
    two rows. Originally this was coded as a subtraction: later_row minus earlier_row.

    Parameters
    ----------
    later_row : pd.DataFrame
        The later of the two rows from a DataFrame
    earlier_row : pd.DataFrame
        The earlier of the two rows from a DataFrame

    Returns
    -------
    (float, float, float, float)
        Returns the speed, distance, course and time difference between the two rows
    """
    distance = sg.sphere_distance(
        later_row.lat, later_row.lon, earlier_row.lat, earlier_row.lon
    )

    timediff = time_control.time_difference(
        earlier_row.date.year,
        earlier_row.date.month,
        earlier_row.date.day,
        earlier_row.date.hour,
        later_row.date.year,
        later_row.date.month,
        later_row.date.day,
        later_row.date.hour,
    )
    if timediff != 0 and timediff is not None:
        speed = distance / abs(timediff)
    else:
        timediff = 0.0
        speed = distance

    course = sg.course_between_points(
        earlier_row.lat, earlier_row.lon, later_row.lat, later_row.lon
    )

    return speed, distance, course, timediff


def calculate_speed_course_distance_time_difference(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates speeds, courses, distances and time differences using consecutive reports.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame for which the speeds, courses, distances, and time differences are to be calculated.

    Returns
    -------
    pd.DataFrame
        Returns the DataFrame with additional columns "speed", "course", "distance", "time_diff"
    """
    number_of_obs = len(df)

    speed = np.empty(number_of_obs)  # type: np.ndarray
    course = np.empty(number_of_obs)  # type: np.ndarray
    distance = np.empty(number_of_obs)  # type: np.ndarray
    time_diff = np.empty(number_of_obs)  # type: np.ndarray

    speed.fill(np.nan)
    course.fill(np.nan)
    distance.fill(np.nan)
    time_diff.fill(np.nan)

    if number_of_obs > 1:
        for i in range(1, number_of_obs):
            row2 = df.iloc[i]
            row1 = df.iloc[i - 1]
            ship_speed, ship_distance, ship_direction, ship_time_difference = (
                row_difference(row2, row1)
            )

            speed[i] = ship_speed
            course[i] = ship_direction
            distance[i] = ship_distance
            time_diff[i] = ship_time_difference

    df["speed"] = speed
    df["course"] = course
    df["distance"] = distance
    df["time_diff"] = time_diff

    return df


def calc_alternate_speeds(df):
    """Calculates speeds, courses, distances and time differences using alternating reports.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame for which the speeds, courses, distances, and time differences are to be calculated.

    Returns
    -------
    pd.DataFrame
        Returns the DataFrame with additional columns "alt_speed", "alt_course", "alt_distance", "alt_time_diff"
    """
    number_of_obs = len(df)

    alt_speed = np.empty(number_of_obs)  # type: np.ndarray
    alt_course = np.empty(number_of_obs)  # type: np.ndarray
    alt_distance = np.empty(number_of_obs)  # type: np.ndarray
    alt_time_diff = np.empty(number_of_obs)  # type: np.ndarray

    alt_speed.fill(np.nan)
    alt_course.fill(np.nan)
    alt_distance.fill(np.nan)
    alt_time_diff.fill(np.nan)

    if number_of_obs > 2:
        for i in range(1, number_of_obs - 1):
            row2 = df.iloc[i + 1]
            row1 = df.iloc[i - 1]
            ship_speed, ship_distance, ship_direction, ship_time_difference = (
                row_difference(row1, row2)
            )

            alt_speed[i] = ship_speed
            alt_course[i] = ship_direction
            alt_distance[i] = ship_distance
            alt_time_diff[i] = ship_time_difference

    df["alt_speed"] = alt_speed
    df["alt_course"] = alt_course
    df["alt_distance"] = alt_distance
    df["alt_time_diff"] = alt_time_diff

    return df


def forward_discrepancy(df: pd.DataFrame) -> list:
    """Calculate what the distance is between the projected position (based on the reported
    speed and heading at the current and previous time steps) and the actual position. The
    observations are taken in time order.

    This takes the speed and direction reported by the ship and projects it forwards half a
    time step, it then projects it forwards another half time-step using the speed and
    direction for the next report, to which the projected location
    is then compared. The distances between the projected and actual locations is returned

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame for which the discrepancies are to be calculated.

    Returns
    -------
    list
        list of distances from estimated positions
    """
    nobs = len(df)

    distance_from_est_location = [None]

    for i in range(1, nobs):

        vsi = df.iloc[i].vsi
        vsi_minus_one = df.iloc[i - 1].vsi
        dsi = df.iloc[i].dsi
        dsi_minus_one = df.iloc[i - 1].dsi
        time_diff = df.iloc[i].time_diff

        if (
            vsi is not None
            and vsi_minus_one is not None
            and dsi is not None
            and dsi_minus_one is not None
            and time_diff is not None
        ):
            # get increment from initial position
            lat1, lon1 = tc.increment_position(
                df.iloc[i - 1].lat,
                df.iloc[i - 1].lon,
                df.iloc[i - 1].vsi / km_to_nm,
                df.iloc[i - 1].dsi,
                df.iloc[i].time_diff,
            )

            lat2, lon2 = tc.increment_position(
                df.iloc[i].lat,
                df.iloc[i].lon,
                df.iloc[i].vsi / km_to_nm,
                df.iloc[i].dsi,
                df.iloc[i].time_diff,
            )
            # apply increments to the lat and lon at i-1
            updated_latitude = df.iloc[i - 1].lat + lat1 + lat2
            updated_longitude = df.iloc[i - 1].lon + lon1 + lon2

            # calculate distance between calculated position and the second reported position
            discrepancy = sg.sphere_distance(
                df.iloc[i].lat, df.iloc[i].lon, updated_latitude, updated_longitude
            )

            distance_from_est_location.append(discrepancy)

        else:
            # in the absence of reported speed and direction set to None
            distance_from_est_location.append(None)

    return distance_from_est_location


def backward_discrepancy(df) -> list:
    """Calculate what the distance is between the projected position (based on the reported speed and
    heading at the current and previous time steps) and the actual position. The calculation proceeds from the
    final, later observation to the first (in contrast to distr1 which runs in time order)

    This takes the speed and direction reported by the ship and projects it forwards half a time step, it then
    projects it forwards another half time step using the speed and direction for the next report, to which the
    projected location is then compared. The distances between the projected and actual locations is returned

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame for which the discrepancies are to be calculated.

    Returns
    -------
    list
        Returns list of distances from estimated positions
    """
    nobs = len(df)

    distance_from_est_location = [None]

    for i in range(nobs - 1, 0, -1):

        vsi = df.iloc[i].vsi
        vsi_minus_one = df.iloc[i - 1].vsi
        dsi = df.iloc[i].dsi
        dsi_minus_one = df.iloc[i - 1].dsi
        time_diff = df.iloc[i].time_diff

        if (
            vsi is not None
            and vsi_minus_one is not None
            and dsi is not None
            and dsi_minus_one is not None
            and time_diff is not None
        ):
            # get increment from initial position - backwards in time
            # means reversing the direction by 180 degrees
            lat1, lon1 = tc.increment_position(
                df.iloc[i].lat,
                df.iloc[i].lon,
                df.iloc[i].vsi / km_to_nm,
                df.iloc[i].dsi - 180.0,
                df.iloc[i].time_diff,
            )

            lat2, lon2 = tc.increment_position(
                df.iloc[i - 1].lat,
                df.iloc[i - 1].lon,
                df.iloc[i - 1].vsi / km_to_nm,
                df.iloc[i - 1].dsi - 180.0,
                df.iloc[i].time_diff,
            )

            # apply increments to the lat and lon at i-1
            alatx = df.iloc[i].lat + lat1 + lat2
            alonx = df.iloc[i].lon + lon1 + lon2

            # calculate distance between calculated position and the second reported position
            discrepancy = sg.sphere_distance(
                df.iloc[i - 1].lat, df.iloc[i - 1].lon, alatx, alonx
            )
            distance_from_est_location.append(discrepancy)

        else:
            # in the absence of reported speed and direction set to None
            distance_from_est_location.append(None)

    # that fancy bit at the end reverses the array
    return distance_from_est_location[::-1]


def calculate_midpoint(df: pd.DataFrame) -> list:
    """Interpolate between alternate reports and compare the interpolated location to the actual location. e.g.
    take difference between reports 2 and 4 and interpolate to get an estimate for the position at the time
    of report 3. Then compare the estimated and actual positions at the time of report 3.

    The calculation linearly interpolates the latitudes and longitudes (allowing for wrapping around the
    dateline and so on).

    Parameters
    ----------
    df : pd.DataFrame
        Input data

    Returns
    -------
    list
        Returns list of distances from estimated positions in km
    """
    nobs = len(df)

    midpoint_discrepancies = [None]

    for i in range(1, nobs - 1):
        t0 = df.iloc[i].time_diff
        t1 = df.iloc[i + 1].time_diff

        if t0 is not None and t1 is not None:
            if t0 + t1 != 0:
                fraction_of_time_diff = t0 / (t0 + t1)
            else:
                fraction_of_time_diff = 0.0
        else:
            fraction_of_time_diff = 0.0

        if fraction_of_time_diff > 1.0:
            print(fraction_of_time_diff, t0, t1)

        estimated_lat_at_midpoint, estimated_lon_at_midpoint = sg.intermediate_point(
            df.iloc[i - 1].lat,
            df.iloc[i - 1].lon,
            df.iloc[i + 1].lat,
            df.iloc[i + 1].lon,
            fraction_of_time_diff,
        )

        discrepancy = sg.sphere_distance(
            df.iloc[i].lat,
            df.iloc[i].lon,
            estimated_lat_at_midpoint,
            estimated_lon_at_midpoint,
        )

        midpoint_discrepancies.append(discrepancy)

    midpoint_discrepancies.append(None)

    return midpoint_discrepancies


def track_check(df: pd.DataFrame) -> pd.DataFrame:
    """Perform one pass of the track check.  This is an implementation of the MDS track check code
    which was originally written in the 1990s. I don't know why this piece of historic trivia so exercises
    my mind, but it does: the 1990s! I wish my code would last so long.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the data to be checked

    Returns
    -------
    pd.DataFrame
        DataFrame with track check QC
    """
    required_columns = ["id", "date", "pt", "dck", "dsi", "vsi", "lat", "lon"]

    for key in required_columns:
        if key not in df:
            raise KeyError(f"{key} not in DataFrame")

    max_direction_change = 60.0
    max_speed_change = 10.0
    max_absolute_speed = 40.0
    max_midpoint_discrepancy = 150.0

    nobs = len(df)

    # no obs in, no qc outcomes out
    if nobs == 0:
        return df

    # Generic ids and buoys get a free pass on the track check
    if icoads_identify.id_is_generic(df.iloc[0].id, df.iloc[0].date.year) or df.iloc[
        0
    ].pt in [6, 7]:
        for i in range(0, nobs):
            df["trk"] = np.zeros(nobs)
            df["few"] = np.zeros(nobs)
        return df

    # fewer than three obs - set the fewsome flag
    # deck 720 gets a pass prior to 1891 see
    # Carella, Kent, Berry 2015 Appendix A3
    if nobs < 3:
        if df.iloc[0].dck == 720 and df.iloc[0].date.year < 1891:
            df["trk"] = np.zeros(nobs)
            df["few"] = np.zeros(nobs)
            return df
        else:
            df["trk"] = np.zeros(nobs)
            df["few"] = np.zeros(nobs) + 1
            return df

    # work out speeds and distances between alternating points
    df = calc_alternate_speeds(df)
    df = calculate_speed_course_distance_time_difference(df)

    # what are the mean and mode speeds?
    modal_speed = tc.modesp(df.speed)

    # set speed limits based on modal speed
    amax, _amaxx, _amin = tc.set_speed_limits(modal_speed)

    # compare reported speeds and positions if we have them
    forward_diff_from_estimated = forward_discrepancy(df)
    reverse_diff_from_estimated = backward_discrepancy(df)

    df["fwd_diff"] = forward_diff_from_estimated
    df["bwd_diff"] = reverse_diff_from_estimated

    midpoint_diff_from_estimated = calculate_midpoint(df)
    df["midpt"] = midpoint_diff_from_estimated

    # do QC
    trk = np.zeros(nobs)  # type: np.ndarray
    few = np.zeros(nobs)  # type: np.ndarray

    for i in range(1, nobs - 1):
        thisqc_a = 0
        thisqc_b = 0

        # together these cover the speeds calculate from point i
        if (
            df.iloc[i].speed is not None
            and df.iloc[i].speed > amax
            and df.iloc[i - 1].alt_speed is not None
            and df.iloc[i - 1].alt_speed > amax
        ):
            thisqc_a += 1.00
        elif (
            df.iloc[i + 1].speed is not None
            and df.iloc[i + 1].speed > amax
            and df.iloc[i + 1].alt_speed is not None
            and df.iloc[i + 1].alt_speed > amax
        ):
            thisqc_a += 2.00
        elif (
            df.iloc[i].speed is not None
            and df.iloc[i].speed > amax
            and df.iloc[i + 1].speed is not None
            and df.iloc[i + 1].speed > amax
        ):
            thisqc_a += 3.00

        # Quality-control by examining the distance
        # between the calculated and reported second position.
        thisqc_b += tc.check_distance_from_estimate(
            df.iloc[i].vsi,
            df.iloc[i - 1].vsi,
            df.iloc[i].time_diff,
            forward_diff_from_estimated[i],
            reverse_diff_from_estimated[i],
        )
        # Check for continuity of direction
        thisqc_b += tc.direction_continuity(
            df.iloc[i].dsi,
            df.iloc[i - 1].dsi,
            df.iloc[i].course,
            max_direction_change,
        )
        # Check for continuity of speed.
        thisqc_b += tc.speed_continuity(
            df.iloc[i].vsi,
            df.iloc[i - 1].vsi,
            df.iloc[i].speed,
            max_speed_change,
        )

        # check for speeds in excess of 40.00 knots
        if df.iloc[i].speed > max_absolute_speed / km_to_nm:
            thisqc_b += 10.0

        # make the final decision
        if (
            midpoint_diff_from_estimated[i] > max_midpoint_discrepancy / km_to_nm
            and thisqc_a > 0
            and thisqc_b > 0
        ):
            trk[i] = 1

    trk[nobs - 1] = 0
    few[nobs - 1] = 0

    df["trk"] = trk
    df["few"] = few

    return df


def find_saturated_runs(df: pd.DataFrame) -> pd.DataFrame:
    """Perform checks on persistence of 100% rh while going through the voyage.
    While going through the voyage repeated strings of 100 %rh (AT == DPT) are noted.
    If a string extends beyond 20 reports and two days/48 hrs in time then all values are set to
    fail the repsat qc flag.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to be checked

    Returns
    -------
    pd.DataFrame
    """
    for key in ["dpt", "at", "date"]:
        if key not in df:
            raise KeyError(f"{key} not in dataframe")

    min_time_threshold = 48.0  # hours
    shortest_run = 4  # number of obs

    satcount = []

    numobs = len(df)

    repsat = np.zeros(numobs)  # type: np.ndarray

    for i in range(numobs):

        row = df.iloc[i]

        saturated = row["dpt"] == row["at"]

        if saturated:
            satcount.append(i)
        elif not saturated and len(satcount) > shortest_run:

            row2 = df.iloc[satcount[len(satcount) - 1]]
            row1 = df.iloc[satcount[0]]
            _, _, _, tdiff = row_difference(row2, row1)

            if tdiff >= min_time_threshold:
                for loc in satcount:
                    repsat[loc] = 1
                satcount = []
            else:
                satcount = []

        else:
            satcount = []

    if len(satcount) > shortest_run:
        row2 = df.iloc[satcount[len(satcount) - 1]]
        row1 = df.iloc[satcount[0]]
        _, _, _, tdiff = row_difference(row2, row1)

        if tdiff >= min_time_threshold:
            for loc in satcount:
                repsat[loc] = 1

    df["repsat"] = repsat

    return df


def find_multiple_rounded_values(df: pd.DataFrame, intype: str) -> pd.DataFrame:
    """Find instances when more than "threshold" of the observations are
    whole numbers and set the 'round' flag. Used in the humidity QC
    where there are times when the values are rounded and this may
    have caused a bias.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing data to be checked
    intype: str
        Specifies which variable should be quality controlled

    Returns
    -------
    pd.DataFrame
        Returns dataframe with additional column "rounded" containing QC outcomes
    """
    allowed_variables = ["sst", "at", "dpt"]
    if intype not in allowed_variables:
        raise ValueError(f"{intype} not one of {allowed_variables}")

    min_count = 20
    threshold = 0.5

    assert 0.0 <= threshold <= 1.0

    numobs = len(df)
    rounded = np.zeros(numobs)  # type: np.ndarray

    valcount = {}
    allcount = 0

    for i in range(numobs):
        row = df.iloc[i]
        if row[intype] is not None:
            allcount += 1
            if str(row[intype]) in valcount:
                valcount[str(row[intype])].append(i)
            else:
                valcount[str(row[intype])] = [i]

    if allcount > min_count:
        wholenums = 0
        for key in valcount:
            if float(key).is_integer():
                wholenums = wholenums + len(valcount[key])

        if float(wholenums) / float(allcount) >= threshold:
            for key in valcount:
                if float(key).is_integer():
                    for i in valcount[key]:
                        rounded[i] = 1

    df["rounded"] = rounded

    return df


def find_repeated_values(df: pd.DataFrame, intype: str) -> pd.DataFrame:
    """Find cases where more than a given proportion of SSTs have the same value

    This function goes through a voyage and finds any cases where more than a threshold fraction of
    the observations have the same values for a specified variable.


    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing data to be checked
    intype: str
        Specifies which variable should be quality controlled

    Returns
    -------
    pd.DataFrame
        Returns dataframe with additional column "rep" containing QC outcomes
    """
    allowed_variables = ["sst", "at", "dpt", "slp"]
    if intype not in allowed_variables:
        raise ValueError(f"{intype} not one of {allowed_variables}")

    threshold = 0.7
    assert 0.0 <= threshold <= 1.0
    min_count = 20

    numobs = len(df)
    rep = np.zeros(numobs)  # type: np.ndarray

    valcount = {}
    allcount = 0

    for i in range(numobs):
        row = df.iloc[i]
        value = row[intype]
        if value is not None:
            allcount += 1
            if str(value) in valcount:
                valcount[str(value)].append(i)
            else:
                valcount[str(value)] = [i]

    if allcount > min_count:
        for key in valcount:
            if float(len(valcount[key])) / float(allcount) > threshold:
                for i in valcount[key]:
                    rep[i] = 1

    df["rep"] = rep

    return df


def iquam_track_check(df: pd.DataFrame) -> pd.DataFrame:
    """Perform the IQUAM track check as detailed in Xu and Ignatov 2013

    The track check calculates speeds between pairs of observations and
    counts how many exceed a threshold speed. The ob with the most
    violations of this limit is flagged as bad and removed from the
    calculation. Then the next worst is found and removed until no
    violatios remain.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing data to be track checked.

    Returns
    -------
    pd.DataFrame
        Returns DataFrame with additional column "iquam_track" containing the outcomes of the QC
    """
    for key in ["lat", "lon", "id", "date"]:
        if key not in df:
            raise KeyError(f"{key} not in dataframe")

    buoy_speed_limit = 15.0  # km/h
    ship_speed_limit = 60.0  # km/h

    delta_d = 1.11  # 0.1 degrees of latitude
    delta_t = 0.01  # one hundredth of an hour

    n_neighbours = 5

    numobs = len(df)

    if numobs == 0:
        return df

    if icoads_identify.id_is_generic(df.iloc[0].id, df.iloc[0].date.year):
        df["iquam_track"] = np.zeros(numobs)
        return df

    if df.iloc[0].pt in [6, 7]:
        speed_limit = buoy_speed_limit
    else:
        speed_limit = ship_speed_limit

    speed_violations = []
    count_speed_violations = []

    iquam_track = np.zeros(numobs)  # type: np.ndarray

    for t1 in range(0, numobs):
        violations_for_this_report = []
        count_violations_this_report = 0.0

        lo = max(0, t1 - n_neighbours)
        hi = min(numobs, t1 + n_neighbours + 1)

        for t2 in range(lo, hi):

            row2 = df.iloc[t2]
            row1 = df.iloc[t1]

            _, distance, _, time_diff = row_difference(row2, row1)

            iquam_condition = max([abs(distance) - delta_d, 0.0]) / (
                abs(time_diff) + delta_t
            )

            if iquam_condition > speed_limit:
                violations_for_this_report.append(t2)
                count_violations_this_report += 1.0

        speed_violations.append(violations_for_this_report)
        count_speed_violations.append(count_violations_this_report)

    count = 0
    while np.sum(count_speed_violations) > 0.0:
        most_fails = int(np.argmax(count_speed_violations))
        iquam_track[most_fails] = 1

        for index in speed_violations[most_fails]:
            if most_fails in speed_violations[index]:
                speed_violations[index].remove(most_fails)
                count_speed_violations[index] -= 1.0

        count_speed_violations[most_fails] = 0
        count += 1

    df["iquam_track"] = iquam_track

    return df
