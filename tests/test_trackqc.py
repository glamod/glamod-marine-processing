# flake8: noqa: E501

from __future__ import annotations

import os
import sys

import numpy as np
import pytest

import glamod_marine_processing.qc_suite.modules.Extended_IMMA as ex

# import glamod_marine_processing.qc_suite.modules.next_level_trackqc as tqc
import glamod_marine_processing.qc_suite.modules.trackqc as otqc
from glamod_marine_processing.qc_suite.modules.IMMA1 import IMMA
from glamod_marine_processing.qc_suite.modules.next_level_track_check_qc import (
    calculate_speed_course_distance_time_difference,
)


def test_daytime_exeter():
    daytime = otqc.track_day_test(2019, 6, 21, 12.0, 50.7, -3.5, elevdlim=-2.5)
    assert daytime


def test_nighttime_exeter():
    daytime = otqc.track_day_test(2019, 6, 21, 0.0, 50.7, -3.5, elevdlim=-2.5)
    assert not (daytime)


def test_large_elevdlim_exeter():
    daytime = otqc.track_day_test(2019, 6, 21, 12.0, 50.7, -3.5, elevdlim=89.0)
    assert not (daytime)


def test_lat_is_zero():
    assert otqc.track_day_test(2022, 5, 3, 12.0, 0.0, 0.0, elevdlim=-2.5)


@pytest.mark.parametrize(
    "year, month, day, hour, lat, lon",
    [
        (2019, 13, 21, 0.0, 50.7, -3.5),
        (None, 12, 21, 0.0, 50.7, -3.5),
        (2019, None, 21, 0.0, 50.7, -3.5),
        (2019, 12, None, 0.0, 50.7, -3.5),
        (2019, 12, 21, None, 50.7, -3.5),
        (2019, 12, 21, 0.0, None, -3.5),
        (2019, 12, 21, 0.0, 50.7, None),
        (2019, 12, 43, 0.0, 50.7, -3.5),
        (2019, 12, 21, -5.0, 50.7, -3.5),
        (2019, 12, 21, 0.0, -99.0, -3.5),
    ],
)
def test_error_invalid_parameter(year, month, day, hour, lat, lon):
    with pytest.raises(ValueError):
        assert otqc.track_day_test(year, month, day, hour, lat, lon, elevdlim=-2.5)


def test_no_trim():
    arr = np.array([10.0, 4.0, 3.0, 2.0, 1.0])
    trim = otqc.trim_mean(arr, 0)
    assert trim == 4.0
    assert np.all(
        arr == np.array([10.0, 4.0, 3.0, 2.0, 1.0])
    )  # this checks the array is not modifed by the function


def test_with_trim():
    arr = np.array([10.0, 4.0, 3.0, 2.0, 1.0])
    trim = otqc.trim_mean(arr, 5)
    assert trim == 3.0
    assert np.all(
        arr == np.array([10.0, 4.0, 3.0, 2.0, 1.0])
    )  # this checks the array is not modifed by the function


def test_sd_no_trim():
    arr = np.array([6.0, 1.0, 1.0, 1.0, 1.0])
    trim = otqc.trim_std(arr, 0)
    assert trim == 2.0
    assert np.all(
        arr == np.array([6.0, 1.0, 1.0, 1.0, 1.0])
    )  # this checks the array is not modifed by the function


def test_sd_with_trim():
    arr = np.array([6.0, 1.0, 1.0, 1.0, 1.0])
    trim = otqc.trim_std(arr, 5)
    assert trim == 0.0
    assert np.all(
        arr == np.array([6.0, 1.0, 1.0, 1.0, 1.0])
    )  # this checks the array is not modifed by the function


# def make_test_data(selection):
#     if selection == 1:
#         # stationary drifter
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 2,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 3,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 4,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 5,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 6,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 2:
#         # stationary drifter (artificial 'jitter' spikes)
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 2,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 3,
#                 "HR": 12,
#                 "LAT": 1.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 4,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 5,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 1.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 6,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 3:
#         # stationary drifter (artificial 'jitter' which won't be fully smoothed and outside tolerance)
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 2,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 3,
#                 "HR": 12,
#                 "LAT": 1.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 4,
#                 "HR": 12,
#                 "LAT": 1.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 5,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 6,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 4:
#         # stationary drifter (artificial 'jitter' which won't be fully smoothed and within tolerance)
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 2,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 3,
#                 "HR": 12,
#                 "LAT": 0.01,
#                 "LON": 0.01,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 4,
#                 "HR": 12,
#                 "LAT": 0.01,
#                 "LON": 0.01,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 5,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 6,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 5:
#         # moving drifter (going west)
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 2,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.02,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 3,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.04,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 4,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.06,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 5,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.08,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 6,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.10,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.12,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 6:
#         # moving drifter (going north)
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 2,
#                 "HR": 12,
#                 "LAT": 0.02,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 3,
#                 "HR": 12,
#                 "LAT": 0.04,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 4,
#                 "HR": 12,
#                 "LAT": 0.06,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 5,
#                 "HR": 12,
#                 "LAT": 0.08,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 6,
#                 "HR": 12,
#                 "LAT": 0.10,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 0.12,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 7:
#         # runs aground (drifter going north then stops)
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 2,
#                 "HR": 12,
#                 "LAT": 0.02,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 3,
#                 "HR": 12,
#                 "LAT": 0.04,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 4,
#                 "HR": 12,
#                 "LAT": 0.06,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 5,
#                 "HR": 12,
#                 "LAT": 0.08,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 6,
#                 "HR": 12,
#                 "LAT": 0.08,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 0.08,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 8:
#         # stationary drifter (high frequency sampling prevents detection)
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 1,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 2,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 3,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 4,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 5,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 6,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 7,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 9:
#         # stationary drifter (low frequency sampling prevents detection)
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 4,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 10,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 13,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 16,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 19,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 10:
#         # stationary drifter (mid frequency sampling enables detection)
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 3,
#                 "HR": 0,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 4,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 6,
#                 "HR": 0,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 9,
#                 "HR": 0,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 10,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 11:
#         # stationary drifter (changed sampling prevents early detection)
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 4,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 8,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 9,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 10,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 11,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 12:
#         # moving drifter (going northwest at equator but going slowly and within tolerance)
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 2,
#                 "HR": 12,
#                 "LAT": 0.005,
#                 "LON": -0.005,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 3,
#                 "HR": 12,
#                 "LAT": 0.01,
#                 "LON": -0.01,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 4,
#                 "HR": 12,
#                 "LAT": 0.015,
#                 "LON": -0.015,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 5,
#                 "HR": 12,
#                 "LAT": 0.02,
#                 "LON": -0.02,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 6,
#                 "HR": 12,
#                 "LAT": 0.025,
#                 "LON": -0.025,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 0.03,
#                 "LON": -0.03,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 13:
#         # moving drifter (going west in high Arctic but going slower than tolerance set at equator)
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 85.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 2,
#                 "HR": 12,
#                 "LAT": 85.0,
#                 "LON": -0.02,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 3,
#                 "HR": 12,
#                 "LAT": 85.0,
#                 "LON": -0.04,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 4,
#                 "HR": 12,
#                 "LAT": 85.0,
#                 "LON": -0.06,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 5,
#                 "HR": 12,
#                 "LAT": 85.0,
#                 "LON": -0.08,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 6,
#                 "HR": 12,
#                 "LAT": 85.0,
#                 "LON": -0.10,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 85.0,
#                 "LON": -0.12,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 14:
#         # stationary then moves
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 2,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 3,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 4,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 5,
#                 "HR": 12,
#                 "LAT": 0.02,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 6,
#                 "HR": 12,
#                 "LAT": 0.04,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 0.06,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 15:
#         # too short for QC
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 2,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.02,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 16:
#         # assertion error - bad input parameter
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 2,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.02,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 3,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.04,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 4,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.06,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 5,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.08,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 6,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.10,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.12,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 17:
#         # assertion error - missing observation
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 2,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.02,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 3,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.04,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 4,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.06,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 5,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.08,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 6,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.10,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.12,
#                 "SST": 5.0,
#             },
#         ]
#     elif selection == 18:
#         # assertion error - times not sorted
#         vals = [
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 1,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": 0.0,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 2,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.02,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 3,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.04,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 2,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.06,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 5,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.08,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 6,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.10,
#                 "SST": 5.0,
#             },
#             {
#                 "ID": "AAAAAAAAA",
#                 "YR": 2003,
#                 "MO": 12,
#                 "DY": 7,
#                 "HR": 12,
#                 "LAT": 0.0,
#                 "LON": -0.12,
#                 "SST": 5.0,
#             },
#         ]
#
#     from datetime import datetime
#
#     id = [x["ID"] for x in vals]
#     date = [datetime(x["YR"], x["MO"], x["DY"], x["HR"]) for x in vals]
#     lat = [x["LAT"] for x in vals]
#     lon = [x["LON"] for x in vals]
#     sst = [x["SST"] for x in vals]
#
#     df = pd.DataFrame({"id": id, "date": date, "lat": lat, "lon": lon, "sst": sst})
#     df = calculate_speed_course_distance_time_difference(df)
#
#     return df
#
#
# @pytest.fixture
# def vals1():
#     return make_test_data(1)
#
#
# @pytest.fixture
# def vals2():
#     return make_test_data(2)
#
#
# @pytest.fixture
# def vals3():
#     return make_test_data(3)
#
#
# @pytest.fixture
# def vals4():
#     return make_test_data(4)
#
#
# @pytest.fixture
# def vals5():
#     return make_test_data(5)
#
#
# @pytest.fixture
# def vals6():
#     return make_test_data(6)
#
#
# @pytest.fixture
# def vals7():
#     return make_test_data(7)
#
#
# @pytest.fixture
# def vals8():
#     return make_test_data(8)
#
#
# @pytest.fixture
# def vals9():
#     return make_test_data(9)
#
#
# @pytest.fixture
# def vals10():
#     return make_test_data(10)
#
#
# @pytest.fixture
# def vals11():
#     return make_test_data(11)
#
#
# @pytest.fixture
# def vals12():
#     return make_test_data(12)
#
#
# @pytest.fixture
# def vals13():
#     return make_test_data(13)
#
#
# @pytest.fixture
# def vals14():
#     return make_test_data(14)
#
#
# @pytest.fixture
# def vals15():
#     return make_test_data(15)
#
#
# @pytest.fixture
# def vals16():
#     return make_test_data(16)
#
#
# @pytest.fixture
# def vals17():
#     return make_test_data(17)
#
#
# @pytest.fixture
# def vals18():
#     return make_test_data(18)
#
#
# def test_stationary(vals1):
#     expected_flags = [1, 1, 1, 1, 1, 1, 1]
#     otqc.aground_check(vals1, 3, 1, 2)
#     for i in range(len(vals1)):
#         assert vals1.drf_agr == expected_flags[i]


