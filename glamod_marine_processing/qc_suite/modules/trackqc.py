"""Marine QC tracking module."""

# noqa: S101

from __future__ import annotations

import copy
import math
import warnings

import numpy as np

from . import Extended_IMMA as ex
from .astronomical_geometry import sunangle
from .auxiliary import isvalid
from .spherical_geometry import sphere_distance
from .time_control import dayinyear

"""
The trackqc module contains a set of functions for performing the tracking QC
first described in Atkinson et al. [2013]. The general procedures described
in Atkinson et al. [2013] were later revised and improved for the SST CCI 2 project.
Documentation and IDL code for the revised (and original) procedures can be found
in the CMA FCM code repository. The code in this module represents a port of the
revised IDL code into the python marine QC suite. New versions of the aground
and speed checks have also been added.

These functions perform tracking QC checks on a :py:class:`ex.Voyage`.

References:

Atkinson, C.P., N.A. Rayner, J. Roberts-Jones, R.O. Smith, 2013:
Assessing the quality of sea surface temperature observations from
drifting buoys and ships on a platform-by-platform basis (doi:10.1002/jgrc.20257).
"""


def track_day_test(
    year: int,
    month: int,
    day: int,
    hour: float,
    lat: float,
    lon: float,
    elevdlim: float = -2.5,
) -> bool:
    """Given date, time, lat and lon calculate if the sun elevation is > elevdlim.
    If so return daytime is True

    This is the "day" test used by tracking QC to decide whether an SST measurement is night or day.
    This is important because daytime diurnal heating can affect comparison with an SST background.
    It uses the function sunangle to calculate the elevation of the sun. A default solar_zenith angle
    of 92.5 degrees (elevation of -2.5 degrees) delimits night from day.

    Parameters
    ----------
    year: int
        Year
    month: int
        Month
    day: int
        Day
    hour: float
        Hour expressed as decimal fraction (e.g. 20.75 = 20:45 pm)
    lat: float
        Latitude in degrees
    lon: float
        Longitude in degrees
    elevdlim: float
        Elevation day/night delimiter in degrees above horizon

    Returns
    -------
    bool
        True if daytime, else False.

    Raises
    ------
    ValueError
        When input values are invalid
    """
    warnings.warn(
        DeprecationWarning(
            "This module trackqc is deprecated, use next_level_trackqc instead"
        )
    )

    if not isvalid(year):
        raise ValueError("year is missing")
    if not isvalid(month):
        raise ValueError("month is missing")
    if not isvalid(day):
        raise ValueError("day is missing")
    if not isvalid(hour):
        raise ValueError("hour is missing")
    if not isvalid(lat):
        raise ValueError("lat is missing")
    if not isvalid(lon):
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

    _, elevation, _, _, _, _ = sunangle(
        year2, day2, hour2, minute2, 0, 0, 0, lat2, lon2
    )

    if elevation > elevdlim:
        daytime = True

    return daytime


def trim_mean(inarr: list, trim: int) -> float:
    """Calculate a resistant (aka robust) mean of an input array given a trimming criteria.

    Parameters
    ----------
    inarr: list
        1-dimensional array of numbers
    trim: int
        trimming criteria. A value of 10 trims one tenth of the values off each end of the sorted array
        before calculating the mean.

    Returns
    -------
    float
        Trimmed mean
    """
    warnings.warn(
        DeprecationWarning(
            "This module trackqc is deprecated, use next_level_trackqc instead"
        )
    )

    arr = np.array(inarr)  # type: np.ndarray
    if trim == 0:
        return float(np.mean(arr))

    length = len(arr)
    arr.sort()

    index1 = int(length / trim)

    trim = float(np.mean(arr[index1 : length - index1]))

    return trim


def trim_std(inarr: list, trim: int) -> float:
    """Calculate a resistant (aka robust) standard deviation of an input array given a trimming criteria.

    Parameters
    ----------
    inarr : list
        Array of numbers
    trim: int
        trimming criteria. A value of 10 trims one tenth of the values off each end of the sorted array before
        calculating the standard deviation.

    Returns
    -------
    float
        Returns trimmed standard deviation
    """
    warnings.warn(
        DeprecationWarning(
            "This module trackqc is deprecated, use next_level_trackqc instead"
        )
    )

    arr = np.array(inarr)  # type: np.ndarray
    if trim == 0:
        return float(np.std(arr))

    length = len(arr)
    arr.sort()

    index1 = int(length / trim)

    trim = float(np.std(arr[index1 : length - index1]))

    return trim


def do_new_speed_check(reps, *args):
    warnings.warn(
        DeprecationWarning(
            "This module trackqc is deprecated, use next_level_trackqc instead"
        )
    )
    checker = NewSpeedChecker(reps)
    if args:
        checker.set_parameters(*args)
    checker.do_qc()


