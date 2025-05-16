from __future__ import annotations

import numpy as np
import pytest

from glamod_marine_processing.qc_suite.modules.qc import (
    climatology_check,
    climatology_plus_stdev_check,
    climatology_plus_stdev_with_lowbar_check,
    failed,
    hard_limit_check,
    isvalid,
    passed,
    sst_freeze_check,
    untestable,
    value_check,
)


@pytest.mark.parametrize(
    "value, climate_normal, standard_deviation, limit, lowbar, expected",
    [
        (None, 0.0, 1.0, 3.0, 0.5, failed),  # check None returns fail
        (1.0, None, 1.0, 3.0, 0.5, failed),
        (1.0, 0.0, None, 3.0, 0.5, failed),
        (
            1.0,
            0.0,
            2.0,
            3.0,
            0.1,
            passed,
        ),  # Check simple pass 1.0 anomaly with 6.0 limits
        (
            7.0,
            0.0,
            2.0,
            3.0,
            0.1,
            failed,
        ),  # Check fail with 7.0 anomaly and 6.0 limits
        (
            0.4,
            0.0,
            0.1,
            3.0,
            0.5,
            passed,
        ),  # Anomaly outside std limits but < lowbar
        (
            0.4,
            0.0,
            0.1,
            -3.0,
            0.5,
            untestable,
        ),  # Anomaly outside std limits but < lowbar
    ],
)
def test_climatology_plus_stdev_with_lowbar(
    value, climate_normal, standard_deviation, limit, lowbar, expected
):
    assert (
        climatology_plus_stdev_with_lowbar_check(
            value, climate_normal, standard_deviation, limit, lowbar
        )
        == expected
    )


@pytest.mark.parametrize(
    "value, climate_normal, standard_deviation, stdev_limits, limit, expected",
    [
        (None, 0.0, 0.5, [0.0, 1.0], 5.0, failed),  # fails with None
        (2.0, None, 0.5, [0.0, 1.0], 5.0, failed),  # fails with None
        (2.0, 0.0, None, [0.0, 1.0], 5.0, failed),  # fails with None
        (2.0, 0.0, 0.5, [0.0, 1.0], 5.0, passed),  # simple pass
        (2.0, 0.0, 0.5, [0.0, 1.0], 3.0, failed),  # simple fail
        (3.0, 0.0, 1.5, [0.0, 1.0], 2.0, failed),  # fail with limited stdev
        (1.0, 0.0, 0.1, [0.5, 1.0], 5.0, passed),  # pass with limited stdev
        (
            1.0,
            0.0,
            0.5,
            [1.0, 0.0],
            5.0,
            untestable,
        ),  # untestable with limited stdev
        (1.0, 0.0, 0.5, [0.0, 1.0], -1, untestable),  # untestable with limited stdev
    ],
)
def test_climatology_plus_stdev_check(
    value, climate_normal, standard_deviation, stdev_limits, limit, expected
):
    assert (
        climatology_plus_stdev_check(
            value, climate_normal, standard_deviation, stdev_limits, limit
        )
        == expected
    )


def _test_climatology_plus_stdev_check_raises():
    with pytest.raises(ValueError):
        climatology_plus_stdev_check(1.0, 0.0, 0.5, [1.0, 0.0], 5.0)
    with pytest.raises(ValueError):
        climatology_plus_stdev_check(1.0, 0.0, 0.5, [0.0, 1.0], -1)


@pytest.mark.parametrize(
    "value, climate_normal, limit, expected",
    [
        (8.0, 0.0, 8.0, passed),  # pass at limit
        (9.0, 0.0, 8.0, failed),  # fail with anomaly exceeding limit
        (0.0, 9.0, 8.0, failed),  # fail with same anomaly but negative
        (9.0, 0.0, 11.0, passed),  # pass with higher limit
        (0.0, 9.0, 11.0, passed),  # same with negative anomaly
        (None, 0.0, 8.0, failed),  # Fail with Nones as inputs
        (9.0, None, 8.0, failed),  # Fail with Nones as inputs
        (9.0, 0.0, None, failed),  # Fail with Nones as inputs
    ],
)
def test_climatology_check(value, climate_normal, limit, expected):
    assert climatology_check(value, climate_normal, limit) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, failed),
        (5.7, passed),
        (np.nan, failed),
    ],
)
def test_isvalid_check(value, expected):
    assert isvalid(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, failed),
        (5.7, passed),
        (np.nan, passed),
    ],
)
def test_value_check(value, expected):
    assert value_check(value) == expected


@pytest.mark.parametrize(
    "value, limits, expected",
    [
        (5.0, [-20.0, 20.0], passed),
        (25.0, [-20.0, 20.0], failed),
        (-10.0, [-30, 15.0], passed),
    ],
)
def test_hard_limit_check(value, limits, expected):
    assert hard_limit_check(value, limits) == expected


@pytest.mark.parametrize(
    "sst, sst_uncertainty, freezing_point, n_sigma, expected",
    [
        (15.0, 0.0, -1.8, 2.0, passed),
        (-15.0, 0.0, -1.8, 2.0, failed),
        (-2.0, 0.0, -2.0, 2.0, passed),
        (-2.0, 0.5, -1.8, 2.0, passed),
        (-5.0, 0.5, -1.8, 2.0, failed),
        (0.0, None, -1.8, 2.0, untestable),
        (0.0, 0.0, None, 2.0, untestable),
    ],
)
def test_sst_freeze_check(sst, sst_uncertainty, freezing_point, n_sigma, expected):
    assert sst_freeze_check(sst, sst_uncertainty, freezing_point, n_sigma) == expected


def _test_sst_freeze_check_raises():
    with pytest.raises(ValueError):
        sst_freeze_check(0.0, None, -1.8, 2.0)
    with pytest.raises(ValueError):
        sst_freeze_check(0.0, 0.0, None, 2.0)


def test_sst_freeze_check_defaults():
    assert sst_freeze_check(0.0) == passed
    assert sst_freeze_check(-1.8) == passed
    assert sst_freeze_check(-2.0) == failed
