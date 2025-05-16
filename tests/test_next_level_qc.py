from __future__ import annotations

from datetime import datetime

import numpy as np
import pytest

from glamod_marine_processing.qc_suite.modules.next_level_qc import (
    do_climatology_check,
    do_climatology_plus_stdev_check,
    do_climatology_plus_stdev_with_lowbar_check,
    do_date_check,
    do_day_check,
    do_hard_limit_check,
    do_missing_value_check,
    do_missing_value_clim_check,
    do_position_check,
    do_sst_freeze_check,
    do_supersaturation_check,
    do_time_check,
    do_wind_consistency_check,
)
from glamod_marine_processing.qc_suite.modules.qc import failed, passed, untestable


@pytest.mark.parametrize(
    "latitude, longitude, expected",
    [
        [0.0, 0.0, passed],
        [91.0, 0.0, failed],
        [-91.0, 0.0, failed],
        [0.0, -180.1, failed],
        [0.0, 360.1, failed],
        [None, 0.0, untestable],
        [0.0, None, untestable],
    ],
)
def test_do_position_check(latitude, longitude, expected):
    result = do_position_check(latitude, longitude)
    assert result == expected


def _test_do_position_check_raises_value_error():
    # Make sure that an exception is raised if latitude or longitude is missing
    with pytest.raises(ValueError):
        _ = do_position_check(None, 0.0)
    with pytest.raises(ValueError):
        _ = do_position_check(0.0, None)


@pytest.mark.parametrize(
    "year, month, day, expected",
    [
        (2023, 1, 1, passed),  # 1st January 2023 PASS
        (2023, 2, 29, failed),  # 29th February 2023 FAIL
        (2023, 1, 31, passed),  # 31st January 2023 PASS
        (0, 0, 0, failed),  # 0th of 0 0 FAIL
        (2024, 2, 29, passed),  # 29th February 2024 PASS
        (2000, 2, 29, passed),  # 29th February 2000 PASS
        (1900, 2, 29, failed),  # 29th February 1900 FAIL
        (1899, 3, None, untestable),  # Missing day UNTESTABLE
        (None, 1, 1, untestable),  # Missing year UNTESTABLE
        (1850, None, 1, untestable),  # Missing month UNTESTABLE
    ],
)
def test_do_date_check(year, month, day, expected):
    result = do_date_check(year=year, month=month, day=day)
    assert result == expected


@pytest.mark.parametrize(
    "year, month, day, expected",
    [
        (2023, 1, 1, passed),  # 1st January 2023 PASS
        (2023, 1, 31, passed),  # 31st January 2023 PASS
        (2024, 2, 29, passed),  # 29th February 2024 PASS
        (2000, 2, 29, passed),  # 29th February 2000 PASS
    ],
)
def test_do_date_check_using_date(year, month, day, expected):
    result = do_date_check(date=datetime(year, month, day, 0))
    assert result == expected


def _test_do_date_check_raises_value_error():
    # Make sure that an exception is raised if year or month is set to None
    with pytest.raises(ValueError):
        _ = do_date_check(year=None, month=1, day=1)
    with pytest.raises(ValueError):
        _ = do_date_check(year=1850, month=None, day=1)


@pytest.mark.parametrize(
    "hour, expected",
    [
        (-1.0, failed),  # no negative hours
        (0.0, passed),
        (23.99, passed),
        (24.0, failed),  # 24 hours not allowed
        (29.2, failed),  # nothing over 24 either
        (6.34451, passed),  # check floats
        (None, failed),
    ],
)
def test_do_time_check(hour, expected):
    assert do_time_check(hour=hour) == expected