@pytest.fixture
def reps1():
    # stationary drifter
    # fmt: off
    vals1 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
    ]
    # fmt: on

    reps = ex.Voyage()

    for v in vals1:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_stationary_b(reps1):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.aground_check(reps1.reps, 3, 1, 2)
    for i in range(0, len(reps1)):
        assert reps1.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps2():
    # stationary drifter (artificial 'jitter' spikes)
    # fmt: off
    vals2 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 1.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.0, "LON": 1.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals2:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_stationary_jitter_spikes(reps2):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.aground_check(reps2.reps, 3, 1, 2)
    for i in range(0, len(reps2)):
        assert reps2.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps3():
    # stationary drifter (artificial 'jitter' which won't be fully smoothed and outside tolerance)
    # fmt: off
    vals3 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 1.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 1.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()

    for v in vals3:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_stationary_big_remaining_jitter(reps3):
    expected_flags = [0, 0, 0, 0, 1, 1, 1]
    otqc.aground_check(reps3.reps, 3, 1, 2)
    for i in range(0, len(reps3)):
        assert reps3.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps4():
    # stationary drifter (artificial 'jitter' which won't be fully smoothed and within tolerance)
    # fmt: off
    vals4 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 0.01, "LON": 0.01, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.01, "LON": 0.01, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals4:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_stationary_small_remaining_jitter(reps4):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.aground_check(reps4.reps, 3, 1, 2)
    for i in range(0, len(reps4)):
        assert reps4.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps5():
    # moving drifter (going west)
    # fmt: off
    vals5 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": -0.02, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 0.0, "LON": -0.04, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.0, "LON": -0.06, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.0, "LON": -0.08, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.0, "LON": -0.10, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": -0.12, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals5:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_moving_west(reps5):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.aground_check(reps5.reps, 3, 1, 2)
    for i in range(0, len(reps5)):
        assert reps5.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps6():
    # moving drifter (going north)
    # fmt: off
    vals6 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.02, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 0.04, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.06, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.08, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.10, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.12, "LON": 0.0, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals6:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_moving_north(reps6):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.aground_check(reps6.reps, 3, 1, 2)
    for i in range(0, len(reps6)):
        assert reps6.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps7():
    # runs aground (drifter going north then stops)
    # fmt: off
    vals7 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.02, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 0.04, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.06, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.08, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.08, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.08, "LON": 0.0, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals7:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)
    return reps


def test_moving_north_then_stop(reps7):
    expected_flags = [0, 0, 0, 0, 1, 1, 1]
    otqc.aground_check(reps7.reps, 3, 1, 2)
    for i in range(0, len(reps7)):
        assert reps7.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps8():
    # stationary drifter (high frequency sampling prevents detection)
    # fmt: off
    vals8 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals8:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_stationary_high_freq_sampling(reps8):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.aground_check(reps8.reps, 3, 1, 2)
    for i in range(0, len(reps8)):
        assert reps8.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps9():
    # stationary drifter (low frequency sampling prevents detection)
    # fmt: off
    vals9 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 10, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 13, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 16, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 19, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals9:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_stationary_low_freq_sampling(reps9):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.aground_check(reps9.reps, 3, 1, 2)
    for i in range(0, len(reps9)):
        assert reps9.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps10():
    # stationary drifter (mid frequency sampling enables detection)
    # fmt: off
    vals10 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 9, "HR": 0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 10, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()

    for v in vals10:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_stationary_mid_freq_sampling(reps10):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.aground_check(reps10.reps, 3, 1, 2)
    for i in range(0, len(reps10)):
        assert reps10.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps11():
    # stationary drifter (changed sampling prevents early detection)
    # fmt: off
    vals11 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 8, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 9, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 10, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 11, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()

    for v in vals11:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_stationary_low_to_mid_freq_sampling(reps11):
    expected_flags = [0, 0, 1, 1, 1, 1, 1]
    otqc.aground_check(reps11.reps, 3, 1, 2)
    for i in range(0, len(reps11)):
        assert reps11.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps12():
    # moving drifter (going northwest at equator but going slowly and within tolerance)
    # fmt: off
    vals12 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.005, "LON": -0.005, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 0.01, "LON": -0.01, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.015, "LON": -0.015, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.02, "LON": -0.02, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.025, "LON": -0.025, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.03, "LON": -0.03, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()  #

    for v in vals12:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)
    return reps


