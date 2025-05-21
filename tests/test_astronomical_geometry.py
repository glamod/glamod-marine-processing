from __future__ import annotations

import numpy as np
import pytest

from glamod_marine_processing.qc_suite.modules.astronomical_geometry import (
    angle_diff,
    convert_degrees,
    day_test,
)
from glamod_marine_processing.qc_suite.modules.qc import failed, passed


# result = day_test(year,month,day,hour,lat,lon)
@pytest.mark.parametrize(
    "year, month, day,hour, lat, lon, expected",
    [
        (2015, 10, 15, 7.8, 50.7365, -3.5344, failed),
        (2018, 9, 25, 11.5000, 50.7365, -3.5344, failed),
        (2015, 10, 15, 7.5000, 50.7365, -3.5344, passed),
        (2015, 1, 1, 0.5000, 0.0, 0.0, passed),
    ],
)
def test_looking_through_window_plus_an_hour_sunup(
    year, month, day, hour, lat, lon, expected
):
    result = day_test(year, month, day, hour, lat, lon)
    assert result == expected


@pytest.mark.parametrize(
    "angle1, angle2, expected",
    [(0.0, 1.0, 1.0), (0.0, 3 * np.pi / 2, np.pi / 2), (0, 2 * np.pi, 0)],
)
def test_angle_diff(angle1, angle2, expected):
    assert angle_diff(angle1, angle2) == expected


def test_angle_diff_raises():
    with pytest.raises(ValueError):
        angle_diff(None, 1.0)
    with pytest.raises(ValueError):
        angle_diff(1.0, None)


def test_convert_degrees():
    assert convert_degrees(-1.0) == 359.0
    assert convert_degrees(1.0) == 1.0
