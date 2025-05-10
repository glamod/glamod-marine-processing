from __future__ import annotations

import pytest

from glamod_marine_processing.qc_suite.modules.astronomical_geometry import day_test


# result = day_test(year,month,day,hour,lat,lon)
def test_looking_through_window_plus_an_hour_sunup():
    result = day_test(2015, 10, 15, 7.8000, 50.7365, -3.5344)
    assert result == 1


def test_looking_through_window_at_elevenish():
    result = day_test(2018, 9, 25, 11.5000, 50.7365, -3.5344)
    assert result == 1


def test_looking_through_window_plus_an_hour_sunstilldown():
    result = day_test(2015, 10, 15, 7.5000, 50.7365, -3.5344)
    assert result == 0
