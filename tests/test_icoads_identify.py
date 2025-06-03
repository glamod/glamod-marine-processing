from __future__ import annotations

import pytest

from glamod_marine_processing.qc_suite.modules.auxiliary import failed, passed
from glamod_marine_processing.qc_suite.modules.icoads_identify import (
    id_is_generic,
    is_buoy,
    is_deck,
    is_drifter,
    is_in_valid_list,
    is_ship,
)


@pytest.mark.parametrize(
    "valid_list, expected_true",
    [
        [[1, 56, 831], [1, 56, 831]],
        [["1", "56", "831"], []],
        [["1", 56, 831], [56, 831]],
        [3, [3]],
        ["3", []],
    ],
)
def test_is_in_valid_list(valid_list, expected_true):
    for val in range(0, 1000):
        result = is_in_valid_list(val, valid_list)
        if val in expected_true:
            assert result == passed
        else:
            assert result == failed


def test_is_buoy():
    for pt in range(0, 47):
        result = is_buoy(pt)
        if pt in [6, 7]:
            assert result == passed
        else:
            assert result == failed


def test_is_buoy_valid_list():
    for pt in range(0, 47):
        result = is_buoy(pt, valid_list=3)
        if pt == 3:
            assert result == passed
        else:
            assert result == failed


def test_is_drifter():
    for pt in range(0, 47):
        result = is_drifter(pt)
        if pt == 7:
            assert result == passed
        else:
            assert result == failed


def test_is_drifter_valid_list():
    for pt in range(0, 47):
        result = is_drifter(pt, valid_list=[6, 8])
        if pt in [6, 8]:
            assert result == passed
        else:
            assert result == failed


def test_is_ship():
    for pt in range(0, 47):
        result = is_ship(pt)
        if pt in [0, 1, 2, 3, 4, 5, 10, 11, 12, 17]:
            assert result == passed
        else:
            assert result == failed


def test_is_ship_valid_list():
    for pt in range(0, 47):
        result = is_ship(pt, valid_list=6)
        if pt == 6:
            assert result == passed
        else:
            assert result == failed


def test_is_deck():
    for deck in range(1000):
        result = is_deck(deck)
        if deck == 780:
            assert result == passed
        else:
            assert result == failed


def test_is_deck_valid_list():
    for deck in range(1000):
        result = is_deck(deck, valid_list=[779, 781])
        if deck in [779, 781]:
            assert result == passed
        else:
            assert result == failed


@pytest.mark.parametrize(
    "in_id, year, expected",
    [
        ("QUALMS", 1999, False),
        ("", 1999, True),
        ("SHIP     ", 1999, True),
        ("PLAT     ", 1999, True),
        ("MASK     ", 1999, True),
        ("2        ", 1941, True),
        ("3        ", 1935, True),
        ("7        ", 1950, True),
    ],
)
def test_id_is_generic(in_id, year, expected):
    assert id_is_generic(in_id, year) == expected
