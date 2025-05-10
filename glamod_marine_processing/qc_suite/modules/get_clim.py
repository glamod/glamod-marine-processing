"""Get climatology fields for base QC."""

from __future__ import annotations

import numpy as np

from .interpolation import bilinear_interp
from .location_control import (
    fill_missing_vals,
    get_four_surrounding_points,
    lat_to_yindex,
    lon_to_xindex,
    mds_lat_to_yindex,
    mds_lon_to_xindex,
)
from .time_control import day_in_year, get_month_lengths, which_pentad


def get_hires_sst(lat: float, lon: float, month: int, day: int, hires_field) -> float:
    """Get a value from a high resolution ie 0.25 degree daily SST field

    Parameters
    ----------
    lat : float
        Latitude of point to extract
    lon : float
        Longitude of point to extract
    month : int
        Month of point to extract
    day : int
        Day in month of point to extract
    hires_field : ndarray(dtype=float, ndim=3)
        The field from which to extract the point

    Returns
    -------
    float
        the SST from the field at the specified point

    Raises
    ------
    ValueError
        When latitude outside range -90 to 90, longitude is outside range -180 to 360, month is outside
        range 1-12 or day is outside range 1-number of days in month
    """
    if lat < -90.0 or lat > 90.0:
        raise ValueError(f"Latitude {lat} outside range -90 to 90")
    if lon < -180.0 or lon > 360.0:
        raise ValueError(f"Longitude {lon} outside range -180 to 360")
    if month < 1 or month > 12:
        raise ValueError(f"Month ({month}) outside range 1-12")

    month_lengths = get_month_lengths(2004)
    if day < 1 or day > month_lengths[month - 1]:
        raise ValueError(f"Day ({day}) outside range 1-{month_lengths[month - 1]}")

    dindex = day_in_year(month, day) - 1
    yindex = lat_to_yindex(lat, 0.25)
    xindex = lon_to_xindex(lon, 0.25)

    result = hires_field[dindex, 0, yindex, xindex]

    if result == -999:
        result = None

    return result


def get_sst_daily(
    lat: float, lon: float, month: int, day: int, sst: np.ndarray
) -> int | float | None:
    """Get SST from pentad climatology interpolated to day.

    Parameters
    ----------
    lat : float
        Latitude of point to extract
    lon : float
        Longitude of point to extract
    month : int
        Month of point to extract
    day : int
        Day of point to extract
    sst : np.ndarray
        The field from which to extract the point

    Returns
    -------
    int or float or None
        SST value at specified location

    Raises
    ------
    ValueError
        When latitude outside range -90 to 90, longitude is outside range -180 to 360, month is outside
        range 1-12 or day is outside range 1-number of days in month
    """
    if lat < -90.0 or lat > 90.0:
        raise ValueError(f"Latitude {lat} outside range -90 to 90")
    if lon < -185.0 or lon > 365.0:
        raise ValueError(f"Longitude {lon} outside range -180 to 360")
    if month < 1 or month > 12:
        raise ValueError(f"Month ({month}) outside range 1-12")

    month_lengths = get_month_lengths(2004)
    if day < 1 or day > month_lengths[month - 1]:
        raise ValueError(f"Day ({day}) outside range 1-{month_lengths[month - 1]}")

    dindex = day_in_year(month, day) - 1
    yindex = mds_lat_to_yindex(lat)
    xindex = mds_lon_to_xindex(lon)

    result = sst[dindex, yindex, xindex]

    if type(result) is np.float64 or type(result) is np.float32:
        pass
    else:
        if result.mask:
            result = None
        else:
            result = result.data[0]

    return result


def get_sst(
    lat: float, lon: float, month: int, day: int, sst: np.ndarray
) -> int | float | None:
    """
    when given an array (sst) of appropriate type, extracts the value associated with that pentad,
    latitude and longitude.

    The structure of the SST array has to be quite specific it assumes a grid that is 360 x 180 x 73
    i.e. one year of 1degree lat x 1degree lon data split up into pentads. The west-most box is at 180degrees with
    index 0 and the northern most box also has index zero.

    Parameters
    ----------
    lat : float
        Latitude of the point
    lon : float
        Longitude of the point
    month : int
        Month of the point
    day : int
        Day of the point
    sst : ndarray(dtype=float, ndim=3)
        An array holding the 1x1x5-day gridded values

    Returns
    -------
    float
        value in array at this point

    Raises
    ------
    ValueError
        When latitude outside range -90 to 90, longitude is outside range -180 to 360, month is outside
        range 1-12 or day is outside range 1-number of days in month
    """
    if lat < -90.0 or lat > 90.0:
        raise ValueError(f"Latitude {lat} outside range -90 to 90")
    if lon < -185.0 or lon > 365.0:
        raise ValueError(f"Longitude {lon} outside range -180 to 360")
    if month < 1 or month > 12:
        raise ValueError(f"Month ({month}) outside range 1-12")
    month_lengths = get_month_lengths(2004)
    if day < 1 or day > month_lengths[month - 1]:
        raise ValueError(f"Day ({day}) outside range 1-{month_lengths[month - 1]}")

    if len(sst[:, 0, 0]) == 1:
        result = get_sst_single_field(lat, lon, sst)
    else:
        # read sst from grid
        pentad = which_pentad(month, day)
        yindex = lat_to_yindex(lat)
        xindex = lon_to_xindex(lon)

        result = sst[pentad - 1, yindex, xindex]

        # sometimes this will be a numpy array and sometimes it will
        # be a masked array. Need to identify which and
        # make sure output is appropriate
        if type(result) is np.float64 or type(result) is np.float32:
            pass
        else:
            if result.mask:
                result = None
            else:
                result = result.data[0]

    return result


