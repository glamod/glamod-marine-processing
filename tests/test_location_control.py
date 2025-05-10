from __future__ import annotations

import math

import pytest

from glamod_marine_processing.qc_suite.modules.location_control import *


def test_0_is_89point5():
    assert yindex_to_lat(0, 1) == 89.5


def test_179_is_minus89point5():
    assert yindex_to_lat(179, 1) == -89.5


def test_35_is_minus87point5_atresof5():
    assert yindex_to_lat(35, 5) == -87.5


def test_0_is_87point5_atresof5():
    assert yindex_to_lat(0, 5) == 87.5


def test_lats_with_res():
    assert mds_lat_to_yindex(90.0, 5.0) == 0
    assert mds_lat_to_yindex(88.0, 5.0) == 0
    assert mds_lat_to_yindex(85.0, 5.0) == 0
    assert mds_lat_to_yindex(-85.0, 5.0) == 35
    assert mds_lat_to_yindex(-88.4, 5.0) == 35
    assert mds_lat_to_yindex(-90.0, 5.0) == 35
    assert mds_lat_to_yindex(0.0, 5.0) == 18


def test_lons_with_res():
    assert mds_lon_to_xindex(-180.0, 5.0) == 0
    assert mds_lon_to_xindex(-178.0, 5.0) == 0
    assert mds_lon_to_xindex(-175.0, 5.0) == 0

    assert mds_lon_to_xindex(175.0, 5.0) == 71
    assert mds_lon_to_xindex(178.4, 5.0) == 71
    assert mds_lon_to_xindex(180.0, 5.0) == 71

    assert mds_lon_to_xindex(0.0, 5.0) == 35


def test_lats():
    assert mds_lat_to_yindex(90.0) == 0
    assert mds_lat_to_yindex(89.0) == 0
    assert mds_lat_to_yindex(88.0) == 1
    assert mds_lat_to_yindex(87.0) == 2

    assert mds_lat_to_yindex(88.7) == 1

    assert mds_lat_to_yindex(-90.0) == 179
    assert mds_lat_to_yindex(-89.0) == 179
    assert mds_lat_to_yindex(-88.0) == 178
    assert mds_lat_to_yindex(-87.0) == 177

    assert mds_lat_to_yindex(-88.7) == 178

    assert mds_lat_to_yindex(0.0) == 90
    assert mds_lat_to_yindex(0.5) == 89
    assert mds_lat_to_yindex(1.0) == 88
    assert mds_lat_to_yindex(-0.5) == 90
    assert mds_lat_to_yindex(-1.0) == 91


def test_lons():
    assert mds_lon_to_xindex(-180.0) == 0
    assert mds_lon_to_xindex(-179.0) == 0
    assert mds_lon_to_xindex(-178.0) == 1

    assert mds_lon_to_xindex(180.0) == 359
    assert mds_lon_to_xindex(179.0) == 359
    assert mds_lon_to_xindex(178.0) == 358

    assert mds_lon_to_xindex(-1.0) == 178
    assert mds_lon_to_xindex(0.0) == 179
    assert mds_lon_to_xindex(1.0) == 181


def test_borderline():
    assert 0 == lon_to_xindex(-180)
    assert 0 == lon_to_xindex(180)


def test_high_negative_long():
    assert 359 == lon_to_xindex(-180.5)
    assert 358 == lon_to_xindex(-181.5)


def test_non180_borderline():
    assert 106 == lon_to_xindex(-74.0)


def test_gridcentres():
    assert 0 == lon_to_xindex(-179.5)
    assert 0 == lon_to_xindex(180.5)


def test_highlong():
    assert 179 == lon_to_xindex(359.5)


def test_highlong_different_res():
    assert 71 == lon_to_xindex(179.5, 5)
    assert 1439 == lon_to_xindex(179.9, 0.25)


def test_oneshift_along_at_hires():
    assert 1 == lon_to_xindex(-179.9 + 0.25, 0.25)


def test_lons_ge_180():
    """test to make sure wrapping works"""
    assert 180 == lon_to_xindex(360.0)
    assert 5 == lon_to_xindex(185.1)
    for i in range(0, 520):
        assert math.fmod(i, 360) == lon_to_xindex(-179.5 + float(i))


