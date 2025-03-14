from __future__ import annotations

import os

import _load_data
import pandas as pd
from _settings import get_settings
from cdm_reader_mapper import read_tables
from cdm_reader_mapper.common.getting_files import load_file

add_data = {
    "level1c": _load_data.load_noc_anc_info,
    "level1d": _load_data.load_pub47,
    "level1e": _load_data.load_metoffice_qc,
}


def _obs_testing(dataset, level, capsys):
    """Observational testing suite."""

    def manipulate_expected(expected, level):
        """Manipulate expected result data."""
        if not hasattr(_settings, "manipulation"):
            return expected
        if level in _settings.manipulation.keys():
            if isinstance(_settings.manipulation[level], list):
                expected = expected[_settings.manipulation[level]]
                new_cols = [col[1] for col in expected.columns]
                expected.columns = new_cols
            else:
                for index, values in _settings.manipulation[level].items():
                    expected[index] = values
        if not hasattr(_settings, "drops"):
            return expected
        if level in _settings.drops.keys():
            expected = expected.drop(_settings.drops[level]).reset_index(drop=True)
        return expected

    _settings = get_settings(dataset)
    tables = _settings.which_tables[level]
    if add_data.get(level) is not None:
        add_data[level](
            cache_dir=f"./T{level}/release_8.0",
        )

    _load_data.load_input(dataset, level, _settings)

    s = (
        "obs_suite "
        f"-l {level} "
        f"-d {dataset} "
        f"-data_dir ./T{level} "
        f"-work_dir ./T{level} "
        f"-sp {_settings.pattern[level]} "
        f"-p_id subset "
        f"-year_i {_settings.year_init} "
        f"-year_e {_settings.year_end} "
        f"-p_list {_settings.process_list} "
        "-o "
        "-run"
    )
    os.system(s)
    captured = capsys.readouterr()
    assert captured.out == ""

    result_dir = f"./T{level}/release_8.0/{dataset}/{level}/{_settings.process_list}"

    if _settings.pattern_out.get(level):
        results = pd.read_csv(
            os.path.join(result_dir, _settings.pattern_out[level]),
            delimiter="|",
            dtype="object",
            keep_default_na=False,
        )
    else:
        results = read_tables(result_dir, cdm_subset=tables)

    for table_name in tables:
        load_file(
            f"{_settings.input_dir}/cdm_tables/{table_name}-{_settings.cdm}.psv",
            cache_dir=f"./E{level}/{dataset}/{level}/{_settings.deck}",
            within_drs=False,
        )

    expected = read_tables(
        f"./E{level}/{dataset}/{level}/{_settings.deck}", cdm_subset=tables
    )
    expected = manipulate_expected(expected.data, level)
    results = results.data

    if "header" in results.columns:
        for deletion in [("header", "record_timestamp"), ("header", "history")]:
            del results[deletion]
            del expected[deletion]

    pd.testing.assert_frame_equal(results, expected)