def get_hires_clim(
    lat: float, lon: float, month: int, day: int, clim: np.ndarray
) -> float | None:
    """Get the climatological value for this particular observation.

    Parameters
    ----------
    lat: float
        Latitude of the point.
    lon: float
        Longitude of the point.
    month: int
        Month of the point.
    day: int
        Day of the point.
    clim: np.ndarray
        A masked array containing the climatological averages.

    Returns
    -------
    float or None
        Climatological value for a particular observation.
    """
    try:
        rep_clim = get_hires_sst(lat, lon, month, day, clim)
        return float(rep_clim)
    except Exception:
        return None


def get_clim(
    lat: float, lon: float, month: int, day: int, clim: np.ndarray
) -> float | None:
    """Get the climatological value for this particular observation.

    Parameters
    ----------
    lat: float
        Latitude of the point.
    lon: float
        Longitude of the point.
    month: int
        Month of the point.
    day: int
        Day of the point.
    clim: np.ndarray
        A masked array containing the climatological averages.

    Returns
    -------
    float or None
    """
    try:
        rep_clim = get_sst(lat, lon, month, day, clim)
        return float(rep_clim)
    except Exception:
        return


def get_sst_single_field(lat: float, lon: float, sst: np.ndarray) -> int | float | None:
    """When given an array (sst) of appropriate type, extracts the value associated with that pentad, latitude and longitude.

    The structure of the SST array has to be quite specific it assumes a grid that is 360 x 180 x 73
    i.e. one year of 1degree lat x 1degree lon data split up into pentads. The west-most box is at 180degrees with
    index 0 and the northern most box also has index zero.

    Parameters
    ----------
    lat : float
        Latitude of the point
    lon : float
        Longitude of the point
    sst : ndarray
        An array holding the 1x1x5-day gridded values

    Returns
    -------
    int or float or None
        Value in array at the specified lat lon point
    """
    assert lat >= -90.0
    assert lat <= 90.0
    assert lon >= -180.00
    assert lon <= 360.00

    # read sst from grid
    yindex = lat_to_yindex(lat)
    xindex = lon_to_xindex(lon)

    result = sst[0, yindex, xindex]

    # sometimes this will be a numpy array and sometimes it will
    # be a masked array. Need to identify which and
    # make sure output is appropriate
    if type(result) is np.float64 or type(result) is np.float32:
        pass
    else:
        if result.mask:
            result = None
        else:
            result = result.data[0]

    return result


"""It doesn't look like this routine is used"""


def get_clim_interpolated(
    lat: float, lon: float, month: int, day: int, clim: np.ndarray
) -> int | float:
    """Get climatological interpolation.

    Parameters
    ----------
    lat: float
        Latitude of the point.
    lon: float
        Longitude of the point.
    month: int
        Month of the point.
    day: int
        Day of the point.
    clim: np.ndarray
        A masked array containing the climatological averages.

    Returns
    -------
    int or float
    """
    try:
        pert1 = get_sst(lat + 0.001, lon + 0.001, month, day, clim)
    except Exception:
        pert1 = None
    try:
        pert2 = get_sst(lat + 0.001, lon - 0.001, month, day, clim)
    except Exception:
        pert2 = None
    try:
        pert3 = get_sst(lat - 0.001, lon + 0.001, month, day, clim)
    except Exception:
        pert3 = None
    try:
        pert4 = get_sst(lat - 0.001, lon - 0.001, month, day, clim)
    except Exception:
        pert4 = None
    if pert1 is None and pert2 is None and pert3 is None and pert4 is None:
        return None

    x1, x2, y1, y2 = get_four_surrounding_points(lat, lon, 1)

    try:
        q11 = get_sst(y1, x1, month, day, clim)
    except Exception:
        q11 = None
    if q11 is not None:
        q11 = float(q11)

    try:
        q22 = get_sst(y2, x2, month, day, clim)
    except Exception:
        q22 = None
    if q22 is not None:
        q22 = float(q22)

    try:
        q12 = get_sst(y2, x1, month, day, clim)
    except Exception:
        q12 = None
    if q12 is not None:
        q12 = float(q12)

    try:
        q21 = get_sst(y1, x2, month, day, clim)
    except Exception:
        q21 = None
    if q21 is not None:
        q21 = float(q21)

    q11, q12, q21, q22 = fill_missing_vals(q11, q12, q21, q22)

    x1, x2, y1, y2 = get_four_surrounding_points(lat, lon, 0)

    return bilinear_interp(x1, x2, y1, y2, lon, lat, q11, q12, q21, q22)
