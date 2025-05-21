"""Some generally helpful location control functions for base QC."""

from __future__ import annotations

from .statistics import missing_mean


def yindex_to_lat(yindex: int, res: float = 1.0) -> float:
    """Convert yindex to latitude.

    Parameters
    ----------
    yindex: int
    res: float, default: 1.0

    Returns
    -------
    float
        Latitude (degrees).
    """
    assert yindex >= 0
    assert yindex < 180 / res
    return 90.0 - yindex * res - res / 2.0


def mds_lat_to_yindex(lat: float, res: float = 1.0) -> int:
    """For a given latitude return the y-index as it was in MDS2/3 in a 1x1 global grid.

    Parameters
    ----------
    lat: float
        Latitude of the point.
    res: float, default: 1.0
        Resolution of grid in degrees.

    Returns
    -------
    int
        Grid box index.

    Note
    ----
    In the northern hemisphere, borderline latitudes which fall on grid boundaries are pushed north, except
    90 which goes south. In the southern hemisphere, they are pushed south, except -90 which goes north.
    At 0 degrees they are pushed south.

    Expects that latitudes run from 90N to 90S
    """
    lat_local = lat  # round(lat,1)

    if lat_local == -90:
        lat_local += 0.001
    if lat_local == 90:
        lat_local -= 0.001

    if lat > 0.0:
        return int(90 / res - 1 - int(lat_local / res))
    return int(90 / res - int(lat_local / res))


def lat_to_yindex(lat: float, res: float = 1.0) -> int:
    """For a given latitude return the y index in a 1x1x5-day global grid.

    Parameters
    ----------
    lat: float
        Latitude of the point.
    res: float, default: 1.0
        Resolution of the grid.

    Returns
    -------
    int
        Grid box index

    Note
    ----
    The routine assumes that the structure of the SST array is a grid that is 360 x 180 x 73
    i.e. one year of 1degree lat x 1degree lon data split up into pentads. The west-most box is at 180degrees with
    index 0 and the northern most box also has index zero. Inputs on the border between grid cells are pushed south.
    """
    if res == 1:
        yindex = int(90 - lat)
        if yindex >= 180:
            yindex = 179
        if yindex < 0:
            yindex = 0
    else:
        yindex = int((90 - lat) / res)
        if yindex >= 180 / res:
            yindex = int(180 / res - 1)
        if yindex < 0:
            yindex = 0
    return yindex


def xindex_to_lon(xindex: int, res: float = 1.0) -> float:
    """Convert xindex to longitude.

    Parameters
    ----------
    xindex: int
    res: float, default: 1.0

    Returns
    -------
    float
        Longitude (degrees).
    """
    assert xindex >= 0
    assert xindex < 360 / res
    return xindex * res - 180.0 + res / 2.0


def mds_lon_to_xindex(lon: float, res: float = 1.0) -> int:
    """For a given longitude return the x-index as it was in MDS2/3 in a 1x1 global grid.

    Parameters
    ----------
    lon: float
        Longitude of the point.
    res: float, default: 1.0
        Resolution of the field.

    Returns
    -------
    int
        Grid box index.

    Note
    ----
    In the western hemisphere, borderline longitudes which fall on grid boundaries are pushed west, except
    -180 which goes east. In the eastern hemisphere, they are pushed east, except 180 which goes west.
    At 0 degrees they are pushed west.
    """
    long_local = lon  # round(lon,1)

    if long_local == -180:
        long_local += 0.001
    if long_local == 180:
        long_local -= 0.001
    if long_local > 0.0:
        return int(int(long_local / res) + 180 / res)
    return int(int(long_local / res) + 180 / res - 1)


def lon_to_xindex(lon: float, res: float = 1.0) -> int:
    """For a given longitude return the x index in a 1x1x5-day global grid.

    Parameters
    ----------
    lon: float
        Longitude of the point.
    res: float, default: 1.0
        Resolution of the grid.


    Returns
    -------
    int
        Grid box index.

    Note
    ----
    The routine assumes that the structure of the SST array is a grid that is 360 x 180 x 73
    i.e. one year of 1degree lat x 1degree lon data split up into pentads. The west-most box is at 180degrees W with
    index 0 and the northern most box also has index zero. Inputs on the border between grid cells are pushed east.
    """
    if res == 1:
        inlon = lon
        if inlon >= 180.0:
            inlon = -180.0 + (inlon - 180.0)
        if inlon < -180.0:
            inlon = inlon + 360.0
        xindex = int(inlon + 180.0)
        while xindex >= 360:
            xindex -= 360
    else:
        inlon = lon
        if inlon >= 180.0:
            inlon = -180.0 + (inlon - 180.0)
        if inlon < -180.0:
            inlon = inlon + 360.0
        xindex = int((inlon + 180.0) / res)
        while xindex >= 360 / res:
            xindex -= 360 / res
    return int(xindex)


def fill_missing_vals(
    q11: float, q12: float, q21: float, q22: float
) -> tuple[float, float, float, float]:
    """
    For a group of four neighbouring grid boxes which form a square, with values q11, q12, q21, q22,
    fill gaps using means of neighbours.

    Parameters
    ----------
    q11 : float
        Value of first gridbox
    q12 : float
        Value of second gridbox
    q21 : float
        Value of third gridbox
    q22 : float
        Value of fourth gridbox

    Returns
    -------
    tuple of float
        A tuple of four floats representing neighbour means.
    """
    outq11 = q11
    outq12 = q12
    outq21 = q21
    outq22 = q22

    if outq11 is None:
        outq11 = missing_mean([q12, q21])
    if outq11 is None:
        outq11 = q22

    if outq22 is None:
        outq22 = missing_mean([q12, q21])
    if outq22 is None:
        outq22 = q11

    if outq12 is None:
        outq12 = missing_mean([q11, q22])
    if outq12 is None:
        outq12 = q21

    if outq21 is None:
        outq21 = missing_mean([q11, q22])
    if outq21 is None:
        outq21 = q12

    return outq11, outq12, outq21, outq22


def get_four_surrounding_points(
    lat: float, lon: float, max90: int = 1
) -> tuple[float, float, float, float]:
    """
    Get the four surrounding points of a specified latitude and longitude point.

    Parameters
    ----------
    lat : float
        Latitude of point
    lon : float
        Longitude of point
    max90 : int, default: 1
        If set to 1 then cap latitude at 90.0, if set to 0 then don't cap latitude.

    Returns
    -------
    tuple of floats
        A tuple of floats representing the longitudes of the leftmost and rightmost pairs of points,
        and the latitudes of the topmost and bottommost pairs of points.
    """
    assert -90.0 <= lat <= 90.0
    assert -180.0 <= lon <= 180.0

    x2_index = lon_to_xindex(lon + 0.5)
    x2 = xindex_to_lon(x2_index)
    if x2 < lon:
        x2 += 360.0

    x1_index = lon_to_xindex(lon - 0.5)
    x1 = xindex_to_lon(x1_index)
    if x1 > lon:
        x1 -= 360.0

    if lat + 0.5 <= 90:
        y2_index = lat_to_yindex(lat + 0.5)
        y2 = yindex_to_lat(y2_index)
    else:
        y2 = 89.5
        if max90 == 0:
            y2 = 90.5

    if lat - 0.5 >= -90:
        y1_index = lat_to_yindex(lat - 0.5)
        y1 = yindex_to_lat(y1_index)
    else:
        y1 = -89.5
        if max90 == 0:
            y1 = -90.5

    return x1, x2, y1, y2
