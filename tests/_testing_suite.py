from __future__ import annotations

import os

import _load_data
import pandas as pd
from _settings import get_settings
from cdm_reader_mapper.cdm_mapper import read_tables
from cdm_reader_mapper.common.getting_files import load_file

add_data = {
    "level1a": None,
    "level1b": _load_data.load_NOC_corrections,
    "level1c": _load_data.load_NOC_ANC_INFO,
    "level1d": _load_data.load_Pub47,
    "level1e": _load_data.load_metoffice_qc,
    "level2": None,
}


def _obs_testing(dataset, level, capsys):
    """Observational testing suite."""

    def manipulate_expected(expected, level):
        """Manipulate expected result data."""
        if not hasattr(_settings, "manipulation"):
            return expected
        if level in _settings.manipulation.keys():
            for index, values in _settings.manipulation[level].items():
                expected[index] = values
        if level in _settings.drops.keys():
            expected = expected.drop(_settings.drops[level]).reset_index(drop=True)
        return expected

    _settings = get_settings(dataset)
    tables = _settings.which_tables[level]
    if add_data[level] is not None:
        add_data[level](
            cache_dir=f"./T{level}/release_7.0",
        )

    cache_dir = _load_data.load_input(dataset, level, _settings)

    s = (
        "obs_suite "
        f"-l {level} "
        f"-d {dataset} "
        f"-data_dir ./T{level} "
        f"-work_dir ./T{level} "
        f"-sp {_settings.pattern[level]} "
        f"-p_list {_settings.process_list} "
        "-o "
        "-run "
    )
    if hasattr(_settings, "p_id"):
        s = s + f" -p_id {_settings.p_id}"

    os.system(s)
    captured = capsys.readouterr()
    assert captured.out == ""

    results = read_tables(
        f"./T{level}/release_7.0/{dataset}/{level}/{_settings.deck}", cdm_subset=tables
    )

    for table_name in tables:
        load_file(
            f"{_settings.input_dir}/cdm_tables/{table_name}-{_settings.output}.psv",
            cache_dir=f"./E{level}/{dataset}/{level}/{_settings.deck}",
            within_drs=False,
        )
    expected = read_tables(
        f"./E{level}/{dataset}/{level}/{_settings.deck}", cdm_subset=tables
    )

    expected = manipulate_expected(expected, level)

    for deletion in [("header", "record_timestamp"), ("header", "history")]:
        del results[deletion]
        del expected[deletion]

    pd.testing.assert_frame_equal(results, expected)
