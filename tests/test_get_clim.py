from __future__ import annotations

import itertools

import numpy as np
import numpy.ma as ma
import pytest

from glamod_marine_processing.qc_suite.modules.get_clim import (
    fill_missing_vals,
    get_four_surrounding_points,
    get_hires_sst,
    get_sst,
    get_sst_daily,
    get_sst_single_field,
)


@pytest.mark.parametrize(
    "q11, q12, q21, q22, expected",
    [
        (None, None, None, None, (None, None, None, None)),
        (1.0, 2.0, 3.0, None, (1.0, 2.0, 3.0, 2.5)),
        (None, 2.0, 3.0, None, (2.5, 2.0, 3.0, 2.5)),
        (None, None, 3.0, None, (3.0, 3.0, 3.0, 3.0)),
    ],
)
def test_fill_missing_values(q11, q12, q21, q22, expected):
    assert fill_missing_vals(q11, q12, q21, q22) == expected


@pytest.mark.parametrize(
    "lat, lon, max90, expected",
    [
        (0.4, 322.2 - 360, 1, (-38.5, -37.5, -0.5, 0.5)),
        (89.9, 0.1, 1, (-0.5, 0.5, 89.5, 89.5)),
        (89.9, 0.1, 0, (-0.5, 0.5, 89.5, 90.5)),
        (0.1, 0.1, 1, (-0.5, 0.5, -0.5, 0.5)),
        (0.0, 0.0, 1, (-0.5, 0.5, -0.5, 0.5)),
        (0.0, 179.9, 1, (179.5, 180.5, -0.5, 0.5)),
        (0.0, -179.9, 1, (-180.5, -179.5, -0.5, 0.5)),
    ],
)
def test_get_four_surrounding_points(lat, lon, max90, expected):
    assert get_four_surrounding_points(lat, lon, max90) == expected


@pytest.fixture
def hires_field():
    outfield = np.zeros((365, 1, 180 * 4, 360 * 4))
    outfield[:, :, -1, :] = -999
    return outfield


@pytest.mark.parametrize(
    "lat, lon, month, day, expected",
    [
        (-89.9, -179.9, 1, 1, None),
        (89.89, -179.9, 1, 1, 0),
        (89.89, -179.9 + 0.25, 1, 1, 0),
        (89.89, 179.9, 1, 1, 0),
    ],
)
def test_get_hires_sst(lat, lon, month, day, expected, hires_field):
    assert get_hires_sst(lat, lon, month, day, hires_field) == expected


@pytest.fixture
def midres_field_masked():
    outfield = np.zeros((365, 180, 360)) + 5.1
    outfield = outfield.view(ma.MaskedArray)
    outfield[:, 179, :] = ma.masked  # Emulate Antarctica having missing data
    return outfield


@pytest.mark.parametrize(
    "lat, lon, month, day, expected",
    [
        (-89.9, -179.9, 1, 1, None),
        (89.89, -179.9, 1, 1, 5.1),
        (89.89, 179.9, 1, 1, 5.1),
    ],
)
def test_get_sst_daily(lat, lon, month, day, expected, midres_field_masked):
    assert get_sst_daily(lat, lon, month, day, midres_field_masked) == expected


@pytest.fixture
def pentad_field():
    """Construct a 1x1xpentad grid with entries equal to pentad + latitude/100."""
    outfield = np.zeros((73, 180, 360))
    for pp, yy in itertools.product(range(73), range(180)):
        outfield[pp, yy, :] = pp + (89.5 - yy) / 100.0
    return outfield


@pytest.fixture
def single_field():
    """Construct a 1x1xpentad grid with entries equal to pentad + latitude/100."""
    outfield = np.zeros((1, 180, 360))
    for pp, yy in itertools.product(range(1), range(180)):
        outfield[pp, yy, :] = pp + (89.5 - yy) / 100.0
    return outfield


@pytest.mark.parametrize(
    "lat, lon, month, day, expected",
    [
        (89.9, 0.0, 12, 31, 72 + 0.895),
        (89.9, 0.0, 1, 1, 0 + 0.895),
        (-9.5, -179.5, 1, 1, 0 - 0.095),
        (-10.5, -179.5, 12, 31, 72 - 0.105),
        (89.9, 0.0, 1, 1, 0 + 0.895),
        (89.9, 0.0, 1, 1, 0 + 0.895),
        (0.5, -179.5, 1, 1, 0 + 0.005),
        (-0.5, -179.5, 1, 1, 0 - 0.005),
        (0.5, -179.5, 1, 1, 0 + 0.005),
        (-0.5, -179.5, 1, 1, 0 - 0.005),
        (-89.9, 0.0, 1, 1, 0 - 0.895),
        (0, 0, 1, 1, 0 - 0.005),
    ],
)
def test_get_sst(lat, lon, month, day, expected, pentad_field):
    assert get_sst(lat, lon, month, day, pentad_field) == expected


@pytest.mark.parametrize(
    "lat, lon, month, day, expected",
    [
        (89.9, 0.0, 12, 31, 0 + 0.895),
        (89.9, 0.0, 1, 1, 0 + 0.895),
        (-9.5, -179.5, 1, 1, 0 - 0.095),
        (-10.5, -179.5, 12, 31, 0 - 0.105),
        (89.9, 0.0, 1, 1, 0 + 0.895),
        (89.9, 0.0, 1, 1, 0 + 0.895),
        (0.5, -179.5, 1, 1, 0 + 0.005),
        (-0.5, -179.5, 1, 1, 0 - 0.005),
        (0.5, -179.5, 1, 1, 0 + 0.005),
        (-0.5, -179.5, 1, 1, 0 - 0.005),
        (-89.9, 0.0, 1, 1, 0 - 0.895),
        (0, 0, 1, 1, 0 - 0.005),
    ],
)
def test_get_sst_with_single_field(lat, lon, month, day, expected, single_field):
    assert get_sst(lat, lon, month, day, single_field) == expected


@pytest.mark.parametrize(
    "lat, lon, expected",
    [
        (89.9, 0.0, 0 + 0.895),
        (89.9, 0.0, 0 + 0.895),
        (-9.5, -179.5, 0 - 0.095),
        (-10.5, -179.5, 0 - 0.105),
        (89.9, 0.0, 0 + 0.895),
        (89.9, 0.0, 0 + 0.895),
        (0.5, -179.5, 0 + 0.005),
        (-0.5, -179.5, 0 - 0.005),
        (0.5, -179.5, 0 + 0.005),
        (-0.5, -179.5, 0 - 0.005),
        (-89.9, 0.0, 0 - 0.895),
        (0, 0, 0 - 0.005),
    ],
)
def test_get_sst_single_field(lat, lon, expected, single_field):
    assert get_sst_single_field(lat, lon, single_field) == expected