@pytest.mark.parametrize(
    "year, month, day, hour, latitude, longitude, time, expected",
    [
        (
            2015,
            10,
            15,
            7.8000,
            50.7365,
            -3.5344,
            1.0,
            passed,
        ),  # Known values from direct observation (day); should trigger pass
        (
            2018,
            9,
            25,
            11.5000,
            50.7365,
            -3.5344,
            1.0,
            passed,
        ),  # Known values from direct observation (day); should trigger pass
        (
            2015,
            10,
            15,
            7.5000,
            50.7365,
            -3.5344,
            1.0,
            failed,
        ),  # Known values from direct observation (night); should trigger fail
        (
            2025,
            4,
            17,
            16.04,
            49.160383,
            5.383146,
            1.0,
            passed,
        ),  # Known values from direct observation: should trigger pass
        (
            2015,
            0,
            15,
            7.5000,
            50.7365,
            -3.5344,
            1.0,
            failed,
        ),  # bad month value should trigger fail
        (
            2015,
            10,
            0,
            7.5000,
            50.7365,
            -3.5344,
            1.0,
            failed,
        ),  # bad day value should trigger fail
        (
            2015,
            10,
            15,
            -7.5000,
            50.7365,
            -3.5344,
            1.0,
            failed,
        ),  # bad hour value should trigger fail
        (
            2015,
            1,
            1,
            0.5,
            0.0,
            0.0,
            1,
            failed,
        ),  # 0 lat 0 lon near midnight should trigger fail
        (2015, 1, 1, None, 0.0, 0.0, 1, failed),  # missing hour should trigger fail
    ],
)
def test_do_day_check(year, month, day, hour, latitude, longitude, time, expected):
    result = do_day_check(
        year=year,
        month=month,
        day=day,
        hour=hour,
        latitude=latitude,
        longitude=longitude,
        time_since_sun_above_horizon=time,
    )
    assert result == expected


@pytest.mark.parametrize(
    "year, month, day, hour, latitude, longitude, time, expected",
    [
        (
            2015,
            10,
            15,
            7.8000,
            50.7365,
            -3.5344,
            1.0,
            passed,
        ),
        # Known values from direct observation (day); should trigger pass
        (
            2018,
            9,
            25,
            11.5000,
            50.7365,
            -3.5344,
            1.0,
            passed,
        ),
        # Known values from direct observation (day); should trigger pass
        (
            2015,
            10,
            15,
            7.5000,
            50.7365,
            -3.5344,
            1.0,
            failed,
        ),
        # Known values from direct observation (night); should trigger fail
        (
            2025,
            4,
            17,
            16.04,
            49.160383,
            5.383146,
            1.0,
            passed,
        ),
        # Known values from direct observation: should trigger pass
        (
            2015,
            1,
            1,
            0.5,
            0.0,
            0.0,
            1,
            failed,
        ),  # 0 lat 0 lon near midnight should trigger fail
    ],
)
def test_do_day_check_using_date(
    year, month, day, hour, latitude, longitude, time, expected
):
    truncated_hour = int(np.floor(hour))
    minute = int(60 * (hour - truncated_hour))

    result = do_day_check(
        date=datetime(year, month, day, truncated_hour, minute),
        latitude=latitude,
        longitude=longitude,
        time_since_sun_above_horizon=time,
    )
    assert result == expected


@pytest.mark.parametrize(
    "at, expected", [(5.6, passed), (None, failed), (np.nan, failed)]
)  # not sure if np.nan should trigger FAIL
def test_do_air_temperature_missing_value_check(at, expected):
    assert do_missing_value_check(at) == expected


@pytest.mark.parametrize(
    "at, at_climatology, maximum_anomaly, expected",
    [
        (5.6, 2.2, 10.0, passed),
        (None, 2.2, 10.0, failed),
        (np.nan, 2.2, 10.0, failed),  # not sure if np.nan should trigger FAIL
    ],
)
def test_do_air_temperature_climatology_check(
    at, at_climatology, maximum_anomaly, expected
):
    assert do_climatology_check(at, at_climatology, maximum_anomaly) == expected


@pytest.mark.parametrize(
    "at_climatology, expected",
    [(5.5, passed), (None, failed), (np.nan, failed)],
)  # not sure if np.nan should trigger FAIL
def test_do_air_temperature_missing_value_clim_check(at_climatology, expected):
    assert do_missing_value_clim_check(at_climatology) == expected


@pytest.mark.parametrize(
    "at, hard_limits, expected",
    [
        (5.6, [-10.0, 10.0], passed),
        (15.6, [-10.0, 10.0], failed),
        (None, [-10.0, 10.0], failed),
        (np.nan, [-10.0, 10.0], failed),
    ],
)
def test_do_air_temperature_hard_limit_check(at, hard_limits, expected):
    assert do_hard_limit_check(at, hard_limits) == expected