def test_moving_slowly_northwest(reps12):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.aground_check(reps12.reps, 3, 1, 2)
    for i in range(0, len(reps12)):
        assert reps12.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps13():
    # moving drifter (going west in high Arctic but going slower than tolerance set at equator)
    # fmt: off
    vals13 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 85.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 85.0, "LON": -0.02, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 85.0, "LON": -0.04, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 85.0, "LON": -0.06, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 85.0, "LON": -0.08, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 85.0, "LON": -0.10, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 85.0, "LON": -0.12, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals13:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_moving_slowly_west_in_arctic(reps13):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.aground_check(reps13.reps, 3, 1, 2)
    for i in range(0, len(reps13)):
        assert reps13.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps14():
    # stationary then moves
    # fmt: off
    vals14 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.02, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.04, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.06, "LON": 0.0, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()

    for v in vals14:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_stop_then_moving_north(reps14):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.aground_check(reps14.reps, 3, 1, 2)
    for i in range(0, len(reps14)):
        assert reps14.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps15():
    # too short for QC
    # fmt: off
    vals15 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": -0.02, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()

    for v in vals15:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_too_short_for_qc(reps15):
    expected_flags = [0, 0]
    old_stdout = sys.stdout
    f = open(os.devnull, "w")
    sys.stdout = f
    otqc.aground_check(reps15.reps, 3, 1, 2)
    sys.stdout = old_stdout
    for i in range(0, len(reps15)):
        assert reps15.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps16():
    # assertion error - bad input parameter
    # fmt: off
    vals16 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": -0.02, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 0.0, "LON": -0.04, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.0, "LON": -0.06, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.0, "LON": -0.08, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.0, "LON": -0.10, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": -0.12, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals16:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_error_bad_input_parameter(reps16):
    expected_flags = [9, 9, 9, 9, 9, 9, 9]
    try:
        otqc.aground_check(reps16.reps, 0, 1, 2)
    except AssertionError as error:
        error_return_text = "invalid input parameter: smooth_win must be >= 1"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps16)):
        assert reps16.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps17():
    # assertion error - missing observation
    # fmt: off
    vals17 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": -0.02, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 0.0, "LON": -0.04, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.0, "LON": -0.06, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.0, "LON": -0.08, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.0, "LON": -0.10, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": -0.12, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals17:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)
    reps.setvar(1, "LON", None)

    return reps


def test_error_missing_observation(reps17):
    expected_flags = [9, 9, 9, 9, 9, 9, 9]
    try:
        otqc.aground_check(reps17.reps, 3, 1, 2)
    except AssertionError as error:
        error_return_text = "problem with report values: Nan(s) found in longitude"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps17)):
        assert reps17.get_qc(i, "POS", "drf_agr") == expected_flags[i]


@pytest.fixture
def reps18():
    # assertion error - times not sorted
    # fmt: off
    vals18 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": -0.02, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 0.0, "LON": -0.04, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": -0.06, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.0, "LON": -0.08, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.0, "LON": -0.10, "SST": 5.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": -0.12, "SST": 5.0, },
    ]
    # fmt: on
    reps = ex.Voyage()

    for v in vals18:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_error_not_time_sorted(reps18):
    expected_flags = [9, 9, 9, 9, 9, 9, 9]
    try:
        otqc.aground_check(reps18.reps, 3, 1, 2)
    except AssertionError as error:
        error_return_text = "problem with report values: times are not sorted"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps18)):
        assert reps18.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_stationary(reps1):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.new_aground_check(reps1.reps, 3, 1)
    for i in range(0, len(reps1)):
        assert reps1.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_stationary_jitter_spikes(reps2):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.new_aground_check(reps2.reps, 3, 1)
    for i in range(0, len(reps2)):
        assert reps2.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_stationary_big_remaining_jitter(reps3):
    expected_flags = [0, 0, 0, 0, 1, 1, 1]
    otqc.new_aground_check(reps3.reps, 3, 1)
    for i in range(0, len(reps3)):
        assert reps3.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_stationary_small_remaining_jitter(reps4):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.new_aground_check(reps4.reps, 3, 1)
    for i in range(0, len(reps4)):
        assert reps4.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_moving_west(reps5):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.new_aground_check(reps5.reps, 3, 1)
    for i in range(0, len(reps5)):
        assert reps5.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_moving_north(reps6):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.new_aground_check(reps6.reps, 3, 1)
    for i in range(0, len(reps6)):
        assert reps6.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_moving_north_then_stop(reps7):
    expected_flags = [0, 0, 0, 0, 1, 1, 1]
    otqc.new_aground_check(reps7.reps, 3, 1)
    for i in range(0, len(reps7)):
        assert reps7.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_stationary_high_freq_sampling(reps8):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.new_aground_check(reps8.reps, 3, 1)
    for i in range(0, len(reps8)):
        assert reps8.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_stationary_low_freq_sampling(reps9):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.new_aground_check(reps9.reps, 3, 1)
    for i in range(0, len(reps9)):
        assert reps9.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_stationary_mid_freq_sampling(reps10):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.new_aground_check(reps10.reps, 3, 1)
    for i in range(0, len(reps10)):
        assert reps10.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_stationary_low_to_mid_freq_sampling(reps11):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.new_aground_check(reps11.reps, 3, 1)
    for i in range(0, len(reps11)):
        assert reps11.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_moving_slowly_northwest(reps12):
    expected_flags = [0, 0, 0, 1, 1, 1, 1]
    otqc.new_aground_check(reps12.reps, 3, 1)
    for i in range(0, len(reps12)):
        assert reps12.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_moving_slowly_west_in_arctic(reps13):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.new_aground_check(reps13.reps, 3, 1)
    for i in range(0, len(reps13)):
        assert reps13.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_stop_then_moving_north(reps14):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.new_aground_check(reps14.reps, 3, 1)
    for i in range(0, len(reps14)):
        assert reps14.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_too_short_for_qc(reps15):
    expected_flags = [0, 0]
    old_stdout = sys.stdout
    f = open(os.devnull, "w")
    sys.stdout = f
    otqc.new_aground_check(reps15.reps, 3, 1)
    sys.stdout = old_stdout
    for i in range(0, len(reps15)):
        assert reps15.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_error_bad_input_parameter(reps16):
    expected_flags = [9, 9, 9, 9, 9, 9, 9]
    try:
        otqc.new_aground_check(reps16.reps, 2, 1)
    except AssertionError as error:
        error_return_text = "invalid input parameter: smooth_win must be an odd number"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps16)):
        assert reps16.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_error_missing_observation(reps17):
    expected_flags = [9, 9, 9, 9, 9, 9, 9]
    try:
        otqc.new_aground_check(reps17.reps, 3, 1)
    except AssertionError as error:
        error_return_text = "problem with report values: Nan(s) found in longitude"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps17)):
        assert reps17.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_new_error_not_time_sorted(reps18):
    expected_flags = [9, 9, 9, 9, 9, 9, 9]
    try:
        otqc.new_aground_check(reps18.reps, 3, 1)
    except AssertionError as error:
        error_return_text = "problem with report values: times are not sorted"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps18)):
        assert reps18.get_qc(i, "POS", "drf_agr") == expected_flags[i]