class NewSpeedChecker:
    """Check to see whether a drifter has been picked up by a ship (out of water) based on 1/100th degree
    precision positions. A flag 'drf_spd' is set for each input report: flag=1 for reports deemed picked up,
    else flag=0.

    A drifter is deemed picked up if it is moving faster than might be expected for a fast ocean current
    (a few m/s). Unreasonably fast movement is detected when speed of travel between report-pairs exceeds
    the chosen 'speed_limit' (speed is estimated as distance between reports divided by time separation -
    this 'straight line' speed between the two points is a minimum speed estimate given a less-direct
    path may have been followed). Positional errors introduced by lon/lat 'jitter' and data precision
    can be of order several km's. Reports must be separated by a suitably long period of time (the 'min_win_period')
    to minimise the effect of these errors when calculating speed e.g. for reports separated by 9 hours
    errors of order 10 cm/s would result which are a few percent of fast ocean current speed. Conversley,
    the period of time chosen should not be too long so as to resolve short-lived burst of speed on
    manouvering ships. Larger positional errors may also trigger the check.

    For each report, speed is assessed over the shortest available period that exceeds 'min_win_period'.

    Prior to assessment the drifter record is screened for positional errors using the iQuam track check
    method (from :py:class:`ex.Voyage`). When running the iQuam check the record is treated as a ship (not a
    drifter) so as to avoid accidentally filtering out observations made aboard a ship (which is what we
    are trying to detect). This iQuam track check does not overwrite any existing iQuam track check flags.

    IMPORTANT - for optimal performance, drifter records with observations failing this check should be
    subsequently manually reviewed. Ships move around in all sorts of complicated ways that can readily
    confuse such a simple check (e.g. pausing at sea, crisscrossing its own path) and once some erroneous
    movement is detected it is likely a human operator can then better pick out the actual bad data. False
    fails caused by positional errors (particularly in fast ocean currents) will also need reinstating.

    The class has the following class attributes which can be modified using the set_parameters method.

    iquam_parameters: Parameter dictionary for Voyage.iquam_track_check() function.
    speed_limit: maximum allowable speed for an in situ drifting buoy (metres per second)
    min_win_period: minimum period of time in days over which position is assessed for speed estimates (see
    description)
    """

    iquam_parameters = {}
    speed_limit = 3.0
    min_win_period = 0.375

    def __init__(self, reps):
        self.reps = reps

        self.lon = None
        self.lat = None
        self.hrs = None
        self.iquam_track_ship = None

    def set_parameters(
        self, iquam_parameters: dict, speed_limit: float, min_win_period: float
    ) -> None:
        """Set the parameters of the QC check. Note that this will set parameters for all instances of the class.

        Parameters
        ----------
        iquam_parameters: dict
            Parameter dictionary for Voyage.iquam_track_check() function.
        speed_limit: float
            Maximum allowable speed for an in situ drifting buoy (metres per second)
        min_win_period: float
            minimum period of time in days over which position is assessed for speed estimates (see
            description)

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            When any of the parameters is invalid
        """
        try:
            speed_limit = float(speed_limit)
            min_win_period = float(min_win_period)
            assert speed_limit >= 0, "speed_limit must be >= 0"
            assert min_win_period >= 0, "min_win_period must be >= 0"
        except AssertionError as error:
            raise AssertionError("invalid input parameter: " + str(error))

        NewSpeedChecker.iquam_parameters = iquam_parameters
        NewSpeedChecker.speed_limit = speed_limit
        NewSpeedChecker.min_win_period = min_win_period

    def do_qc(self) -> None:
        """Perform the new speed check QC"""
        nrep = len(self.reps)

        # pairs of records are needed to evaluate speed
        if nrep <= 1:
            for rep in self.reps:
                rep.set_qc("POS", "drf_spd", 0)
            return

        self._preprocess_reps()
        self._initialise_reps()
        self._do_speed_check()

    def _preprocess_reps(self) -> None:
        """Process the reps and calculate the values used in the QC check"""
        nrep = len(self.reps)

        # retrieve lon/lat/time_diff variables from marine reports
        lon = np.empty(nrep)  # type: np.ndarray
        lon[:] = np.nan
        lat = np.empty(nrep)  # type: np.ndarray
        lat[:] = np.nan
        hrs = np.empty(nrep)  # type: np.ndarray
        hrs[:] = np.nan
        try:
            for ind, rep in enumerate(self.reps):
                lon[ind] = rep.getvar("LON")  # returns None if missing
                lat[ind] = rep.getvar("LAT")  # returns None if missing
                if ind == 0:
                    hrs[ind] = 0
                else:
                    hrs[ind] = rep.getext(
                        "time_diff"
                    )  # raises assertion error if 'time_diff' not found
            assert not any(np.isnan(lon)), "Nan(s) found in longitude"
            assert not any(np.isnan(lat)), "Nan(s) found in latitude"
            assert not any(np.isnan(hrs)), "Nan(s) found in time differences"
            assert not any(np.less(hrs, 0)), "times are not sorted"
        except AssertionError as error:
            raise AssertionError("problem with report values: " + str(error))

        hrs = np.cumsum(hrs)  # get time difference in hours relative to first report

        # perform iQuam track check as if a ship
        # a deep copy of reps is made so metadata can be safely modified ahead of iQuam check
        # an array of qc flags (iquam_track_ship) is the result
        reps_copy = copy.deepcopy(self.reps)
        v = ex.Voyage()
        qc_list = []
        for rep in reps_copy:
            rep.setvar("PT", 5)  # ship
            rep.set_qc("POS", "iquam_track", 0)  # reset iquam parameters
            v.add_report(rep)
        v.iquam_track_check(NewSpeedChecker.iquam_parameters)
        for rep in v.rep_feed():
            qc_list.append(rep.get_qc("POS", "iquam_track"))
        iquam_track_ship = np.array(qc_list)  # type: np.ndarray
        del reps_copy, v, qc_list

        self.iquam_track_ship = iquam_track_ship
        self.lat = lat
        self.lon = lon
        self.hrs = hrs

    def _initialise_reps(self) -> None:
        """Initialise the QC flags in the reports"""
        # begin by setting all reports to pass
        for rep in self.reps:
            rep.set_qc("POS", "drf_spd", 0)

    def _do_speed_check(self) -> None:
        """Perform the actual speed check"""
        nrep = len(self.reps)
        min_win_period_hours = NewSpeedChecker.min_win_period * 24.0

        # loop through timeseries to see if drifter is moving too fast and flag any occurrences
        index_arr = np.array(range(0, nrep))  # type: np.ndarray
        i = 0
        time_to_end = self.hrs[-1] - self.hrs[i]
        while time_to_end >= min_win_period_hours:
            if self.iquam_track_ship[i] == 1:
                i += 1
                time_to_end = self.hrs[-1] - self.hrs[i]
                continue
            f_win = (self.hrs >= self.hrs[i] + min_win_period_hours) & (
                self.iquam_track_ship == 0
            )
            if not any(f_win):
                i += 1
                time_to_end = self.hrs[-1] - self.hrs[i]
                continue

            win_len = self.hrs[f_win][0] - self.hrs[i]
            displace = sphere_distance(
                self.lat[i], self.lon[i], self.lat[f_win][0], self.lon[f_win][0]
            )
            speed = displace / win_len  # km per hr
            speed = speed * 1000.0 / (60.0 * 60)  # metres per sec

            if speed > NewSpeedChecker.speed_limit:
                for ix in range(i, index_arr[f_win][0] + 1):
                    if self.reps[ix].get_qc("POS", "drf_spd") == 0:
                        self.reps[ix].set_qc("POS", "drf_spd", 1)
                i += 1
                time_to_end = self.hrs[-1] - self.hrs[i]
            else:
                i += 1
                time_to_end = self.hrs[-1] - self.hrs[i]


def do_speed_check(reps, *args):
    warnings.warn(
        DeprecationWarning(
            "This module trackqc is deprecated, use next_level_trackqc instead"
        )
    )
    checker = SpeedChecker(reps)
    if args:
        checker.set_parameters(*args)
    checker.do_qc()


