from __future__ import annotations

import os

import _load_data
import pandas as pd
from _settings import get_settings
from cdm_reader_mapper import read_tables
from cdm_reader_mapper.common.getting_files import load_file

cache_dir = ".pytest_cache"

add_data = {
    "level1c": _load_data.load_noc_anc_info,
    "level1d": _load_data.load_pub47,
    "level1e": _load_data.load_metofficeqc,
}


def get_cache_dir(level, cache_dir_t, cache_dir_d):
    """Get cache directory for additonal files."""
    if level == "level1e":
        return cache_dir_t
    return cache_dir_d


def _obs_testing(dataset, level, capsys):
    """Observational testing suite."""

    def manipulate_expected(expected, level):
        """Manipulate expected result data."""
        if (
            hasattr(_settings, "manipulation")
            and level in _settings.manipulation.keys()
        ):
            for index, values in _settings.manipulation[level].items():
                expected[index] = values
        if hasattr(_settings, "selection") and level in _settings.selection.keys():
            expected = expected[_settings.selection[level]]
            new_cols = [col[1] for col in expected.columns]
            expected.columns = new_cols
        if hasattr(_settings, "renames") and level in _settings.renames.keys():
            expected = expected.rename(columns=_settings.renames[level])
        if hasattr(_settings, "drops") and level in _settings.drops.keys():
            expected = expected.drop(_settings.drops[level]).reset_index(drop=True)
        if hasattr(_settings, "reindex") and level in _settings.reindex:
            expected = expected.sort_values(by=("header", "report_id")).reset_index(
                drop=True
            )
        return expected

    cache_dir_t = f"{cache_dir}/T{level}"
    cache_dir_e = f"{cache_dir}/E{level}"
    cache_dir_r = f"{cache_dir_t}/release_8.0"
    cache_dir_d = f"{cache_dir_t}/datasets"

    _settings = get_settings(dataset)
    tables = _settings.which_tables[level]
    if add_data.get(level) is not None:
        add_data[level](
            cache_dir=get_cache_dir(level, cache_dir_t, cache_dir_d),
        )

    _load_data.load_input(dataset, level, _settings, cache_dir_t)
    click_tables = " ".join(f"-tables {t}" for t in tables)

    s = (
        "obs_suite "
        f"-l {level} "
        f"-d {dataset} "
        f"{click_tables} "
        f"-data_dir {cache_dir_t} "
        f"-work_dir {cache_dir_t} "
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

    result_dir = f"{cache_dir_r}/{dataset}/{level}/{_settings.process_list}"
    if _settings.pattern_out.get(level):
        results = pd.read_csv(
            os.path.join(result_dir, _settings.pattern_out[level]),
            delimiter="|",
            dtype="object",
            keep_default_na=False,
        )
    else:
        results = read_tables(result_dir, cdm_subset=tables).data

    for table_name in tables:
        load_file(
            f"{_settings.input_dir}/cdm_tables/{table_name}-{_settings.cdm}.psv",
            cache_dir=f"{cache_dir_e}/{dataset}/{level}/{_settings.deck}",
            within_drs=False,
        )

    expected = read_tables(
        os.path.join(cache_dir_e, dataset, level, _settings.deck), cdm_subset=tables
    )
    expected = manipulate_expected(expected.data, level)

    if "header" in results.columns:
        for deletion in [("header", "record_timestamp"), ("header", "history")]:
            del results[deletion]
            del expected[deletion]

    pd.testing.assert_frame_equal(results, expected)