@pytest.mark.parametrize(
    "at, at_climatology, at_stdev, minmax_standard_deviation, maximum_standardised_anomaly, expected",
    [
        (
            5.6,
            2.2,
            3.3,
            [1.0, 10.0],
            2.0,
            passed,
        ),
        (
            15.6,
            0.6,
            5.0,
            [1.0, 10.0],
            2.0,
            failed,
        ),
        (
            1.0,
            0.0,
            0.1,
            [1.0, 10.0],
            2.0,
            passed,
        ),
        (
            15.0,
            0.0,
            25.0,
            [1.0, 4.0],
            2.0,
            failed,
        ),
        (
            None,
            2.2,
            3.3,
            [1.0, 10.0],
            2.0,
            failed,
        ),
        (
            np.nan,
            2.2,
            3.3,
            [1.0, 10.0],
            2.0,
            failed,  # not sure if np.nan should trigger FAIL
        ),
    ],
)
def test_do_air_temperature_climatology_plus_stdev_check(
    at,
    at_climatology,
    at_stdev,
    minmax_standard_deviation,
    maximum_standardised_anomaly,
    expected,
):
    assert (
        do_climatology_plus_stdev_check(
            at,
            at_climatology,
            at_stdev,
            minmax_standard_deviation,
            maximum_standardised_anomaly,
        )
        == expected
    )


@pytest.mark.parametrize(
    "slp, slp_climatology, slp_stdev, limit, lowbar, expected",
    [
        (
            5.6,
            2.2,
            3.5,
            1.0,
            2.0,
            passed,
        ),  # anomaly of 3.4 is less than 1 sigma (3.5)
        (
            15.6,
            0.6,
            5.0,
            1.0,
            2.0,
            failed,
        ),  # anomaly 15.0 is greater than 1 sigma (5.0)
        (
            1.0,
            0.0,
            0.1,
            1.0,
            2.0,
            passed,
        ),  # anomaly of 1.0 is 10 sigma (0.1) but below lowbar
        (
            15.0,
            0.0,
            25.0,
            1.0,
            2.0,
            passed,
        ),  # anomaly 15.0 is less than 1 sigma (25.0) so passes
        (
            None,
            2.2,
            3.3,
            1.0,
            2.0,
            failed,
        ),  # None causes failed
        (np.nan, 2.2, 3.3, 1.0, 2.0, failed),  # not sure if np.nan should trigger FAIL
    ],
)
def test_do_slp_climatology_plus_stdev_with_lowbar_check(
    slp,
    slp_climatology,
    slp_stdev,
    limit,
    lowbar,
    expected,
):
    assert (
        do_climatology_plus_stdev_with_lowbar_check(
            slp,
            slp_climatology,
            slp_stdev,
            limit,
            lowbar,
        )
        == expected
    )


@pytest.mark.parametrize(
    "dpt, expected", [(5.6, passed), (None, failed), (np.nan, failed)]
)  # not sure if np.nan should trigger FAIL
def test_do_dpt_missing_value_check(dpt, expected):
    assert do_missing_value_check(dpt) == expected


@pytest.mark.parametrize(
    "dpt, dpt_climatology, dpt_stdev, minmax_standard_deviation, maximum_standardised_anomaly, expected",
    [
        (
            5.6,
            2.2,
            3.3,
            [1.0, 10.0],
            2.0,
            passed,
        ),
        (
            15.6,
            0.6,
            5.0,
            [1.0, 10.0],
            2.0,
            failed,
        ),
        (
            1.0,
            0.0,
            0.1,
            [1.0, 10.0],
            2.0,
            passed,
        ),
        (
            15.0,
            0.0,
            25.0,
            [1.0, 4.0],
            2.0,
            failed,
        ),
        (
            None,
            2.2,
            3.3,
            [1.0, 10.0],
            2.0,
            failed,
        ),
        (
            np.nan,
            2.2,
            3.3,
            [1.0, 10.0],
            2.0,
            failed,  # not sure if np.nan should trigger FAIL
        ),
    ],
)
def test_do_dpt_climatology_plus_stdev_check(
    dpt,
    dpt_climatology,
    dpt_stdev,
    minmax_standard_deviation,
    maximum_standardised_anomaly,
    expected,
):
    assert (
        do_climatology_plus_stdev_check(
            dpt,
            dpt_climatology,
            dpt_stdev,
            minmax_standard_deviation,
            maximum_standardised_anomaly,
        )
        == expected
    )


@pytest.mark.parametrize(
    "dpt_climatology, expected",
    [
        (5.5, passed),
        (None, failed),
        (np.nan, failed),
    ],  # not sure if np.nan should trigger FAIL
)
def test_do_dpt_temperature_missing_value_clim_check(dpt_climatology, expected):
    assert do_missing_value_clim_check(dpt_climatology) == expected