class SpeedChecker:
    """Check to see whether a drifter has been picked up by a ship (out of water) based on 1/100th degree
    precision positions. A flag 'drf_spd' is set for each input report: flag=1 for reports deemed picked up,
    else flag=0.

    A drifter is deemed picked up if it is moving faster than might be expected for a fast ocean current
    (a few m/s). Unreasonably fast movement is detected when speed of travel between report-pairs exceeds
    the chosen 'speed_limit' (speed is estimated as distance between reports divided by time separation -
    this 'straight line' speed between the two points is a minimum speed estimate given a less-direct
    path may have been followed). Positional errors introduced by lon/lat 'jitter' and data precision
    can be of order several km's. Reports must be separated by a suitably long period of time (the 'min_win_period')
    to minimise the effect of these errors when calculating speed e.g. for reports separated by 24 hours
    errors of several cm/s would result which are two orders of magnitude less than a fast ocean current
    which seems reasonable. Conversley, the period of time chosen should not be too long so as to resolve
    short-lived burst of speed on manouvering ships. Larger positional errors may also trigger the check.
    Because temporal sampling can be erratic the time period over which this assessment is made is specified
    as a range (bound by 'min_win_period' and 'max_win_period') - assessment uses the longest time separation
    available within this range.

    IMPORTANT - for optimal performance, drifter records with observations failing this check should be
    subsequently manually reviewed. Ships move around in all sorts of complicated ways that can readily
    confuse such a simple check (e.g. pausing at sea, crisscrossing its own path) and once some erroneous
    movement is detected it is likely a human operator can then better pick out the actual bad data. False
    fails caused by positional errors (particularly in fast ocean currents) will also need reinstating.

    speed_limit: maximum allowable speed for an in situ drifting buoy (metres per second)
    min_win_period: minimum period of time in days over which position is assessed for speed estimates (see description)
    max_win_period: maximum period of time in days over which position is assessed for speed estimates
    (this should be greater than min_win_period and allow for some erratic temporal sampling e.g. min_win_period+0.2
    to allow for gaps of up to 0.2-days in sampling).
    """

    speed_limit = 2.5
    min_win_period = 0.8
    max_win_period = 1.0

    def __init__(self, reps):

        self.reps = reps

        self.lon = None
        self.lat = None
        self.hrs = None

    def set_parameters(
        self, speed_limit: float, min_win_period: float, max_win_period: float
    ) -> None:
        """Set the parameters of the QC check. Note that this will set parameters for all instances of the class.

        Parameters
        ----------
        speed_limit: float
            maximum allowable speed for an in situ drifting buoy (metres per second)
        min_win_period: float
            minimum period of time in days over which position is assessed for speed estimates (see
            description)
        max_win_period: float
            maximum period of time in days over which position is assessed for speed estimates
            (this should be greater than min_win_period and allow for some erratic temporal sampling e.g. min_win_period+0.2
            to allow for gaps of up to 0.2-days in sampling).

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            When any of the input parameters are invalid
        """
        try:
            speed_limit = float(speed_limit)
            min_win_period = float(min_win_period)
            max_win_period = float(max_win_period)
            assert speed_limit >= 0, "speed_limit must be >= 0"
            assert min_win_period >= 0, "min_win_period must be >= 0"
            assert max_win_period >= 0, "max_win_period must be >= 0"
            assert (
                max_win_period >= min_win_period
            ), "max_win_period must be >= min_win_period"
        except AssertionError as error:
            raise AssertionError("invalid input parameter: " + str(error))

        SpeedChecker.speed_limit = speed_limit
        SpeedChecker.min_win_period = min_win_period
        SpeedChecker.max_win_period = max_win_period

    def do_qc(self) -> None:
        """Perform the new speed check QC"""
        nrep = len(self.reps)
        # pairs of records are needed to evaluate speed
        if nrep <= 1:
            for rep in self.reps:
                rep.set_qc("POS", "drf_spd", 0)
            return

        self._preprocess_reps()
        self._initialise_reps()
        self._do_speed_check()

    def _initialise_reps(self) -> None:
        """Initialise the QC flags in the reports"""
        # begin by setting all reports to pass
        for rep in self.reps:
            rep.set_qc("POS", "drf_spd", 0)

    def _preprocess_reps(self):
        """Process the reps and calculate the values used in the QC check"""
        nrep = len(self.reps)

        # retrieve lon/lat/time_diff variables from marine reports
        lon = np.empty(nrep)  # type: np.ndarray
        lon[:] = np.nan
        lat = np.empty(nrep)  # type: np.ndarray
        lat[:] = np.nan
        hrs = np.empty(nrep)  # type: np.ndarray
        hrs[:] = np.nan
        try:
            for ind, rep in enumerate(self.reps):
                lon[ind] = rep.getvar("LON")  # returns None if missing
                lat[ind] = rep.getvar("LAT")  # returns None if missing
                if ind == 0:
                    hrs[ind] = 0
                else:
                    hrs[ind] = rep.getext(
                        "time_diff"
                    )  # raises assertion error if 'time_diff' not found
            assert not any(np.isnan(lon)), "Nan(s) found in longitude"
            assert not any(np.isnan(lat)), "Nan(s) found in latitude"
            assert not any(np.isnan(hrs)), "Nan(s) found in time differences"
            assert not any(np.less(hrs, 0)), "times are not sorted"
        except AssertionError as error:
            raise AssertionError("problem with report values: " + str(error))

        hrs = np.cumsum(hrs)  # get time difference in hours relative to first report

        self.lon = lon
        self.lat = lat
        self.hrs = hrs

    def _do_speed_check(self):
        """Perform the actual speed check"""
        nrep = len(self.reps)
        min_win_period_hours = SpeedChecker.min_win_period * 24.0
        max_win_period_hours = SpeedChecker.max_win_period * 24.0

        # loop through timeseries to see if drifter is moving too fast
        # and flag any occurrences
        index_arr = np.array(range(0, nrep))  # type: np.ndarray
        i = 0
        time_to_end = self.hrs[-1] - self.hrs[i]
        while time_to_end >= min_win_period_hours:
            f_win = self.hrs <= self.hrs[i] + max_win_period_hours
            win_len = self.hrs[f_win][-1] - self.hrs[i]
            if win_len < min_win_period_hours:
                i += 1
                time_to_end = self.hrs[-1] - self.hrs[i]
                continue

            displace = sphere_distance(
                self.lat[i], self.lon[i], self.lat[f_win][-1], self.lon[f_win][-1]
            )
            speed = displace / win_len  # km per hr
            speed = speed * 1000.0 / (60.0 * 60)  # metres per sec

            if speed > SpeedChecker.speed_limit:
                for ix in range(i, index_arr[f_win][-1] + 1):
                    if self.reps[ix].get_qc("POS", "drf_spd") == 0:
                        self.reps[ix].set_qc("POS", "drf_spd", 1)
                i += 1
                time_to_end = self.hrs[-1] - self.hrs[i]
            else:
                i += 1
                time_to_end = self.hrs[-1] - self.hrs[i]


def do_aground_check(reps, *args):
    warnings.warn(
        DeprecationWarning(
            "This module trackqc is deprecated, use next_level_trackqc instead"
        )
    )
    checker = AgroundChecker(reps)
    if args:
        checker.set_parameters(*args)
    checker.do_qc()


