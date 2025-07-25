from __future__ import annotations

import pytest  # noqa

from glamod_marine_processing.qc_suite.modules.astronomical_geometry import (
    convert_degrees,
)


def test_convert_degrees():
    assert convert_degrees(-1.0) == 359.0
    assert convert_degrees(1.0) == 1.0
