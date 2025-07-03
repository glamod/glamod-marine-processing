from __future__ import annotations

import math

import numpy as np
import pytest

import glamod_marine_processing.qc_suite.modules.Extended_IMMA as ex
import glamod_marine_processing.qc_suite.modules.spherical_geometry as sg
from glamod_marine_processing.qc_suite.modules.auxiliary import convert_to
from glamod_marine_processing.qc_suite.modules.IMMA1 import IMMA
from glamod_marine_processing.qc_suite.modules.track_check import (
    check_distance_from_estimate,
    direction_continuity,
    distr1,
    distr2,
    increment_position,
    midpt,
    modesp,
    set_speed_limits,
    speed_continuity,
)


def test_ship_heading_north_at_60knots_goes1degree_in_1hour():
    """A ship travelling north at 60 knots will go 1 degree in 1 hours"""
    for lat in range(-90, 90):
        alat1 = lat
        alon1 = lat
        avs = convert_to(60.0, "knots", "km/h")
        ads = 0.0
        timdif = 2.0
        alat2, alon2 = increment_position(alat1, alon1, avs, ads, timdif)
        assert pytest.approx(alon2, 0.001) == 0
        assert pytest.approx(alat2, 0.001) == 1
        alat2, alon2 = increment_position(alat1, alon1, avs, ads, None)
        assert np.isnan(alat2)
        assert np.isnan(alon2)


def test_ship_heading_east_at_60knots_goes1degree_in_1hour():
    """A ship at the equator travelling east at 60 knots will go 1 degree in 1 hour"""
    alat1 = 0.0
    alat2 = 0.0
    avs = convert_to(60.0, "knots", "km/h")
    ads = 90.0
    timdif = 2.0
    aud1, avd1 = increment_position(alat1, alat2, avs, ads, timdif)
    assert pytest.approx(avd1, 0.001) == 1
    assert pytest.approx(aud1, 0.001) == 0


def test_ship_heading_east_at_60knots_at_latitude60_goes2degrees_in_1hour():
    """A ship travelling east at 60 knots will go 2 degrees in 1 hour at 60N"""
    km_to_nm = 0.539957
    alat = 60.0
    alon = 0.0
    avs = convert_to(60.0, "knots", "km/h")
    ads = 90.0
    timdif = 2.0
    dlat, dlon = increment_position(alat, alon, avs, ads, timdif)
    distance = sg.sphere_distance(alat, alon, alat + dlat, alon + dlon) * km_to_nm
    assert pytest.approx(distance, 0.0001) == 60.0


def test_ship_goes_southwest():
    alat1 = 0.0
    alat2 = 0.0
    avs = convert_to(60.0, "knots", "km/h")
    ads = 225.0
    timdif = 2.0
    aud1, avd1 = increment_position(alat1, alat2, avs, ads, timdif)
    assert pytest.approx(avd1, 0.001) == -1.0 / np.sqrt(2)
    assert pytest.approx(aud1, 0.001) == -1.0 / np.sqrt(2)


def test_noinput():
    m = modesp([])
    assert np.isnan(m)


def test_one_input():
    m = modesp([17.0])
    assert np.isnan(m)


def test_zero_index_input():
    m = modesp([-17.0, -17.0])
    assert m == convert_to(8.5, "knots", "km/h")


@pytest.mark.parametrize(
    "base_speed, expected",
    [
        (20.0, 19.5),
        (2.0, 8.5),
        (200.0, 34.5),
    ],
)
def test_modesp_single_speed_input_over8point5(base_speed, expected):
    speeds = [convert_to(base_speed, "knots", "km/h") for i in range(8)]
    m = modesp(speeds)
    assert m == convert_to(expected, "knots", "km/h")


def test_one_of_each_speed_input_min_under8point5():
    speeds = [convert_to(i, "knots", "km/h") for i in range(1, 20)]
    m = modesp(speeds)
    assert m == convert_to(8.5, "knots", "km/h")


@pytest.mark.parametrize(
    "amode, expected",
    [
        (None, (15.00, 20.00, 0.00)),
        (5.5, (15.00, 20.00, 0.00)),
        (
            9.5,
            (9.5 * 1.25, 30.00, 9.5 * 0.75),
        ),
    ],
)
def test_set_speed_limits(amode, expected):
    amode = convert_to(amode, "knots", "km/h")
    expected = convert_to(expected, "knots", "km/h")
    result = set_speed_limits(amode)
    np.allclose(np.array(result), np.array(expected))


# rec = IMMA()
# v = {'ID':'SHIP1   ', 'YR':2001, 'MO':1, 'DY':1, 'HR':hour, 'LAT': hour*speed1/60., 'LON':0.0, 'DS':8, 'VS':4 }
# for key in v: rec.data[key] = v[key]
# .trip1.add_report(ex.MarineReport(rec))
# shipid, lat, lon, sst, mat, year, month, day, hour, icoads_ds, icoads_vs, uid


@pytest.fixture()
def trip1():
    _trip1 = ex.Voyage()
    speed1 = convert_to(18.0, "knots", "km/h")
    for hour in range(0, 24):
        rec = IMMA()
        v = {
            "ID": "SHIP1    ",
            "YR": 2001,
            "MO": 1,
            "DY": 1,
            "HR": hour,
            "LAT": hour * speed1 * 360.0 / (2 * np.pi * sg.earths_radius),
            "LON": 0.0,
            "DS": 8,
            "VS": 4,
        }
        for key in v:
            rec.data[key] = v[key]
        _trip1.add_report(ex.MarineReport(rec))

    return _trip1