class AgroundChecker:
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
    as a range (bound by 'min_win_period' and 'max_win_period') - assessSment uses the longest time separation
    available within this range. If a drifter is deemed aground and subsequently starts moving (e.g. if a drifter
    has moved very slowly for a prolonged period) incorrectly flagged reports will be reinstated.

    smooth_win: length of window (odd number) in datapoints used for smoothing lon/lat
    min_win_period: minimum period of time in days over which position is assessed for no movement (see description)
    max_win_period: maximum period of time in days over which position is assessed for no movement (this should be
    greater than min_win_period and allow for erratic temporal sampling e.g. min_win_period+2 to allow for gaps of
    up to 2-days in sampling).

    The following Class attributes are used to store the parameters of the QC check. These can be modified using
    the set_parameters method.

    smooth_win: length of window (odd number) in datapoints used for smoothing lon/lat
    min_win_period: minimum period of time in days over which position is assessed for no movement (see description)
    max_win_period: maximum period of time in days over which position is assessed for no movement (this should be
    greater than min_win_period and allow for erratic temporal sampling e.g. min_win_period+2 to allow for gaps of
    up to 2-days in sampling).
    """

    smooth_win = 41
    min_win_period = 8
    max_win_period = 10

    # displacement resulting from 1/100th deg 'position-jitter' at equator (km)
    tolerance = sphere_distance(0, 0, 0.01, 0.01)

    def __init__(self, reps):
        self.reps = reps

        self.lon_smooth = None
        self.lat_smooth = None
        self.hrs_smooth = None

    def set_parameters(
        self, smooth_win: int, min_win_period: int, max_win_period: int
    ) -> None:
        """Set the parameters of the QC check. Note that this will set parameters for all instances of the class.

        Parameters
        ----------
        smooth_win: int
            Length of window (odd number) in datapoints used for smoothing lon/lat
        min_win_period: int
            minimum period of time in days over which position is assessed for no movement (see description)
        max_win_period: int
            maximum period of time in days over which position is assessed for no movement (this should be greater
            than min_win_period and allow for erratic temporal sampling e.g. min_win_period+2 to allow for gaps of
            up to 2-days in sampling).

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            When any of the input values are invalid
        """
        try:
            smooth_win = int(smooth_win)
            min_win_period = int(min_win_period)
            max_win_period = int(max_win_period)
            assert smooth_win >= 1, "smooth_win must be >= 1"
            assert smooth_win % 2 != 0, "smooth_win must be an odd number"
            assert min_win_period >= 1, "min_win_period must be >= 1"
            assert max_win_period >= 1, "max_win_period must be >= 1"
            assert (
                max_win_period >= min_win_period
            ), "max_win_period must be >= min_win_period"
        except AssertionError as error:
            raise AssertionError("invalid input parameter: " + str(error))

        AgroundChecker.smooth_win = smooth_win
        AgroundChecker.min_win_period = min_win_period
        AgroundChecker.max_win_period = max_win_period

    def do_qc(self):
        """Perform the new aground check QC"""
        nrep = len(self.reps)
        # records shorter than smoothing-window can't be evaluated
        if nrep <= AgroundChecker.smooth_win:
            for rep in self.reps:
                rep.set_qc("POS", "drf_agr", 0)
            return

        self._preprocess_reps()
        self._do_aground_check()

    def _preprocess_reps(self) -> None:
        """Process the reps and calculate the values used in the QC check"""
        nrep = len(self.reps)
        half_win = int((AgroundChecker.smooth_win - 1) / 2)

        # retrieve lon/lat/time_diff variables from marine reports
        lon = np.empty(nrep)  # type: np.ndarray
        lon[:] = np.nan
        lat = np.empty(nrep)  # type: np.ndarray
        lat[:] = np.nan
        hrs = np.empty(nrep)  # type: np.ndarray
        hrs[:] = np.nan
        try:
            for ind, rep in enumerate(self.reps):
                lon[ind] = rep.getvar("LON")  # returns None if missing
                lat[ind] = rep.getvar("LAT")  # returns None if missing
                if ind == 0:
                    hrs[ind] = 0
                else:
                    # raises assertion error if 'time_diff' not found
                    hrs[ind] = rep.getext("time_diff")
            assert not any(np.isnan(lon)), "Nan(s) found in longitude"
            assert not any(np.isnan(lat)), "Nan(s) found in latitude"
            assert not any(np.isnan(hrs)), "Nan(s) found in time differences"
            assert not any(np.less(hrs, 0)), "times are not sorted"
        except AssertionError as error:
            raise AssertionError("problem with report values: " + str(error))

        hrs = np.cumsum(hrs)  # get time difference in hours relative to first report

        # create smoothed lon/lat timeseries
        nrep_smooth = (
            nrep - AgroundChecker.smooth_win + 1
        )  # length of series after smoothing
        lon_smooth = np.empty(nrep_smooth)  # type: np.ndarray
        lon_smooth[:] = np.nan
        lat_smooth = np.empty(nrep_smooth)  # type: np.ndarray
        lat_smooth[:] = np.nan
        hrs_smooth = np.empty(nrep_smooth)  # type: np.ndarray
        hrs_smooth[:] = np.nan
        try:
            for i in range(0, nrep_smooth):
                lon_smooth[i] = np.median(lon[i : i + AgroundChecker.smooth_win])
                lat_smooth[i] = np.median(lat[i : i + AgroundChecker.smooth_win])
                hrs_smooth[i] = hrs[i + half_win]
            assert not any(np.isnan(lon_smooth)), "Nan(s) found in smoothed longitude"
            assert not any(np.isnan(lat_smooth)), "Nan(s) found in smoothed latitude"
            assert not any(
                np.isnan(hrs_smooth)
            ), "Nan(s) found in smoothed time differences"
        except AssertionError as error:
            raise AssertionError("problem with smoothed report values: " + str(error))

        self.lon_smooth = lon_smooth
        self.lat_smooth = lat_smooth
        self.hrs_smooth = hrs_smooth

    def _do_aground_check(self):
        """Perform the actual aground check"""
        half_win = (AgroundChecker.smooth_win - 1) / 2
        min_win_period_hours = AgroundChecker.min_win_period * 24.0
        max_win_period_hours = AgroundChecker.max_win_period * 24.0

        # loop through smoothed timeseries to see if drifter has run aground
        i = 0
        is_aground = False  # keeps track of whether drifter is deemed aground
        i_aground = np.nan  # keeps track of index when drifter first ran aground
        time_to_end = self.hrs_smooth[-1] - self.hrs_smooth[i]
        while time_to_end >= min_win_period_hours:
            f_win = self.hrs_smooth <= self.hrs_smooth[i] + max_win_period_hours
            win_len = self.hrs_smooth[f_win][-1] - self.hrs_smooth[i]
            if win_len < min_win_period_hours:
                i += 1
                time_to_end = self.hrs_smooth[-1] - self.hrs_smooth[i]
                continue

            displace = sphere_distance(
                self.lat_smooth[i],
                self.lon_smooth[i],
                self.lat_smooth[f_win][-1],
                self.lon_smooth[f_win][-1],
            )
            if displace <= AgroundChecker.tolerance:
                if not (is_aground):
                    is_aground = True
                    i_aground = i
            else:
                is_aground = False
                i_aground = np.nan

            i += 1
            time_to_end = self.hrs_smooth[-1] - self.hrs_smooth[i]

        # set flags
        if is_aground and i_aground > 0:
            i_aground += half_win
        # this gets the first index the drifter is deemed aground for the original (un-smoothed) timeseries
        # n.b. if i_aground=0 then the entire drifter record is deemed aground and flagged as such
        for ind, rep in enumerate(self.reps):
            if is_aground and ind >= i_aground:
                rep.set_qc("POS", "drf_agr", 1)
            else:
                rep.set_qc("POS", "drf_agr", 0)


def do_new_aground_check(reps, *args):
    warnings.warn(
        DeprecationWarning(
            "This module trackqc is deprecated, use next_level_trackqc instead"
        )
    )
    checker = NewAgroundChecker(reps)
    if args:
        checker.set_parameters(*args)
    checker.do_qc()


class NewAgroundChecker:
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

    The check progresses by comparing each report with the final report (i.e. the first report with the
    final report, the second report with the final report and so on) until the time separation between reports
    is less than 'min_win_period'. If a drifter is deemed aground and subsequently starts moving (e.g. if a drifter
    has followed a circular path) incorrectly flagged reports will be reinstated.

    The class has the following class attributes which can be modified using the set_parameters method.

    smooth_win: length of window (odd number) in datapoints used for smoothing lon/lat
    min_win_period: minimum period of time in days over which position is assessed for no movement (see description)
    """

    smooth_win = 41
    min_win_period = 8
    tolerance = sphere_distance(0, 0, 0.01, 0.01)

    def __init__(self, reps):
        self.reps = reps

    def set_parameters(self, smooth_win: int, min_win_period: int) -> None:
        """Set the parameters of the QC check. Note that this will set parameters for all instances of the class.

        Parameters
        ----------
        smooth_win: int
            length of window (odd number) in datapoints used for smoothing lon/lat
        min_win_period: int
            minimum period of time in days over which position is assessed for no movement (see description)

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            When any of the input values are invalid
        """
        try:
            smooth_win = int(smooth_win)
            min_win_period = int(min_win_period)
            assert smooth_win >= 1, "smooth_win must be >= 1"
            assert smooth_win % 2 != 0, "smooth_win must be an odd number"
            assert min_win_period >= 1, "min_win_period must be >= 1"
        except AssertionError as error:
            raise AssertionError("invalid input parameter: " + str(error))
        NewAgroundChecker.smooth_win = smooth_win
        NewAgroundChecker.min_win_period = min_win_period

    def do_qc(self) -> None:
        """Perform the new speed check QC"""
        nrep = len(self.reps)

        # records shorter than smoothing-window can't be evaluated
        if nrep <= NewAgroundChecker.smooth_win:
            for rep in self.reps:
                rep.set_qc("POS", "drf_agr", 0)
            return

        self._preprocess_reps()
        self._do_aground_check()

    def _preprocess_reps(self) -> None:
        """Process the reps and calculate the values used in the QC check"""
        nrep = len(self.reps)
        half_win = int((NewAgroundChecker.smooth_win - 1) / 2)
        min_win_period_hours = NewAgroundChecker.min_win_period * 24.0

        # retrieve lon/lat/time_diff variables from marine reports
        lon = np.empty(nrep)  # type: np.ndarray
        lon[:] = np.nan
        lat = np.empty(nrep)  # type: np.ndarray
        lat[:] = np.nan
        hrs = np.empty(nrep)  # type: np.ndarray
        hrs[:] = np.nan

        try:
            for ind, rep in enumerate(self.reps):
                lon[ind] = rep.getvar("LON")  # returns None if missing
                lat[ind] = rep.getvar("LAT")  # returns None if missing
                if ind == 0:
                    hrs[ind] = 0
                else:
                    hrs[ind] = rep.getext(
                        "time_diff"
                    )  # raises assertion error if 'time_diff' not found
            assert not any(np.isnan(lon)), "Nan(s) found in longitude"
            assert not any(np.isnan(lat)), "Nan(s) found in latitude"
            assert not any(np.isnan(hrs)), "Nan(s) found in time differences"
            assert not any(np.less(hrs, 0)), "times are not sorted"
        except AssertionError as error:
            raise AssertionError("problem with report values: " + str(error))

        hrs = np.cumsum(hrs)  # get time difference in hours relative to first report

        # create smoothed lon/lat timeseries
        nrep_smooth = (
            nrep - NewAgroundChecker.smooth_win + 1
        )  # length of series after smoothing
        lon_smooth = np.empty(nrep_smooth)  # type: np.ndarray
        lon_smooth[:] = np.nan
        lat_smooth = np.empty(nrep_smooth)  # type: np.ndarray
        lat_smooth[:] = np.nan
        hrs_smooth = np.empty(nrep_smooth)  # type: np.ndarray
        hrs_smooth[:] = np.nan
        try:
            for i in range(0, nrep_smooth):
                lon_smooth[i] = np.median(lon[i : i + NewAgroundChecker.smooth_win])
                lat_smooth[i] = np.median(lat[i : i + NewAgroundChecker.smooth_win])
                hrs_smooth[i] = hrs[i + half_win]
            assert not any(np.isnan(lon_smooth)), "Nan(s) found in smoothed longitude"
            assert not any(np.isnan(lat_smooth)), "Nan(s) found in smoothed latitude"
            assert not any(
                np.isnan(hrs_smooth)
            ), "Nan(s) found in smoothed time differences"
        except AssertionError as error:
            raise AssertionError("problem with smoothed report values: " + str(error))

        self.lat_smooth = lat_smooth
        self.lon_smooth = lon_smooth
        self.hrs_smooth = hrs_smooth

    def _do_aground_check(self) -> None:
        """Perform the actual aground check"""
        half_win = int((NewAgroundChecker.smooth_win - 1) / 2)
        min_win_period_hours = NewAgroundChecker.min_win_period * 24.0

        # loop through smoothed timeseries to see if drifter has run aground
        i = 0
        is_aground = False  # keeps track of whether drifter is deemed aground
        i_aground = np.nan  # keeps track of index when drifter first ran aground
        time_to_end = self.hrs_smooth[-1] - self.hrs_smooth[i]
        while time_to_end >= min_win_period_hours:

            displace = sphere_distance(
                self.lat_smooth[i],
                self.lon_smooth[i],
                self.lat_smooth[-1],
                self.lon_smooth[-1],
            )
            if displace <= NewAgroundChecker.tolerance:
                if is_aground:
                    i += 1
                    time_to_end = self.hrs_smooth[-1] - self.hrs_smooth[i]
                    continue
                else:
                    is_aground = True
                    i_aground = i
                    i += 1
                    time_to_end = self.hrs_smooth[-1] - self.hrs_smooth[i]
            else:
                is_aground = False
                i_aground = np.nan
                i += 1
                time_to_end = self.hrs_smooth[-1] - self.hrs_smooth[i]

                # set flags
        if is_aground:
            if i_aground > 0:
                i_aground += half_win
            # this gets the first index the drifter is deemed aground for the original (un-smoothed) timeseries
            # n.b. if i_aground=0 then the entire drifter record is deemed aground and flagged as such
        for ind, rep in enumerate(self.reps):
            if is_aground:
                if ind < i_aground:
                    rep.set_qc("POS", "drf_agr", 0)
                else:
                    rep.set_qc("POS", "drf_agr", 1)
            else:
                rep.set_qc("POS", "drf_agr", 0)


