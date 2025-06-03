from __future__ import annotations

import pytest

from glamod_marine_processing.qc_suite.modules.interpolation import bilinear_interp


@pytest.mark.parametrize(
    "x1, x2, y1, y2, x, y, q11, q12, q21, q22, expected",
    [
        (0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),  # zero when all zero
        (
            0.0,
            1.0,
            0.0,
            1.0,
            0.5,
            0.5,
            0.0,
            1.0,
            1.0,
            2.0,
            1.0,
        ),  # test_gradient_across_square
        (0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 2.0, 0.0),
        (0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 2.0, 2.0),
        (0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 2.0, 1.0),
        (0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 2.0, 1.0),
        (
            0.0,
            1.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            1.0,
            1.0,
            1.0,
            0.0,
        ),  # test_zero_at_point_set_to_zero
        (
            0.0,
            1.0,
            0.0,
            1.0,
            0.0,
            1.0,
            0.0,
            1.0,
            1.0,
            1.0,
            1.0,
        ),  # test_one_at_points_set_to_one
        (0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0),
        (0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0),
        (
            0.0,
            1.0,
            0.0,
            1.0,
            0.5,
            0.0,
            0.0,
            0.0,
            1.0,
            1.0,
            0.5,
        ),  # test_half_at_point_halfway_between_zero_and_one
        (0.0, 1.0, 0.0, 1.0, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 0.5),
    ],
)
def test_bilinear_interp(x1, x2, y1, y2, x, y, q11, q12, q21, q22, expected):
    assert bilinear_interp(x1, x2, y1, y2, x, y, q11, q12, q21, q22) == expected


@pytest.mark.parametrize(
    "x1, x2, y1, y2, x, y, q11, q12, q21, q22, expected",
    [
        (1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),  # x1 > x2
        (
            0.0,
            1.0,
            1.0,
            0.0,
            0.5,
            0.5,
            0.0,
            1.0,
            1.0,
            2.0,
            1.0,
        ),  # y1 > y2
        (0.0, 1.0, 0.0, 1.0, 1.1, 0.0, 0.0, 1.0, 1.0, 2.0, 0.0),  # x>x2
        (0.0, 1.0, 0.0, 1.0, 1.0, -0.1, 0.0, 1.0, 1.0, 2.0, 2.0),  # y<y1
        (0.0, 1.0, 0.0, 1.0, 0.0, 1.0, None, 1.0, 1.0, 2.0, 1.0),  # missing data points
        (0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, None, 1.0, 2.0, 1.0),
        (
            0.0,
            1.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            1.0,
            None,
            1.0,
            0.0,
        ),
        (
            0.0,
            1.0,
            0.0,
            1.0,
            0.0,
            1.0,
            0.0,
            1.0,
            1.0,
            None,
            1.0,
        ),
    ],
)
def test_bilinear_interp_raises(x1, x2, y1, y2, x, y, q11, q12, q21, q22, expected):
    with pytest.raises(ValueError):
        bilinear_interp(x1, x2, y1, y2, x, y, q11, q12, q21, q22)