def test_assert_limit_periods():
    # default values
    speed_limit, min_win_period, max_win_period = otqc.assert_limit_periods()
    assert speed_limit == 2.5
    assert min_win_period == 1
    assert max_win_period is None

    speed_limit, min_win_period, max_win_period = otqc.assert_limit_periods(
        max_win_period=5.7
    )
    assert speed_limit == 2.5
    assert min_win_period == 1
    assert max_win_period == 5.7


def test_assert_drifters():
    # default values
    n_eval, bias_lim, drif_intra, drif_inter, err_std_n, n_bad, background_err_lim = (
        otqc.assert_drifters()
    )
    assert n_eval == 1
    assert bias_lim == 1.10
    assert drif_intra == 1.0
    assert drif_inter == 0.29
    assert err_std_n == 3.0
    assert n_bad == 2
    assert background_err_lim == 0.3


def test_assert_window_drifters():
    # default values
    (
        long_win_len,
        long_err_std_n,
        short_win_len,
        short_err_std_n,
        short_win_n_bad,
        drif_inter,
        drif_intra,
        background_err_lim,
    ) = otqc.assert_window_drifters()

    assert long_win_len == 1
    assert long_err_std_n == 3.0
    assert short_win_len == 1
    assert short_err_std_n == 3.0
    assert short_win_n_bad == 1
    assert drif_inter == 0.29
    assert drif_intra == 1.00
    assert background_err_lim == 0.3


@pytest.fixture
def iquam_parameters():
    return {
        "number_of_neighbours": 5,
        "buoy_speed_limit": 15.0,
        "ship_speed_limit": 60.0,
        "delta_d": 1.11,
        "delta_t": 0.01,
    }


@pytest.fixture
def reps1a():
    # stationary drifter
    # fmt: off
    vals1 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals1:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


@pytest.fixture
def reps2a():
    # fast moving drifter
    # fmt: off
    vals2 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 3.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 6.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 9.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 12.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 15.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 18.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals2:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


@pytest.fixture
def reps3a():
    # slow moving drifter
    # fmt: off
    vals3 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": 1.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 0.0, "LON": 2.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.0, "LON": 3.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.0, "LON": 4.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.0, "LON": 5.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": 6.0, "SST": 5.0, "PT": 7, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals3:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


@pytest.fixture
def reps4a():
    # slow-fast-slow moving drifter
    # fmt: off
    vals4 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 1.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 2.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 5.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 8.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 9.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 10.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals4:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


@pytest.fixture
def reps5a():
    # fast moving drifter (high frequency sampling)
    # fmt: off
    vals5 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 1, "LAT": 3.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 2, "LAT": 6.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 3, "LAT": 9.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 4, "LAT": 12.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 5, "LAT": 15.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 6, "LAT": 18.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals5:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


@pytest.fixture
def reps6a():
    # fast moving drifter (low frequency sampling)
    # fmt: off
    vals6 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 13, "LAT": 5.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 14, "LAT": 10.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 15, "LAT": 15.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 16, "LAT": 20.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 17, "LAT": 25.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 18, "LAT": 30.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals6:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


@pytest.fixture
def reps7a():
    # slow-fast-slow moving drifter (mid frequency sampling)
    # fmt: off
    vals7 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.5, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 0, "LAT": 1.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 2.5, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 0, "LAT": 4.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 4.5, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 0, "LAT": 5.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals7:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


@pytest.fixture
def reps8a():
    # fast moving drifter (with irregular sampling)
    # fmt: off
    vals8 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 3.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 12.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 12.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 23, "LAT": 14.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 23, "LAT": 14.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 23, "LAT": 17.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals8:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


@pytest.fixture
def reps9a():
    # fast moving Arctic drifter
    # fmt: off
    vals9 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 85.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 85.0, "LON": 30.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 85.0, "LON": 60.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 85.0, "LON": 90.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 85.0, "LON": 120.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 85.0, "LON": 150.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 85.0, "LON": 180.0, "SST": 5.0, "PT": 7, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals9:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


@pytest.fixture
def reps10a():
    # stationary drifter (gross position errors)
    # fmt: off
    vals10 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 50.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 50.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals10:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


@pytest.fixture
def reps11a():
    # too short for QC
    # fmt: off
    vals11 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals11:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


@pytest.fixture
def reps12a():
    # assertion error - bad input parameter
    # fmt: off
    vals12 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals12:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


@pytest.fixture
def reps13a():
    # assertion error - missing observation
    # fmt: off
    vals13 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 4, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
    ]
    # fmt: on
    reps = ex.Voyage()
    for v in vals13:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)
    reps.setvar(1, "LON", None)

    return reps


@pytest.fixture
def reps14a():
    # assertion error - times not sorted
    # fmt: off
    vals14 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 3, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 2, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 5, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 6, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 7, "HR": 12, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "PT": 7, },
    ]
    # fmt: on
    reps = ex.Voyage()

    for v in vals14:
        rec = IMMA()
        for key in v:
            rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        reps.add_report(rep)

    return reps


def test_stationary_a(reps1a):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.speed_check(reps1a.reps, 2.5, 0.5, 1.0)
    for i in range(0, len(reps1a)):
        assert reps1a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_fast_drifter(reps2a):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.speed_check(reps2a.reps, 2.5, 0.5, 1.0)
    for i in range(0, len(reps2a)):
        assert reps2a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_slow_drifter(reps3a):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.speed_check(reps3a.reps, 2.5, 0.5, 1.0)
    for i in range(0, len(reps3a)):
        assert reps3a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_slow_fast_slow_drifter(reps4a):
    expected_flags = [0, 0, 1, 1, 1, 0, 0]
    otqc.speed_check(reps4a.reps, 2.5, 0.5, 1.0)
    for i in range(0, len(reps4a)):
        assert reps4a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_high_freqency_sampling(reps5a):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.speed_check(reps5a.reps, 2.5, 0.5, 1.0)
    for i in range(0, len(reps5a)):
        assert reps5a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_low_freqency_sampling(reps6a):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.speed_check(reps6a.reps, 2.5, 0.5, 1.0)
    for i in range(0, len(reps6a)):
        assert reps6a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_slow_fast_slow_mid_freqency_sampling(reps7a):
    expected_flags = [0, 1, 1, 1, 1, 1, 0]
    otqc.speed_check(reps7a.reps, 2.5, 0.5, 1.0)
    for i in range(0, len(reps7a)):
        assert reps7a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_irregular_sampling(reps8a):
    expected_flags = [1, 1, 0, 0, 0, 1, 1]
    otqc.speed_check(reps8a.reps, 2.5, 0.5, 1.0)
    for i in range(0, len(reps8a)):
        assert reps8a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_fast_arctic_drifter(reps9a):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.speed_check(reps9a.reps, 2.5, 0.5, 1.0)
    for i in range(0, len(reps9a)):
        assert reps9a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_stationary_gross_error(reps10a):
    expected_flags = [0, 1, 1, 1, 1, 1, 1]
    otqc.speed_check(reps10a.reps, 2.5, 0.5, 1.0)
    for i in range(0, len(reps10a)):
        assert reps10a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_too_short_for_qc_a(reps11a):
    expected_flags = [0, 0]
    old_stdout = sys.stdout
    f = open(os.devnull, "w")
    sys.stdout = f
    otqc.speed_check(reps11a.reps, 2.5, 0.5, 1.0)
    sys.stdout = old_stdout
    for i in range(0, len(reps11a)):
        assert reps11a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_error_bad_input_parameter_a(reps12a):
    expected_flags = [9, 9, 9, 9, 9, 9, 9]
    try:
        otqc.speed_check(reps12a.reps, -2.5, 0.5, 1.0)
    except AssertionError as error:
        error_return_text = "invalid input parameter: speed_limit must be >= 0"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps12a)):
        assert reps12a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_error_missing_observation_a(reps13a):
    expected_flags = [9, 9, 9, 9, 9, 9, 9]
    try:
        otqc.speed_check(reps13a.reps, 2.5, 0.5, 1.0)
    except AssertionError as error:
        error_return_text = "problem with report values: Nan(s) found in longitude"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps13a)):
        assert reps13a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_error_not_time_sorted_a(reps14a):
    expected_flags = [9, 9, 9, 9, 9, 9, 9]
    try:
        otqc.speed_check(reps14a.reps, 2.5, 0.5, 1.0)
    except AssertionError as error:
        error_return_text = "problem with report values: times are not sorted"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps14a)):
        assert reps14a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


