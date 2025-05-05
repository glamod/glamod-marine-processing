from __future__ import annotations

import os

from cdm_reader_mapper.common.getting_files import load_file


def load_noc_anc_info(**kwargs):
    """Load NOC ANC INFO data from cdm-testdata."""
    load_file(
        "NOC_ANC_INFO/json_files/dck992.json",
        **kwargs,
    )


def load_pub47(**kwargs):
    """Load Pub47 data from cdm-testdata."""
    load_file(
        "Pub47/monthly/pub47-2022-01.csv",
        **kwargs,
    )


def load_metoffice_qc(**kwargs):
    """Load metoffice QC data from cdm-testdata."""
    for qc_file in [
        "AT_qc_202201_CCIrun.csv",
        "DPT_qc_202201_CCIrun.csv",
        "POS_qc_202201_CCIrun.csv",
        "SLP_qc_202201_CCIrun.csv",
        "SST_qc_202201_CCIrun.csv",
        "SST_qc_202201_hires_CCIrun.csv",
        "Variables_202201_CCIrun.csv",
        "W_qc_202201_CCIrun.csv",
    ]:
        load_file(f"metoffice_qc/base/2022/01/{qc_file}", **kwargs)


def load_input(dataset, level, settings, cache_dir):
    """Load level input data data from cdm-testdata."""
    p_level = settings.prev_level[level]
    leveli = settings.level_input[level]
    process_list = settings.process_list
    cache_dir = f"{cache_dir}/{leveli}/{dataset}/{p_level}/{process_list}"
    if level == "level1a":
        load_level0(cache_dir, settings)
    else:
        load_cdms(cache_dir, settings)
    return cache_dir


def load_cdms(cache_dir, settings):
    """Load level CDM input data from cdm-testdata."""
    for table_name in settings.table_names:
        load_file(
            f"{settings.input_dir}/cdm_tables/{table_name}-{settings.cdm}.psv",
            cache_dir=cache_dir,
            within_drs=False,
        )


def load_level0(cache_dir, settings):
    """Load level0 input data from cdm-testdata."""
    load_file(
        settings.level0,
        cache_dir=cache_dir,
        within_drs=False,
    )