@pytest.mark.parametrize(
    "dpt, at, expected",
    [
        (3.6, 5.6, passed),  # clearly unsaturated
        (5.6, 5.6, passed),  # 100% saturation
        (15.6, 13.6, failed),  # clearly supersaturated
        (None, 12.0, failed),  # missing dpt FAIL
        (12.0, None, failed),  # missing at FAIL
    ],
)
def test_do_supersaturation_check(dpt, at, expected):
    assert do_supersaturation_check(dpt, at) == expected


@pytest.mark.parametrize(
    "sst, expected", [(5.6, passed), (None, failed), (np.nan, failed)]
)  # not sure if np.nan should trigger FAIL
def test_do_sst_missing_value_check(sst, expected):
    assert do_missing_value_check(sst) == expected


@pytest.mark.parametrize(
    "sst, sst_climatology, maximum_anomaly, expected",
    [
        (5.6, 2.2, 10.0, passed),
        (None, 2.2, 10.0, failed),
        (np.nan, 2.2, 10.0, failed),  # not sure if np.nan should trigger FAIL
    ],
)
def test_do_sst_climatology_check(sst, sst_climatology, maximum_anomaly, expected):
    assert do_climatology_check(sst, sst_climatology, maximum_anomaly) == expected


@pytest.mark.parametrize(
    "sst_climatology, expected",
    [
        (5.5, passed),
        (None, failed),
        (np.nan, failed),
    ],  # not sure if np.nan should trigger FAIL
)
def test_do_sst_missing_value_clim_check(sst_climatology, expected):
    assert do_missing_value_clim_check(sst_climatology) == expected


@pytest.mark.parametrize(
    "sst, freezing_point, freeze_check_n_sigma, expected",
    [
        (5.6, -1.8, 2.0, passed),
        (-5.6, -1.8, 2.0, failed),
        (0.0, -1.8, 2.0, passed),
        (5.6, 11.8, 2.0, failed),
    ],
)
def test_do_sst_freeze_check(sst, freezing_point, freeze_check_n_sigma, expected):
    assert do_sst_freeze_check(sst, freezing_point, freeze_check_n_sigma) == expected


@pytest.mark.parametrize(
    "ws, expected", [(5.6, passed), (None, failed), (np.nan, failed)]
)  # not sure if np.nan should trigger FAIL
def test_do_wind_speed_missing_value_check(ws, expected):
    assert do_missing_value_check(ws) == expected


@pytest.mark.parametrize(
    "ws, hard_limits, expected",
    [
        (5.6, [-10.0, 10.0], passed),
        (15.6, [-10.0, 10.0], failed),
        (None, [-10.0, 10.0], failed),
        (np.nan, [-10.0, 10.0], failed),
    ],
)
def test_do_wind_speed_hard_limit_check(ws, hard_limits, expected):
    assert do_hard_limit_check(ws, hard_limits=hard_limits) == expected


@pytest.mark.parametrize(
    "wd, expected", [(56, passed), (None, failed), (np.nan, failed)]
)  # not sure if np.nan should trigger FAIL
def test_do_wind_direction_missing_value_check(wd, expected):
    assert do_missing_value_check(wd) == expected


@pytest.mark.parametrize(
    "wd, hard_limits, expected",
    [
        (56, [-100, 100], passed),
        (156, [-100, 100], failed),
        (None, [-100, 100], failed),
        (np.nan, [-100, 100], failed),
    ],
)
def test_do_wind_direction_hard_limit_check(wd, hard_limits, expected):
    assert do_hard_limit_check(wd, hard_limits=hard_limits) == expected


@pytest.mark.parametrize(
    "wind_speed, wind_direction, expected",
    [
        (None, 4, failed),  # missing wind speed; failed
        (4, None, failed),  # missing wind directory; failed
        (0, 0, passed),
        (0, 120, failed),
        (5.0, 0, failed),
        (5, 361, passed),  # do not test hard limits; passed
        (12.0, 362, passed),  # do not test hard limits; passed
        (5, 165, passed),
        (12.0, 73, passed),
    ],
)
def test_do_wind_consistency_check(wind_speed, wind_direction, expected):
    assert (
        do_wind_consistency_check(
            wind_speed,
            wind_direction,
        )
        == expected
    )