# --- new speed check ---
def test_new_stationary_a(reps1a, iquam_parameters):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.new_speed_check(reps1a.reps, iquam_parameters, 2.5, 0.5)
    for i in range(0, len(reps1a)):
        assert reps1a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_new_fast_drifter(reps2a, iquam_parameters):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.new_speed_check(reps2a.reps, iquam_parameters, 2.5, 0.5)
    for i in range(0, len(reps2a)):
        assert reps2a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_new_slow_drifter(reps3a, iquam_parameters):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.new_speed_check(reps3a.reps, iquam_parameters, 2.5, 0.5)
    for i in range(0, len(reps3a)):
        assert reps3a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_new_slow_fast_slow_drifter(reps4a, iquam_parameters):
    expected_flags = [0, 0, 1, 1, 1, 0, 0]
    otqc.new_speed_check(reps4a.reps, iquam_parameters, 2.5, 0.5)
    for i in range(0, len(reps4a)):
        assert reps4a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_new_high_freqency_sampling(reps5a, iquam_parameters):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.new_speed_check(reps5a.reps, iquam_parameters, 2.5, 0.5)
    for i in range(0, len(reps5a)):
        assert reps5a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_new_low_freqency_sampling(reps6a, iquam_parameters):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.new_speed_check(reps6a.reps, iquam_parameters, 2.5, 0.5)
    for i in range(0, len(reps6a)):
        assert reps6a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_new_slow_fast_slow_mid_freqency_sampling(reps7a, iquam_parameters):
    expected_flags = [0, 0, 1, 1, 1, 0, 0]
    otqc.new_speed_check(reps7a.reps, iquam_parameters, 2.5, 0.5)
    for i in range(0, len(reps7a)):
        assert reps7a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_new_irregular_sampling(reps8a, iquam_parameters):
    expected_flags = [1, 1, 1, 0, 0, 1, 1]
    otqc.new_speed_check(reps8a.reps, iquam_parameters, 2.5, 0.5)
    for i in range(0, len(reps8a)):
        assert reps8a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_new_fast_arctic_drifter(reps9a, iquam_parameters):
    expected_flags = [1, 1, 1, 1, 1, 1, 1]
    otqc.new_speed_check(reps9a.reps, iquam_parameters, 2.5, 0.5)
    for i in range(0, len(reps9a)):
        assert reps9a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_new_stationary_gross_error(reps10a, iquam_parameters):
    expected_flags = [0, 0, 0, 0, 0, 0, 0]
    otqc.new_speed_check(reps10a.reps, iquam_parameters, 2.5, 0.5)
    for i in range(0, len(reps10a)):
        assert reps10a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_new_too_short_for_qc_a(reps11a, iquam_parameters):
    expected_flags = [0, 0]
    old_stdout = sys.stdout
    f = open(os.devnull, "w")
    sys.stdout = f
    otqc.new_speed_check(reps11a.reps, iquam_parameters, 2.5, 0.5)
    sys.stdout = old_stdout
    for i in range(0, len(reps11a)):
        assert reps11a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_new_error_bad_input_parameter_a(reps12a, iquam_parameters):
    expected_flags = [9, 9, 9, 9, 9, 9, 9]
    try:
        otqc.new_speed_check(reps12a.reps, iquam_parameters, -2.5, 0.5)
    except AssertionError as error:
        error_return_text = "invalid input parameter: speed_limit must be >= 0"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps12a)):
        assert reps12a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_new_error_missing_observation_a(reps13a, iquam_parameters):
    expected_flags = [9, 9, 9, 9, 9, 9, 9]
    try:
        otqc.new_speed_check(reps13a.reps, iquam_parameters, 2.5, 0.5)
    except AssertionError as error:
        error_return_text = "problem with report values: Nan(s) found in longitude"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps13a)):
        assert reps13a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def test_new_error_not_time_sorted_a(reps14a, iquam_parameters):
    expected_flags = [9, 9, 9, 9, 9, 9, 9]
    try:
        otqc.new_speed_check(reps14a.reps, iquam_parameters, 2.5, 0.5)
    except AssertionError as error:
        error_return_text = "problem with report values: times are not sorted"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps14a)):
        assert reps14a.get_qc(i, "POS", "drf_spd") == expected_flags[i]