def do_sst_tail_check(reps, *args):
    warnings.warn(
        DeprecationWarning(
            "This module trackqc is deprecated, use next_level_trackqc instead"
        )
    )
    checker = SSTTailChecker(reps)
    if args:
        checker.set_parameters(*args)
    checker.do_qc()


class SSTTailChecker:
    """Check to see whether there is erroneous sea surface temperature data at the beginning or end of a drifter record
    (referred to as 'tails'). The flags 'drf_tail1' and 'drf_tail2' are set for each input report: flag=1 for reports
    with erroneous data, else flag=0, 'drf_tail1' is used for bad data at the beginning of a record, 'drf_tail2' is
    used for bad data at the end of a record.

    The tail check makes an assessment of the quality of data at the start and end of a drifting buoy record by
    comparing to a background reference field. Data found to be unacceptably biased or noisy relative to the
    background are flagged by the check. When making the comparison an allowance is made for background error
    variance and also normal drifter error (both bias and random measurement error). The correlation of the
    background error is treated as unknown and takes on a value which maximises background error dependent on the
    assessment being made. A background error variance limit is also specified, beyond which the background is deemed
    unreliable. Observations made during the day, in icy regions or where the background value is missing are
    excluded from the comparison.

    The check proceeds in two steps; a 'long tail-check' followed by a 'short tail-check'. The idea is that the short
    tail-check has finer resolution but lower sensitivity than the long tail-check and may pick off noisy data not
    picked up by the long tail check. Only observations that pass the long tail-check are passed to the short
    tail-check. Both of these tail checks proceed by moving a window over the data and assessing the data in each
    window. Once good data are found the check stops and any bad data preceding this are flagged. If unreliable
    background data are encountered the check stops. The checks are run forwards and backwards over the record so as
    to assess data at the start and end of the record. If the whole record fails no observations are flagged as there
    are then no 'tails' in the data (this is left for other checks). The long tail check looks for groups of
    observations that are too biased or noisy as a whole. The short tail check looks for individual observations
    exceeding a noise limit within the window.

    long_win_len: int
        Length of window (in data-points) over which to make long tail-check (must be an odd number)
    long_err_std_n: float
        Number of standard deviations of combined background and drifter bias error, beyond which
        data fail bias check
    short_win_len: int
        Length of window (in data-points) over which to make the short tail-check
    short_err_std_n: float
        Number of standard deviations of combined background and drifter error, beyond which data
        are deemed suspicious
    short_win_n_bad: int
        Minimum number of suspicious data points required for failure of short check window
    drif_inter: float
        spread of biases expected in drifter data (standard deviation, degC)
    drif_intra: float
        Maximum random measurement uncertainty reasonably expected in drifter data (standard deviation, degC)
    background_err_lim: float
        Background error variance beyond which the SST background is deemed unreliable (degC squared)
    """

    long_win_len = 121
    long_err_std_n = 3.0
    short_win_len = 30
    short_err_std_n = 3.0
    short_win_n_bad = 2
    drif_inter = 0.29
    drif_intra = 1.00
    background_err_lim = 0.3

    def __init__(self, reps):
        self.reps = reps
        self.reps_ind = None
        self.sst_anom = None
        self.bgerr = None

        self.start_tail_ind = None
        self.end_tail_ind = None

    def set_parameters(
        self,
        long_win_len: int,
        long_err_std_n: float,
        short_win_len: int,
        short_err_std_n: float,
        short_win_n_bad: int,
        drif_inter: float,
        drif_intra: float,
        background_err_lim: float,
    ) -> None:
        """Set the parameters of the QC check. Note that this will set parameters for all instances of the class.

        Parameters
        ----------
        long_win_len: int
            Length of window (in data-points) over which to make long tail-check (must be an odd number)
        long_err_std_n: float
            Number of standard deviations of combined background and drifter bias error, beyond which
            data fail bias check
        short_win_len: int
            Length of window (in data-points) over which to make the short tail-check
        short_err_std_n: float
            Number of standard deviations of combined background and drifter error, beyond which data
            are deemed suspicious
        short_win_n_bad: int
            Minimum number of suspicious data points required for failure of short check window
        drif_inter: float
            spread of biases expected in drifter data (standard deviation, degC)
        drif_intra: float
            Maximum random measurement uncertainty reasonably expected in drifter data (standard deviation, degC)
        background_err_lim: float
            Background error variance beyond which the SST background is deemed unreliable (degC squared)

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            When any of the input values are invalid.
        """
        try:
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
        except AssertionError as error:
            raise AssertionError("invalid input parameter: " + str(error))

        SSTTailChecker.long_win_len = long_win_len
        SSTTailChecker.long_err_std_n = long_err_std_n
        SSTTailChecker.short_win_len = short_win_len
        SSTTailChecker.short_err_std_n = short_err_std_n
        SSTTailChecker.short_win_n_bad = short_win_n_bad
        SSTTailChecker.drif_inter = drif_inter
        SSTTailChecker.drif_intra = drif_intra
        SSTTailChecker.background_err_lim = background_err_lim

    def do_qc(self):
        self._preprocess_reps()
        self._initialise_reps()
        if len(self.sst_anom) == 0:
            return

        nrep = len(self.sst_anom)
        self.start_tail_ind = -1  # keeps track of index where start tail stops
        self.end_tail_ind = nrep  # keeps track of index where end tail starts

        # do long tail check - records shorter than long-window length aren't evaluated
        if not (nrep < SSTTailChecker.long_win_len):
            # run forwards then backwards over timeseries
            self._do_long_tail_check(forward=True)
            self._do_long_tail_check(forward=False)

        # do short tail check on records that pass long tail check - whole record already failed long tail check
        if not (self.start_tail_ind >= self.end_tail_ind):
            first_pass_ind = (
                self.start_tail_ind + 1
            )  # first index passing long tail check
            last_pass_ind = self.end_tail_ind - 1  # last index passing long tail check
            self._do_short_tail_check(first_pass_ind, last_pass_ind, forward=True)
            self._do_short_tail_check(first_pass_ind, last_pass_ind, forward=False)

        # now flag reps - whole record failed tail checks, don't flag
        if self.start_tail_ind >= self.end_tail_ind:
            self.start_tail_ind = -1
            self.end_tail_ind = nrep

        if not self.start_tail_ind == -1:
            for ind, rep in enumerate(self.reps):
                if ind <= self.reps_ind[self.start_tail_ind]:
                    rep.set_qc("SST", "drf_tail1", 1)
        if not self.end_tail_ind == nrep:
            for ind, rep in enumerate(self.reps):
                if ind >= self.reps_ind[self.end_tail_ind]:
                    rep.set_qc("SST", "drf_tail2", 1)

    def _initialise_reps(self) -> None:
        """Initialise the QC flags in the reports"""
        # set start and end tail flags to pass to ensure all obs receive flag
        # then exit if there are no obs suitable for assessment
        for rep in self.reps:
            rep.set_qc("SST", "drf_tail1", 0)
            rep.set_qc("SST", "drf_tail2", 0)
        if len(self.sst_anom) == 0:
            return

    @staticmethod
    def _parse_rep(rep) -> (float, float, float, bool):
        """Process a report

        Parameters
        ----------
        rep: MarineReport
            MarineReport from which the information is to be extracted

        Returns
        -------
        (float, float, float, bool)
            Background value, ice concentration, background variance, and a boolean variable indicating whether the
            report is "good"
        """
        bg_val = rep.getext("OSTIA")  # raises assertion error if not found
        ice_val = rep.getext("ICE")  # raises assertion error if not found
        bgvar_val = rep.getext("BGVAR")  # raises assertion error if not found

        if ice_val is None:
            ice_val = 0.0
        assert (
            ice_val is not None and 0.0 <= ice_val <= 1.0
        ), "matched ice proportion is invalid"

        daytime = track_day_test(
            rep.getvar("YR"),
            rep.getvar("MO"),
            rep.getvar("DY"),
            rep.getvar("HR"),
            rep.getvar("LAT"),
            rep.getvar("LON"),
            -2.5,
        )

        try:
            # raises assertion error if 'time_diff' not found
            time_diff = rep.getext("time_diff")
            if time_diff is not None:
                assert time_diff >= 0, "times are not sorted"
        except AssertionError as error:
            raise AssertionError("problem with report value: " + str(error))

        land_match = bg_val is None
        ice_match = ice_val > 0.15

        good_match = not (daytime or land_match or ice_match)

        return bg_val, ice_val, bgvar_val, good_match

    def _preprocess_reps(self) -> None:
        """Process the reps and calculate the values used in the QC check"""
        # test and filter out obs with unsuitable background matches
        reps_ind = []  # type: list
        sst_anom = []  # type: list
        bgvar = []  # type: list
        for ind, rep in enumerate(self.reps):
            bg_val, ice_val, bgvar_val, good_match = SSTTailChecker._parse_rep(rep)

            if good_match:
                assert (
                    bg_val is not None and -5.0 <= bg_val <= 45.0
                ), "matched background sst is invalid"
                assert (
                    bgvar_val is not None and 0.0 <= bgvar_val <= 10
                ), "matched background error variance is invalid"
                reps_ind.append(ind)
                sst_anom.append(rep.getvar("SST") - bg_val)
                bgvar.append(bgvar_val)

        # prepare numpy arrays and variables needed for tail checks
        # indices of obs suitable for assessment
        self.reps_ind = np.array(reps_ind)  # type: np.ndarray
        # ob-background differences
        self.sst_anom = np.array(sst_anom)  # type: np.ndarray
        # standard deviation of background error
        self.bgerr = np.sqrt(np.array(bgvar))  # type: np.ndarray

    def _do_long_tail_check(self, forward: bool = True) -> None:
        """Perform the long tail check

        Parameters
        ----------
        forward: bool
            Flag to set for a forward (True) or backward (False) pass of the long tail check

        Returns
        -------
        None
        """
        nrep = len(self.sst_anom)
        mid_win_ind = int((SSTTailChecker.long_win_len - 1) / 2)

        if forward:
            sst_anom_temp = self.sst_anom
            bgerr_temp = self.bgerr
        else:
            sst_anom_temp = np.flipud(self.sst_anom)
            bgerr_temp = np.flipud(self.bgerr)

        # this is the long tail check
        for ix in range(0, nrep - SSTTailChecker.long_win_len + 1):
            sst_anom_winvals = sst_anom_temp[ix : ix + SSTTailChecker.long_win_len]
            bgerr_winvals = bgerr_temp[ix : ix + SSTTailChecker.long_win_len]
            if np.any(bgerr_winvals > np.sqrt(SSTTailChecker.background_err_lim)):
                break
            sst_anom_avg = trim_mean(sst_anom_winvals, 100)
            sst_anom_stdev = trim_std(sst_anom_winvals, 100)
            bgerr_avg = np.mean(bgerr_winvals)
            bgerr_rms = np.sqrt(np.mean(bgerr_winvals**2))
            if (
                abs(sst_anom_avg)
                > SSTTailChecker.long_err_std_n
                * np.sqrt(SSTTailChecker.drif_inter**2 + bgerr_avg**2)
            ) or (
                sst_anom_stdev > np.sqrt(SSTTailChecker.drif_intra**2 + bgerr_rms**2)
            ):
                if forward:
                    self.start_tail_ind = ix + mid_win_ind
                else:
                    self.end_tail_ind = (nrep - 1) - ix - mid_win_ind
            else:
                break

    def _do_short_tail_check(self, first_pass_ind, last_pass_ind, forward=True):
        """Perform the short tail check

        Parameters
        ----------
        first_pass_ind: int
            Index
        last_pass_ind: int
            Index
        forward: bool
            Flag to set for a forward (True) or backward (False) pass of the short tail check

        Returns
        -------
        None
        """
        npass = last_pass_ind - first_pass_ind + 1
        assert npass > 0, "short tail check: npass not > 0"

        # records shorter than short-window length aren't evaluated
        if npass < SSTTailChecker.short_win_len:
            return

        if forward:
            sst_anom_temp = self.sst_anom[first_pass_ind : last_pass_ind + 1]
            bgerr_temp = self.bgerr[first_pass_ind : last_pass_ind + 1]
        else:
            sst_anom_temp = np.flipud(self.sst_anom[first_pass_ind : last_pass_ind + 1])
            bgerr_temp = np.flipud(self.bgerr[first_pass_ind : last_pass_ind + 1])

        # this is the short tail check
        for ix in range(0, npass - SSTTailChecker.short_win_len + 1):
            sst_anom_winvals = sst_anom_temp[ix : ix + SSTTailChecker.short_win_len]
            bgerr_winvals = bgerr_temp[ix : ix + SSTTailChecker.short_win_len]
            if np.any(bgerr_winvals > np.sqrt(SSTTailChecker.background_err_lim)):
                break
            limit = SSTTailChecker.short_err_std_n * np.sqrt(
                bgerr_winvals**2
                + SSTTailChecker.drif_inter**2
                + SSTTailChecker.drif_intra**2
            )
            exceed_limit = np.logical_or(
                sst_anom_winvals > limit, sst_anom_winvals < -limit
            )
            if np.sum(exceed_limit) >= SSTTailChecker.short_win_n_bad:
                if forward:
                    # if all windows have failed, flag everything
                    if ix == npass - SSTTailChecker.short_win_len:
                        self.start_tail_ind += SSTTailChecker.short_win_len
                    else:
                        self.start_tail_ind += 1
                else:
                    # if all windows have failed, flag everything
                    if ix == npass - SSTTailChecker.short_win_len:
                        self.end_tail_ind -= SSTTailChecker.short_win_len
                    else:
                        self.end_tail_ind -= 1
            else:
                break