def test_latitude_too_high():
    assert 0 == lat_to_yindex(99.2)


def test_borderline37():
    assert 53 == lat_to_yindex(37.00)
    assert 11 == lat_to_yindex(35.00, 5)


def test_latitude_too_low():
    assert 179 == lat_to_yindex(-199.3)


def test_borderline():
    for i in range(0, 180):
        assert i == lat_to_yindex(90 - i)


def test_gridcentres():
    for i in range(0, 180):
        assert i == lat_to_yindex(90 - i - 0.5)


def test_some_points():
    assert 9 == lat_to_yindex(87.52, 0.25)
    assert 18 == lat_to_yindex(-2.5, 5)


def test_latitude_varying_res():
    assert 0 == lat_to_yindex(89.9, 0.25)
    assert 0 == lat_to_yindex(89.9, 0.5)
    assert 0 == lat_to_yindex(89.9, 1.0)
    assert 0 == lat_to_yindex(89.9, 2.0)
    assert 0 == lat_to_yindex(89.9, 5.0)

    assert 719 == lat_to_yindex(-89.9, 0.25)
    assert 359 == lat_to_yindex(-89.9, 0.5)
    assert 179 == lat_to_yindex(-89.9, 1.0)
    assert 89 == lat_to_yindex(-89.9, 2.0)
    assert 35 == lat_to_yindex(-89.9, 5.0)


def test_0():
    assert xindex_to_lon(0, 1) == -179.5


def test_359():
    assert xindex_to_lon(359, 1) == 179.5


def test_179():
    assert xindex_to_lon(179, 1) == -0.5


def test_180():
    assert xindex_to_lon(180, 1) == 0.5


def test_all_missing_in_square():
    q11, q12, q21, q22 = fill_missing_vals(None, None, None, None)
    assert q11 is None
    assert q12 is None
    assert q21 is None
    assert q22 is None


def test_one_missing_corner():
    q11, q12, q21, q22 = fill_missing_vals(1.0, 2.0, 3.0, None)
    assert q11 == 1.0
    assert q12 == 2.0
    assert q21 == 3.0
    assert q22 == 2.5


def test_two_missing_corners():
    q11, q12, q21, q22 = fill_missing_vals(None, 2.0, 3.0, None)
    assert q11 == 2.5
    assert q12 == 2.0
    assert q21 == 3.0
    assert q22 == 2.5


def test_three_missing_corners():
    q11, q12, q21, q22 = fill_missing_vals(None, None, 3.0, None)
    assert q11 == 3.0
    assert q12 == 3.0
    assert q21 == 3.0
    assert q22 == 3.0


def test_high_lon():
    x1, x2, y1, y2 = get_four_surrounding_points(0.4, 322.2 - 360, 1)
    assert x1 == -38.5
    assert x2 == -37.5
    assert y1 == -0.5
    assert y2 == 0.5


def test_high_n_lat():
    x1, x2, y1, y2 = get_four_surrounding_points(89.9, 0.1, 1)
    assert x1 == -0.5
    assert x2 == 0.5
    assert y1 == 89.5
    assert y2 == 89.5

    x1, x2, y1, y2 = get_four_surrounding_points(89.9, 0.1, 0)
    assert x1 == -0.5
    assert x2 == 0.5
    assert y1 == 89.5
    assert y2 == 90.5


def test_off_zero():
    x1, x2, y1, y2 = get_four_surrounding_points(0.1, 0.1)
    assert x1 == -0.5
    assert x2 == 0.5
    assert y1 == -0.5
    assert y2 == 0.5


def test_zero_zero():
    x1, x2, y1, y2 = get_four_surrounding_points(0.0, 0.0)
    assert x1 == -0.5
    assert x2 == 0.5
    assert y1 == -0.5
    assert y2 == 0.5


def test_dateline_crossover():
    x1, x2, y1, y2 = get_four_surrounding_points(0.0, 179.9)
    assert x1 == 179.5
    assert x2 == 180.5
    assert y1 == -0.5
    assert y2 == 0.5


def test_negative_dateline_crossover():
    x1, x2, y1, y2 = get_four_surrounding_points(0.0, -179.9)
    assert x1 == -180.5
    assert x2 == -179.5
    assert y1 == -0.5
    assert y2 == 0.5