def tailcheck_vals(selector):
    # all daytime
    # fmt: off
    # @formatter:off
    vals1 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 12.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # all land-masked
    vals2 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # all ice
    vals3 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.2, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.2, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.2, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.2, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.2, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.2, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.2, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.2, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.2, },
    ]

    # one usable value
    vals4 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # start tail bias
    vals5 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # start tail negative bias
    vals6 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 4.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 4.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 4.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 4.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # start tail bias obs missing
    vals7 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # end tail bias
    vals8 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # end tail bias obs missing
    vals9 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": None, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # start tail noisy
    vals10 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 7.5, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # end tail noisy
    vals11 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 7.5, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # two tails
    vals12 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 7.5, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # all biased
    vals13 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # all noisy
    vals14 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 7.5, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 7.5, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 7.5, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # start tail bias with bgvar
    vals15 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.4, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # all biased with bgvar
    vals16 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.4, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # short start tail
    vals17 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # short end tail
    vals18 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # short two tails
    vals19 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # short all fail
    vals20 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # short start tail with bgvar
    vals21 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.4, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # short all fail with bgvar
    vals22 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.4, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 7.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # long and short start tail
    vals23 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 6.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # long and short end tail
    vals24 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 6.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # long and short two tail
    vals25 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 6.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 6.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # one long and one short tail
    vals26 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 6.2, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # too short for short tail
    vals27 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # long and short all fail
    vals28 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.5, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.5, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # long and short start tail with bgvar
    vals29 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 7.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 7.0, "OSTIA": 5.0, "BGVAR": 0.4, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # long and short all fail with bgvar
    vals30 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 6.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.5, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.5, "OSTIA": 5.0, "BGVAR": 0.4, "ICE": 0.0, },
    ]

    # good data
    vals31 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.1, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.1, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.1, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.1, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.1, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.01, "ICE": 0.0, },
    ]

    # long and short start tail big bgvar
    vals32 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 6.1, "OSTIA": 5.0, "BGVAR": 0.3, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 6.1, "OSTIA": 5.0, "BGVAR": 0.3, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 6.1, "OSTIA": 5.0, "BGVAR": 0.3, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 6.1, "OSTIA": 5.0, "BGVAR": 0.3, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.3, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.3, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.3, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.3, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 0.3, "ICE": 0.0, },
    ]

    # start tail noisy big bgvar
    vals33 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 7.5, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
    ]

    # assertion error - bad input parameter
    vals34 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
    ]

    # assertion error - missing matched value
    vals35 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
    ]

    # assertion error - invalid ice value
    vals36 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 1.1, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
    ]

    # assertion error - missing observation value
    vals37 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
    ]

    # assertion error - times not sorted
    vals38 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
    ]

    # assertion error - invalid background sst
    vals39 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 46.0, "BGVAR": 1.0, "ICE": 0.0, },
    ]

    # assertion error - invalid background error variance
    vals40 = [
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.0, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.1, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.2, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.3, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": -1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.4, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.5, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.6, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.7, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
        {"ID": "AAAAAAAAA", "YR": 2003, "MO": 12, "DY": 1, "HR": 0.8, "LAT": 0.0, "LON": 0.0, "SST": 5.0, "OSTIA": 5.0, "BGVAR": 1.0, "ICE": 0.0, },
    ]
    # fmt: on
    # @formatter:on
    obs = locals()[f"vals{selector}"]
    reps = ex.Voyage()
    for v in obs:
        rec = IMMA()
        for key in v:
            if key not in ["OSTIA", "BGVAR", "ICE"]:
                rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        if selector != 35:
            rep.setext("OSTIA", v["OSTIA"])
        rep.setext("BGVAR", v["BGVAR"])
        rep.setext("ICE", v["ICE"])
        reps.add_report(rep)

    if selector == 37:
        reps.setvar(1, "LAT", None)

    return reps


