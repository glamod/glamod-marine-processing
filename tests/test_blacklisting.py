from __future__ import annotations

import pytest

from glamod_marine_processing.qc_suite.modules.blacklisting import (
    do_blacklist,
    do_humidity_blacklist,
    do_mat_blacklist,
    do_wind_blacklist,
)
from glamod_marine_processing.qc_suite.modules.qc import failed, passed


@pytest.mark.parametrize(
    "id, deck, year, month, latitude, longitude, platform_type, expected",
    [
        ("", 980, 1850, 1, 0, 0, 1, failed),  # fails lat/lon = 0 zero check
        ("", 874, 1850, 1, 0, 1, 1, failed),  # Deck 874 SEAS fail
        ("", 732, 1850, 1, 0, 1, 13, failed),  # C-MAN station fail
        ("", 732, 1850, 1, 0, 1, 1, passed),  # Deck 732 pass
        ("", 732, 1958, 1, 45, -172, 1, failed),  # Deck 732 fail
        ("", 732, 1974, 1, -47, -60, 1, failed),  # Deck 732 fail
        (
            "",
            732,
            1958,
            1,
            45,
            -172 + 360,
            1,
            failed,
        ),  # Deck 732 shifted longitude fail
        (
            "",
            732,
            1974,
            1,
            -47,
            -60 + 360,
            1,
            failed,
        ),  # Deck 732 shifted longitude fail
        (
            "",
            731,
            1958,
            1,
            45,
            -172,
            1,
            passed,
        ),  # Same are but not in Deck 732 should pass
        (
            "",
            731,
            1974,
            1,
            -47,
            -60,
            1,
            passed,
        ),  # Same are but not in Deck 732 should pass
        (
            "",
            732,
            1957,
            1,
            45,
            -172,
            1,
            passed,
        ),  # Same area but wrong year should pass
        (
            "",
            732,
            1975,
            1,
            -47,
            -60,
            1,
            passed,
        ),  # Same area but wrong year should pass
        ("SUPERIGORINA", 162, 1999, 2, -10, 179, 4, failed),
        ("53521    ", 162, 2005, 11, -10, 179, 4, failed),
        ("53521    ", 162, 2007, 11, -10, 179, 4, passed),
    ],
)
def test_do_blacklist(
    id, deck, year, month, latitude, longitude, platform_type, expected
):
    result = do_blacklist(id, deck, year, month, latitude, longitude, platform_type)
    assert result == expected


def test_do_humidity_blacklist():
    for platform_type in range(0, 47):
        result = do_humidity_blacklist(platform_type)
        if platform_type in [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 15]:
            assert result == passed
        else:
            assert result == failed


@pytest.mark.parametrize(
    "platform_type, deck, latitude, longitude, year, expected",
    [
        (
            5,
            780,
            0.5,
            2.0,
            2011,
            1,
        ),  # Check Deck 780 platform type 5 combination that fails
        (5, 781, 0.5, 2.0, 2011, passed),  # and variants that should pass
        (6, 780, 0.5, 2.0, 2011, passed),  # and variants that should pass
        (1, 193, 45.0, -40.0, 1885, failed),  # In the exclusion zone
        (1, 193, 25.0, -40.0, 1885, passed),  # Outside the exclusion zone (in space)
        (1, 193, 45.0, -40.0, 1877, passed),  # Outside the exclusion zone (in time)
        (1, 193, 45.0, -40.0, 1999, passed),  # Outside the exclusion zone (in time)
    ],
)
def test_do_mat_blacklist(platform_type, deck, latitude, longitude, year, expected):
    result = do_mat_blacklist(platform_type, deck, latitude, longitude, year)
    assert result == expected


def test_do_wind_blacklist():
    for deck in range(1, 1000):
        result = do_wind_blacklist(deck)
        if deck in [708, 780]:
            assert result == failed
        else:
            assert result == passed
