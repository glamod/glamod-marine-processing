from __future__ import annotations

import numpy as np
import pytest

from glamod_marine_processing.qc_suite.modules.astronomical_geometry import (
    angle_diff,
    convert_degrees,
)


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