def test_all_daytime():
    reps = tailcheck_vals(1)

    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_all_land_masked():
    reps = tailcheck_vals(2)

    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_all_ice():
    reps = tailcheck_vals(3)

    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_one_usable_value():
    reps = tailcheck_vals(4)
    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 2, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_start_tail_bias():
    reps = tailcheck_vals(5)
    expected_flags = {
        "drf_tail1": [1, 1, 1, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_start_tail_negative_bias():
    reps = tailcheck_vals(6)
    expected_flags = {
        "drf_tail1": [1, 1, 1, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_start_tail_bias_obs_missing():
    reps = tailcheck_vals(7)
    expected_flags = {
        "drf_tail1": [1, 1, 1, 1, 1, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_end_tail_bias():
    reps = tailcheck_vals(8)
    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 1, 1, 1],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_end_tail_bias_obs_missing():
    reps = tailcheck_vals(9)
    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 1, 1, 1, 1, 1],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_start_tail_noisy():
    reps = tailcheck_vals(10)
    expected_flags = {
        "drf_tail1": [1, 1, 1, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_end_tail_noisy():
    reps = tailcheck_vals(11)
    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 1, 1, 1],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_two_tails():
    reps = tailcheck_vals(12)
    expected_flags = {
        "drf_tail1": [1, 1, 1, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 1, 1, 1],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_all_biased():
    reps = tailcheck_vals(13)
    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_all_noisy():
    reps = tailcheck_vals(14)
    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_start_tail_bias_with_bgvar():
    reps = tailcheck_vals(15)
    expected_flags = {
        "drf_tail1": [1, 1, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


# BROKEN TEST FIXED BY REVERTING TO ORIGINAL CODE
def test_all_biased_with_bgvar():
    reps = tailcheck_vals(16)
    expected_flags = {
        "drf_tail1": [1, 1, 1, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 1, 1, 1],
    }
    otqc.og_sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_short_start_tail():
    reps = tailcheck_vals(17)
    expected_flags = {
        "drf_tail1": [1, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 7, 3.0, 3, 2.0, 2, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_short_end_tail():
    reps = tailcheck_vals(18)
    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 1],
    }
    otqc.sst_tail_check(reps.reps, 7, 3.0, 3, 2.0, 2, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_short_two_tails():
    reps = tailcheck_vals(19)
    expected_flags = {
        "drf_tail1": [1, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 1],
    }
    otqc.sst_tail_check(reps.reps, 7, 3.0, 3, 2.0, 2, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_short_all_fail():
    reps = tailcheck_vals(20)
    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 7, 9.0, 3, 2.0, 2, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


# BROKEN TEST FIXED BY REVERTING TO ORIGINAL CODE
def test_short_start_tail_with_bgvar():
    reps = tailcheck_vals(21)
    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.og_sst_tail_check(reps.reps, 7, 3.0, 3, 2.0, 2, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


# BROKEN TEST FIXED BY REVERTING TO ORIGINAL CODE
def test_short_all_fail_with_bgvar():
    reps = tailcheck_vals(22)
    expected_flags = {
        "drf_tail1": [1, 1, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 1, 1],
    }
    otqc.og_sst_tail_check(reps.reps, 7, 9.0, 3, 2.0, 2, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_long_and_short_start_tail():
    reps = tailcheck_vals(23)
    expected_flags = {
        "drf_tail1": [1, 1, 1, 1, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 1.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_long_and_short_end_tail():
    reps = tailcheck_vals(24)
    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 1, 1, 1, 1],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 1.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_long_and_short_two_tails():
    reps = tailcheck_vals(25)
    expected_flags = {
        "drf_tail1": [1, 1, 1, 1, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 1, 1, 1, 1],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 1.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_one_long_and_one_short_tail():
    reps = tailcheck_vals(26)
    expected_flags = {
        "drf_tail1": [1, 1, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 1],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 1.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_too_short_for_short_tail():
    reps = tailcheck_vals(27)
    expected_flags = {
        "drf_tail1": [1, 1, 1, 1, 1, 1, 1, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 3, 0.5, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_long_and_short_all_fail():
    reps = tailcheck_vals(28)
    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 0.25, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_long_and_short_start_tail_with_bgvar():
    reps = tailcheck_vals(29)
    expected_flags = {
        "drf_tail1": [1, 1, 1, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 1.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


# BROKEN TEST FIXED BY REVERTING TO ORIGINAL CODE
def test_long_and_short_all_fail_with_bgvar():
    reps = tailcheck_vals(30)
    expected_flags = {
        "drf_tail1": [1, 1, 1, 1, 1, 1, 1, 1, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.og_sst_tail_check(reps.reps, 3, 3.0, 1, 0.25, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_good_data():
    reps = tailcheck_vals(31)
    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_long_and_short_start_tail_big_bgvar():
    reps = tailcheck_vals(32)
    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 1.0, 1, 0.29, 1.0, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_start_tail_noisy_big_bgvar():
    reps = tailcheck_vals(33)
    expected_flags = {
        "drf_tail1": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_tail2": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 2.0)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_error_bad_input_parameter_tail_check():
    reps = tailcheck_vals(34)
    expected_flags = {
        "drf_tail1": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_tail2": [9, 9, 9, 9, 9, 9, 9, 9, 9],
    }
    try:
        otqc.sst_tail_check(reps.reps, 0, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    except AssertionError as error:
        error_return_text = "invalid input parameter: long_win_len must be >= 1"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_error_missing_matched_value():
    reps = tailcheck_vals(35)
    expected_flags = {
        "drf_tail1": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_tail2": [9, 9, 9, 9, 9, 9, 9, 9, 9],
    }
    try:
        otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    except AssertionError as error:
        error_return_text = (
            "matched report value is missing: unknown extended variable name OSTIA"
        )
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_error_invalid_ice_value():
    reps = tailcheck_vals(36)
    expected_flags = {
        "drf_tail1": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_tail2": [9, 9, 9, 9, 9, 9, 9, 9, 9],
    }
    try:
        otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    except AssertionError as error:
        error_return_text = "matched ice proportion is invalid"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_error_missing_ob_value():
    reps = tailcheck_vals(37)
    expected_flags = {
        "drf_tail1": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_tail2": [9, 9, 9, 9, 9, 9, 9, 9, 9],
    }

    with pytest.raises(ValueError):
        otqc.og_sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    # try:
    #     otqc.og_sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    # except ValueError as error:
    #     print("CHAPPED")
    # except AssertionError as error:
    #     error_return_text = 'problem with report value: latitude is missing'
    #     assert str(error)[0:len(error_return_text)] == error_return_text
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_error_not_time_sorted_tail_check():
    reps = tailcheck_vals(38)
    expected_flags = {
        "drf_tail1": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_tail2": [9, 9, 9, 9, 9, 9, 9, 9, 9],
    }
    try:
        otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    except AssertionError as error:
        error_return_text = "problem with report value: times are not sorted"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


# BROKEN TEST FIXED BY REVERTING TO ORIGINAL CODE
def test_error_invalid_background():
    reps = tailcheck_vals(39)
    expected_flags = {
        "drf_tail1": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_tail2": [9, 9, 9, 9, 9, 9, 9, 9, 9],
    }
    try:
        otqc.og_sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    except AssertionError as error:
        error_return_text = "matched background sst is invalid"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]


def test_error_invalid_background_error_variance():
    reps = tailcheck_vals(40)
    expected_flags = {
        "drf_tail1": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_tail2": [9, 9, 9, 9, 9, 9, 9, 9, 9],
    }
    try:
        otqc.sst_tail_check(reps.reps, 3, 3.0, 1, 3.0, 1, 0.29, 1.0, 0.3)
    except AssertionError as error:
        error_return_text = "matched background error variance is invalid"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_tail1") == expected_flags["drf_tail1"][i]
        assert reps.get_qc(i, "SST", "drf_tail2") == expected_flags["drf_tail2"][i]

        # tests summary
    """
    - NO CHECK MADE
    + alldaytime
    + all OSTIA missing
    + all ice
    + record too short for either check
    - LONG-TAIL ONLY
    + start tail bias
    + start tail negative bias
    + start tail bias first few obs missing
    + end tail bias
    + end tail bias last few obs missing
    + start tail noisy
    + end tail noisy
    + two tails
    + all record biased
    + all record noisy
    + background error short circuits start tail
    + background error short circuits all biased
    - SHORT-TAIL ONLY
    + start tail
    + end tail
    + two tails
    + all record fail
    + background error short circuits start tail
    + background error short circuits all fail
    - LONG-TAIL then SHORT-TAIL
    + long and short start tail
    + long and short end tail
    + long and short two tails
    + one long tail and one short tail
    + too short for short tail
    + long and short combined fail whole record
    + background error short circuits start tail
    + background error short circuits all fail
    - NO-TAILS
    + no tails
    - EXTRA
    + long and short start tail big bgvar
    + start tail noisy big bgvar
    + assertion error - bad input parameter
    + assertion error - missing matched value
    + assertion error - missing ob value
    + assertion error - invalid ice value
    + assertion error - data not time-sorted
    + assertion error - invalid background sst
    + assertion error - invalid background error
    """


def sst_biased_noisy_check_vals(selector):
    # fmt: off
    # @formatter:off
    # all daytime
    vals1 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 12.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 12.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 12.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 12.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 12.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 12.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 12.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 12.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 12.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # all land-masked
    vals2 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0}]

    # all ice
    vals3 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.2},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.2},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.2},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.2},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.2},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.2},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.2},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.2},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.2}]

    # all bgvar exceeds limit
    vals4 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.4, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.4, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.4, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.4, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.4, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.4, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.4, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.4, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.4, 'ICE': 0.0}]

    # biased warm
    vals5 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # biased cool
    vals6 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 3.8, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 3.8, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 3.8, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 3.8, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 3.8, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 3.8, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 3.8, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 3.8, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 3.8, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # noisy
    vals7 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 7.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 3.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 7.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 3.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 7.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # biased and noisy
    vals8 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 9.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 7.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 7.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 9.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 7.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 7.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 9.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # biased warm obs missing
    vals9 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
             {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 6.2, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0}]

    # short record one bad
    vals10 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 9.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # short record two bad
    vals11 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 9.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 9.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # short record two bad obs missing
    vals12 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 9.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 9.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0}]

    # short record two bad obs missing with bgvar masked
    vals13 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.4, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 9.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 9.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0}]

    # good data
    vals14 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # short record good data
    vals15 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # short record obs missing good data
    vals16 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 0.01, 'ICE': 0.0}]

    # noisy big bgvar
    vals17 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 7.0, 'OSTIA': 5.0, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 3.0, 'OSTIA': 5.0, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 7.0, 'OSTIA': 5.0, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 3.0, 'OSTIA': 5.0, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 7.0, 'OSTIA': 5.0, 'BGVAR': 4.0, 'ICE': 0.0}]

    # short record two bad obs missing big bgvar
    vals18 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 9.0, 'OSTIA': 5.0, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 9.0, 'OSTIA': 5.0, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 4.0, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': None, 'BGVAR': 4.0, 'ICE': 0.0}]

    # good data
    vals19 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # assertion error - bad input parameter
    vals20 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # assertion error - missing matched value
    vals21 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # assertion error - invalid ice value
    vals22 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 1.1},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # assertion error - missing observation value
    vals23 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # assertion error - times not sorted
    vals24 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # assertion error - invalid background sst
    vals25 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 46.0, 'BGVAR': 0.01, 'ICE': 0.0}]

    # assertion error - invalid background error variance
    vals26 = [{'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.0, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.1, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.2, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.3, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': -0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.4, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.5, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.6, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.7, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0},
              {'ID': 'AAAAAAAAA', 'YR': 2003, 'MO': 12, 'DY': 1, 'HR': 0.8, 'LAT': 0.0, 'LON': 0.0, 'SST': 5.0, 'OSTIA': 5.0, 'BGVAR': 0.01, 'ICE': 0.0}]
    # fmt: on
    # @formatter:on

    reps = ex.Voyage()
    obs = locals()[f"vals{selector}"]

    for v in obs:
        rec = IMMA()
        for key in v:
            if key not in ["OSTIA", "BGVAR", "ICE"]:
                rec.data[key] = v[key]
        rep = ex.MarineReportQC(rec)
        if selector != 21:
            rep.setext("OSTIA", v["OSTIA"])
        rep.setext("BGVAR", v["BGVAR"])
        rep.setext("ICE", v["ICE"])
        reps.add_report(rep)

    if selector == 23:
        reps.setvar(1, "LAT", None)

    return reps