def do_sst_biased_noisy_check(reps, *args):
    warnings.warn(
        DeprecationWarning(
            "This module trackqc is deprecated, use next_level_trackqc instead"
        )
    )
    checker = SSTBiasedNoisyChecker(reps)
    if args:
        checker.set_parameters(*args)
    checker.do_qc()


class SSTBiasedNoisyChecker:
    """Check to see whether a drifter sea surface temperature record is unacceptably biased or noisy as a whole.

    The check makes an assessment of the quality of data in a drifting buoy record by comparing to a background
    reference field. If the record is found to be unacceptably biased or noisy relative to the background all
    observations are flagged by the check. For longer records the flags 'drf_bias' and 'drf_noise' are set for each
    input report: flag=1 for records with erroneous data, else flag=0. For shorter records 'drf_short' is set for
    each input report: flag=1 for reports with erroneous data, else flag=0.

    When making the comparison an allowance is made for background error variance and also normal drifter error (both
    bias and random measurement error). A background error variance limit is also specified, beyond which the
    background is deemed unreliable and is excluded from comparison. Observations made during the day, in icy regions
    or where the background value is missing are also excluded from the comparison.

    The check has two separate streams; a 'long-record check' and a 'short-record check'. Records with at least
    n_eval observations are passed to the long-record check, else they are passed to the short-record check. The
    long-record check looks for records that are too biased or noisy as a whole. The short record check looks for
    individual observations exceeding a noise limit within a record. The purpose of n_eval is to ensure records with
    too few observations for their bias and noise to be reliably estimated are handled separately by the short-record
    check.

    The correlation of the background error is treated as unknown and handled differently for each assessment. For
    the long-record noise-check and the short-record check the background error is treated as uncorrelated,
    which maximises the possible impact of background error on these assessments. For the long-record bias-check a
    limit (bias_lim) is specified beyond which the record is considered biased. The default value for this limit was
    chosen based on histograms of drifter-background bias. An alternative approach would be to treat the background
    error as entirely correlated across a long-record, which maximises its possible impact on the bias assessment. In
    this case the histogram approach was used as the limit could be tuned to give better results.

    The following class attributes are set and can be modified using the set_parameter method

    n_eval: int
        the minimum number of drifter observations required to be assessed by the long-record check
    bias_lim: float
        maximum allowable drifter-background bias, beyond which a record is considered biased (degC)
    drif_intra: float
        maximum random measurement uncertainty reasonably expected in drifter data (standard
        deviation, degC)
    drif_inter: float
        spread of biases expected in drifter data (standard deviation, degC)
    err_std_n: float
        number of standard deviations of combined background and drifter error, beyond which
        short-record data are deemed suspicious
    n_bad: int
        minimum number of suspicious data points required for failure of short-record check
    background_err_lim: float
        background error variance beyond which the SST background is deemed unreliable (degC squared)
    """

    n_eval = 30
    bias_lim = 1.10
    drif_intra = 1.0
    drif_inter = 0.29
    err_std_n = 3.0
    n_bad = 2
    background_err_lim = 0.3

    def __init__(self, reps):
        self.reps = reps
        self.sst_anom = None
        self.bgerr = None
        self.bgvar_is_masked = None

    def set_parameters(
        self,
        n_eval: int,
        bias_lim: float,
        drif_intra: float,
        drif_inter: float,
        err_std_n: float,
        n_bad: int,
        background_err_lim: float,
    ) -> None:
        """Set the parameters of the QC check. Note that this will set parameters for all instances of the class.

        Parameters
        ----------
        n_eval: int
            the minimum number of drifter observations required to be assessed by the long-record check
        bias_lim: float
            maximum allowable drifter-background bias, beyond which a record is considered biased (degC)
        drif_intra: float
            maximum random measurement uncertainty reasonably expected in drifter data (standard
            deviation, degC)
        drif_inter: float
            spread of biases expected in drifter data (standard deviation, degC)
        err_std_n: float
            number of standard deviations of combined background and drifter error, beyond which
            short-record data are deemed suspicious
        n_bad: int
            minimum number of suspicious data points required for failure of short-record check
        background_err_lim: float
            background error variance beyond which the SST background is deemed unreliable (degC squared)

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            When any of the parameters is invalid
        """
        assert n_eval > 0, "n_eval must be > 0"
        assert bias_lim >= 0, "bias_lim must be >= 0"
        assert drif_intra >= 0, "drif_intra must be >= 0"
        assert drif_inter >= 0, "drif_inter must be >= 0"
        assert err_std_n >= 0, "err_std_n must be >= 0"
        assert n_bad >= 1, "n_bad must be >= 1"
        assert background_err_lim >= 0, "background_err_lim must be >= 0"

        SSTBiasedNoisyChecker.n_eval = n_eval
        SSTBiasedNoisyChecker.bias_lim = bias_lim
        SSTBiasedNoisyChecker.drif_intra = drif_intra
        SSTBiasedNoisyChecker.drif_inter = drif_inter
        SSTBiasedNoisyChecker.err_std_n = err_std_n
        SSTBiasedNoisyChecker.n_bad = n_bad
        SSTBiasedNoisyChecker.background_err_lim = background_err_lim

    def do_qc(self):
        """Perform the bias/noise check QC"""
        self._preprocess_reps()
        self._initialise_flags()

        long_record = not (len(self.sst_anom) < SSTBiasedNoisyChecker.n_eval)

        if long_record:
            self._long_record_qc()
        else:
            if not self.bgvar_is_masked:
                self._short_record_qc()

    @staticmethod
    def _parse_rep(rep) -> (float, float, float, bool, bool):
        """
        Extract QC-relevant variables from a marine report and

        Parameters
        ----------
        rep: MarineRepor
            Marine report. Must have variables OSTIA, ICE and BGVAR

        Returns
        -------
        float, float, float, bool, bool
            Returns the background SST value, ice value, background SST variance, a flag that indicates a good match,
            and a flag that indicates if the background variance is valid.

        Raises
        ------
        AssertionError
            When bad values are identified
        """
        bg_val = rep.getext("OSTIA")
        ice_val = rep.getext("ICE")
        bgvar_val = rep.getext("BGVAR")

        if ice_val is None:
            ice_val = 0.0
        assert (
            ice_val is not None and 0.0 <= ice_val <= 1.0
        ), "matched ice proportion is invalid"

        daytime = track_day_test(
            rep.getvar("YR"),
            rep.getvar("MO"),
            rep.getvar("DY"),
            rep.getvar("HR"),
            rep.getvar("LAT"),
            rep.getvar("LON"),
            -2.5,
        )

        try:
            # raises assertion error if 'time_diff' not found
            time_diff = rep.getext("time_diff")
            if time_diff is not None:
                assert time_diff >= 0, "times are not sorted"
        except AssertionError as error:
            raise AssertionError("problem with report value: " + str(error))

        land_match = bg_val is None
        ice_match = ice_val > 0.15
        bgvar_mask = (
            bgvar_val is not None
            and bgvar_val > SSTBiasedNoisyChecker.background_err_lim
        )

        good_match = not (daytime or land_match or ice_match or bgvar_mask)

        return bg_val, ice_val, bgvar_val, good_match, bgvar_mask

    def _preprocess_reps(self) -> None:
        """
        Fill SST anomalies and background errors used in the QC checks, as well as a flag
        indicating missing or invalid background values.
        """
        # test and filter out obs with unsuitable background matches
        sst_anom = []
        bgvar = []
        bgvar_is_masked = False

        for rep in self.reps:
            bg_val, ice_val, bgvar_val, good_match, bgvar_mask = (
                SSTBiasedNoisyChecker._parse_rep(rep)
            )

            if bgvar_mask:
                bgvar_is_masked = True

            if good_match:
                assert (
                    bg_val is not None and -5.0 <= bg_val <= 45.0
                ), "matched background sst is invalid"
                assert (
                    bgvar_val is not None and 0.0 <= bgvar_val <= 10
                ), "matched background error variance is invalid"
                sst_anom.append(rep.getvar("SST") - bg_val)
                bgvar.append(bgvar_val)

        # prepare numpy arrays and variables needed for checks
        sst_anom = np.array(sst_anom)  # ob-background differences
        bgerr = np.sqrt(np.array(bgvar))  # standard deviation of background error

        self.sst_anom = sst_anom
        self.bgerr = bgerr
        self.bgvar_is_masked = bgvar_is_masked

    def _initialise_flags(self):
        """Initialise the QC flags in the reports"""
        for rep in self.reps:
            rep.set_qc("SST", "drf_bias", 0)
            rep.set_qc("SST", "drf_noise", 0)
            rep.set_qc("SST", "drf_short", 0)

    def _long_record_qc(self) -> None:
        """Perform the long record check"""
        sst_anom_avg = np.mean(self.sst_anom)
        sst_anom_stdev = np.std(self.sst_anom)
        bgerr_rms = np.sqrt(np.mean(self.bgerr**2))

        if abs(sst_anom_avg) > SSTBiasedNoisyChecker.bias_lim:
            for rep in self.reps:
                rep.set_qc("SST", "drf_bias", 1)

        if sst_anom_stdev > np.sqrt(SSTBiasedNoisyChecker.drif_intra**2 + bgerr_rms**2):
            for rep in self.reps:
                rep.set_qc("SST", "drf_noise", 1)

    def _short_record_qc(self) -> None:
        """Perform the short record check"""
        # Calculate the limit based on the combined uncertainties (background error, drifter inter and drifter intra
        # error) and then multiply by the err_std_n
        limit = SSTBiasedNoisyChecker.err_std_n * np.sqrt(
            self.bgerr**2
            + SSTBiasedNoisyChecker.drif_inter**2
            + SSTBiasedNoisyChecker.drif_intra**2
        )

        # If the number of obs outside the limit exceed n_bad then flag them all as bad
        exceed_limit = np.logical_or(self.sst_anom > limit, self.sst_anom < -limit)
        if np.sum(exceed_limit) >= SSTBiasedNoisyChecker.n_bad:
            for rep in self.reps:
                rep.set_qc("SST", "drf_short", 1)
