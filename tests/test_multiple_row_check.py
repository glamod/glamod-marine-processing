from __future__ import annotations

import pandas as pd
import pytest

from glamod_marine_processing.qc_suite.modules.multiple_row_checks import (
    do_multiple_row_check,
)


def test_multiple_row_check_raises_return_method():
    with pytest.raises(ValueError):
        do_multiple_row_check(
            data=pd.Series(),
            qc_dict={},
            return_method="false",
        )


def test_multiple_row_check_raises_func():
    with pytest.raises(NameError):
        do_multiple_row_check(
            data=pd.Series(),
            qc_dict={"test_QC": {"func": "do_test_qc"}},
        )


def test_multiple_row_check_raises_3():
    with pytest.raises(NameError):
        do_multiple_row_check(
            data=pd.Series(),
            qc_dict={
                "MISSVAL": {
                    "func": "do_missing_value_check",
                    "names": {"value": "observation_value"},
                }
            },
        )


def test_multiple_row_check_raises_4():
    with pytest.raises(ValueError):
        do_multiple_row_check(
            data=pd.Series(),
            qc_dict={
                "MISSVAL": {
                    "func": "do_missing_value_check",
                    "names": {"value2": "observation_value"},
                }
            },
        )