def test_all_daytime_bnc():
    reps = sst_biased_noisy_check_vals(1)
    expected_flags = {
        "drf_bias": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_noise": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_short": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_all_land_masked_bnc():
    reps = sst_biased_noisy_check_vals(2)
    expected_flags = {
        "drf_bias": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_noise": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_short": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_all_ice_bnc():
    reps = sst_biased_noisy_check_vals(3)
    expected_flags = {
        "drf_bias": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_noise": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_short": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_all_bgvar_exceeds_limit_bnc():
    reps = sst_biased_noisy_check_vals(4)
    expected_flags = {
        "drf_bias": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_noise": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_short": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_biased_warm_bnc():
    reps = sst_biased_noisy_check_vals(5)
    expected_flags = {
        "drf_bias": [1, 1, 1, 1, 1, 1, 1, 1, 1],
        "drf_noise": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_short": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_biased_cool_bnc():
    reps = sst_biased_noisy_check_vals(6)
    expected_flags = {
        "drf_bias": [1, 1, 1, 1, 1, 1, 1, 1, 1],
        "drf_noise": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_short": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_noisy_bnc():
    reps = sst_biased_noisy_check_vals(7)
    expected_flags = {
        "drf_bias": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_noise": [1, 1, 1, 1, 1, 1, 1, 1, 1],
        "drf_short": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_biased_and_noisy_bnc():
    reps = sst_biased_noisy_check_vals(8)
    expected_flags = {
        "drf_bias": [1, 1, 1, 1, 1, 1, 1, 1, 1],
        "drf_noise": [1, 1, 1, 1, 1, 1, 1, 1, 1],
        "drf_short": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_biased_warm_obs_missing_bnc():
    reps = sst_biased_noisy_check_vals(9)
    expected_flags = {
        "drf_bias": [1, 1, 1, 1, 1, 1, 1, 1, 1],
        "drf_noise": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_short": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_biased_noisy_check(reps.reps, 5, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_short_record_one_bad_bnc():
    reps = sst_biased_noisy_check_vals(10)
    expected_flags = {
        "drf_bias": [0, 0, 0, 0, 0],
        "drf_noise": [0, 0, 0, 0, 0],
        "drf_short": [0, 0, 0, 0, 0],
    }
    otqc.og_sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_short_record_two_bad_bnc():
    reps = sst_biased_noisy_check_vals(11)
    expected_flags = {
        "drf_bias": [0, 0, 0, 0, 0],
        "drf_noise": [0, 0, 0, 0, 0],
        "drf_short": [1, 1, 1, 1, 1],
    }
    otqc.og_sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_short_record_two_bad_obs_missing_bnc():
    reps = sst_biased_noisy_check_vals(12)
    expected_flags = {
        "drf_bias": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_noise": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_short": [1, 1, 1, 1, 1, 1, 1, 1, 1],
    }
    otqc.og_sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_short_record_two_bad_obs_missing_with_bgvar_bnc():
    reps = sst_biased_noisy_check_vals(13)
    expected_flags = {
        "drf_bias": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_noise": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_short": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.og_sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_good_data_bnc_14():
    reps = sst_biased_noisy_check_vals(14)
    expected_flags = {
        "drf_bias": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_noise": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_short": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_short_record_good_data_bnc():
    reps = sst_biased_noisy_check_vals(15)
    expected_flags = {
        "drf_bias": [0, 0, 0, 0, 0],
        "drf_noise": [0, 0, 0, 0, 0],
        "drf_short": [0, 0, 0, 0, 0],
    }
    otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_short_record_obs_missing_good_data_bnc():
    reps = sst_biased_noisy_check_vals(16)
    expected_flags = {
        "drf_bias": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_noise": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_short": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_noisy_big_bgvar_bnc():
    reps = sst_biased_noisy_check_vals(17)
    expected_flags = {
        "drf_bias": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_noise": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_short": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 4.0)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_short_record_two_bad_obs_missing_big_bgvar_bnc():
    reps = sst_biased_noisy_check_vals(18)
    expected_flags = {
        "drf_bias": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_noise": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_short": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 4.0)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_good_data_bnc_19():
    reps = sst_biased_noisy_check_vals(19)
    expected_flags = {
        "drf_bias": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_noise": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "drf_short": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_error_bad_input_parameter_bnc():
    reps = sst_biased_noisy_check_vals(20)
    expected_flags = {
        "drf_bias": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_noise": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_short": [9, 9, 9, 9, 9, 9, 9, 9, 9],
    }
    try:
        otqc.og_sst_biased_noisy_check(reps.reps, 0, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    except AssertionError as error:
        error_return_text = "invalid input parameter: n_eval must be > 0"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_error_missing_matched_value_bnc():
    reps = sst_biased_noisy_check_vals(21)
    expected_flags = {
        "drf_bias": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_noise": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_short": [9, 9, 9, 9, 9, 9, 9, 9, 9],
    }
    try:
        otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    except AssertionError as error:
        error_return_text = (
            "matched report value is missing: unknown extended variable name OSTIA"
        )
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_error_invalid_ice_value_bnc():
    reps = sst_biased_noisy_check_vals(22)
    expected_flags = {
        "drf_bias": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_noise": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_short": [9, 9, 9, 9, 9, 9, 9, 9, 9],
    }
    try:
        otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    except AssertionError as error:
        error_return_text = "matched ice proportion is invalid"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_error_missing_ob_value_bnc():
    reps = sst_biased_noisy_check_vals(23)
    expected_flags = {
        "drf_bias": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_noise": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_short": [9, 9, 9, 9, 9, 9, 9, 9, 9],
    }
    with pytest.raises(ValueError):
        otqc.og_sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)

    try:
        otqc.og_sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    except ValueError as error:
        error_return_text = "lat is missing"
        assert str(error)[0 : len(error_return_text)] == error_return_text

    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_error_not_time_sorted_bnc():
    reps = sst_biased_noisy_check_vals(24)
    expected_flags = {
        "drf_bias": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_noise": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_short": [9, 9, 9, 9, 9, 9, 9, 9, 9],
    }
    try:
        otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    except AssertionError as error:
        error_return_text = "problem with report value: times are not sorted"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_error_invalid_background_bnc():
    reps = sst_biased_noisy_check_vals(25)
    expected_flags = {
        "drf_bias": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_noise": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_short": [9, 9, 9, 9, 9, 9, 9, 9, 9],
    }
    try:
        otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    except AssertionError as error:
        error_return_text = "matched background sst is invalid"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]


def test_error_invalid_background_error_variance_bnc():
    reps = sst_biased_noisy_check_vals(26)
    expected_flags = {
        "drf_bias": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_noise": [9, 9, 9, 9, 9, 9, 9, 9, 9],
        "drf_short": [9, 9, 9, 9, 9, 9, 9, 9, 9],
    }
    try:
        otqc.sst_biased_noisy_check(reps.reps, 9, 1.10, 1.0, 0.29, 3.0, 2, 0.3)
    except AssertionError as error:
        error_return_text = "matched background error variance is invalid"
        assert str(error)[0 : len(error_return_text)] == error_return_text
    for i in range(0, len(reps)):
        assert reps.get_qc(i, "SST", "drf_bias") == expected_flags["drf_bias"][i]
        assert reps.get_qc(i, "SST", "drf_noise") == expected_flags["drf_noise"][i]
        assert reps.get_qc(i, "SST", "drf_short") == expected_flags["drf_short"][i]