@pytest.fixture()
def trip2():
    _trip2 = ex.Voyage()
    speed1 = convert_to(18.0, "knots", "km/h")
    for hour in range(0, 3):
        rec = IMMA()
        v = {
            "ID": "SHIP1    ",
            "YR": 2001,
            "MO": 1,
            "DY": 1,
            "HR": hour,
            "LAT": hour * speed1 * 360.0 / (2 * np.pi * sg.earths_radius),
            "LON": 0.0,
            "DS": 8,
            "VS": 4,
        }
        for key in v:
            rec.data[key] = v[key]
        _trip2.add_report(ex.MarineReport(rec))
    _trip2.reps[1].setvar("LON", 1.0)

    return _trip2


def test_first_entry_missing(trip1):
    difference_from_estimated_location = distr1(trip1)
    assert difference_from_estimated_location[0] is None


def test_ship_is_at_computed_location(trip1):
    difference_from_estimated_location = distr1(trip1)
    for i, diff in enumerate(difference_from_estimated_location):
        if 0 < i < len(difference_from_estimated_location) - 1:
            assert pytest.approx(diff, 1) == 0


def test_misplaced_ob_out_by_1degree_times_coslat(trip2):
    difference_from_estimated_location = distr1(trip2)
    expected = (
        (2 * np.pi * sg.earths_radius)
        * np.cos(trip2.reps[1].lat() * np.pi / 180.0)
        / 360
    )
    assert pytest.approx(difference_from_estimated_location[1], 0.00001) == expected


def test_last_entry_missing_1(trip1):
    difference_from_estimated_location = distr2(trip1)
    assert difference_from_estimated_location[-1] is None


def test_ship_is_at_computed_location_1(trip1):
    difference_from_estimated_location = distr2(trip1)
    for i, diff in enumerate(difference_from_estimated_location):
        if 0 < i < len(difference_from_estimated_location) - 1:
            assert pytest.approx(diff, 1) == 0


def test_misplaced_ob_out_by_1degree_times_coslat_1(trip2):
    difference_from_estimated_location = distr2(trip2)
    expected = (
        (2 * np.pi * sg.earths_radius)
        * np.cos(trip2.reps[1].lat() * np.pi / 180.0)
        / 360.0
    )
    assert pytest.approx(difference_from_estimated_location[1], 0.00001) == expected


def test_first_and_last_are_missing_2(trip1):
    midpoint_discrepancies = midpt(trip1)
    assert midpoint_discrepancies[0] is None
    assert midpoint_discrepancies[-1] is None


def test_midpt_1_deg_error_out_by_60coslat_2(trip2):
    midpoint_discrepancies = midpt(trip2)
    assert (
        pytest.approx(midpoint_discrepancies[1], 0.00001)
        == (2 * np.pi * sg.earths_radius)
        * math.cos(trip2.reps[1].lat() * np.pi / 180)
        / 360.0
    )


def test_midpt_at_computed_location_2(trip1):
    midpoint_discrepancies = midpt(trip1)
    for i, pt in enumerate(midpoint_discrepancies):
        if 0 < i < len(midpoint_discrepancies) - 1:
            assert pt is not None
            assert pytest.approx(pt, 1) == 0


@pytest.mark.parametrize("angle", [0, 45, 90, 135, 180, 225, 270, 315, 360])
def test_just_pass_and_just_fail(angle):
    assert 10 == direction_continuity(angle, angle, angle + 60.1)
    assert 0 == direction_continuity(angle, angle, angle + 59.9)


def test_direction_continuity():
    with pytest.raises(ValueError):
        direction_continuity(1, 0, 0 + 60.1)
    with pytest.raises(ValueError):
        direction_continuity(0, 1, 0 + 60.1)


@pytest.mark.parametrize(
    "vsi, vsi_previous, speeds, expected",
    [
        (12, 12, 12, 0),
        (12, 12, 12 + 10.01, 10),
        (12, 12, 12 + 9.99, 0),
        (12, 12, None, 0),
    ],
)
def test_speed_continuity(vsi, vsi_previous, speeds, expected):
    assert speed_continuity(vsi, vsi_previous, speeds) == expected


@pytest.mark.parametrize(
    "vsi, vsi_previous, time_differences, fwd_diff_from_estimated, rev_diff_from_estimated, expected",
    [
        (None, 2.0, 5.0, 5.0, 5.0, 0.0),
        (2.0, None, 5.0, 5.0, 5.0, 0.0),
        (2.0, 2.0, None, 5.0, 5.0, 0.0),
        (2.0, 2.0, 5.0, None, 5.0, 0.0),
        (2.0, 2.0, 5.0, 5.0, None, 0.0),
        (2.0, 2.0, 5.0, 5.0, 5.0, 0.0),
        (2.0, 2.0, 1.0, 20.0, 20.0, 10.0),
    ],
)
def test_check_distance_from_estimate(
    vsi,
    vsi_previous,
    time_differences,
    fwd_diff_from_estimated,
    rev_diff_from_estimated,
    expected,
):
    result = check_distance_from_estimate(
        vsi,
        vsi_previous,
        time_differences,
        fwd_diff_from_estimated,
        rev_diff_from_estimated,
    )
    assert result == expected
