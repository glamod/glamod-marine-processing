"""Some generally helpful interpolation functions for base QC."""

from __future__ import annotations


def bilinear_interp(
    x1: int | float,
    x2: int | float,
    y1: int | float,
    y2: int | float,
    x: int | float,
    y: int | float,
    q11: int | float,
    q12: int | float,
    q21: int | float,
    q22: int | float,
) -> int | float:
    """
    Perform a bilinear interpolation at the point x,y from the rectangular grid
    defined by x1,y1 and x2,y2 with values at the four corners equal to Q11, Q12,
    Q21 and Q22.

    Parameters
    ----------
    x1 : int or float
        x coordinate of leftmost values
    x2 : int or float
        x coordinate of rightmost values
    y1 : int or float
        y coordinate of lower values
    y2 : int or float
        y coordinate of upper values
    x : int or float
        x coordinate of point for which interpolated value is required
    y : int or float
        y coordinate of point for which interpolated value is required
    q11 : int or float
        value in lower left grid cell
    q12 : int or float
        value in upper left grid cell
    q21 : int or float
        value in lower right grid cell
    q22 : int or float
        value in  upper right grid cell

    Returns
    -------
    int or float
       Interpolated value
    """
    if x2 < x1:
        raise ValueError("x2 not greater than x1")
    if y2 < y1:
        raise ValueError("y2 not greater than y1")
    if not (x1 <= x <= x2):
        raise ValueError("X point not between x1 and x2")
    if not (y1 <= y <= y2):
        raise ValueError("Y point not between y1 and y2")
    if q11 is None or q12 is None or q21 is None or q22 is None:
        raise ValueError("One or more data values not specified")

    val = q11 * (x2 - x) * (y2 - y)
    val += q21 * (x - x1) * (y2 - y)
    val += q12 * (x2 - x) * (y - y1)
    val += q22 * (x - x1) * (y - y1)
    val /= (x2 - x1) * (y2 - y1)

    assert val <= 0.0001 + max([q11, q12, q21, q22]), (
        str(val) + " " + str(q11) + " " + str(q12) + " " + str(q21) + " " + str(q22)
    )
    assert val >= -0.0001 + min([q11, q12, q21, q22]), (
        str(val) + " " + str(q11) + " " + str(q12) + " " + str(q21) + " " + str(q22)
    )
    return val
