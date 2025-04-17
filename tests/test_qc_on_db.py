from __future__ import annotations

import pytest  # noqa
from _settings import get_settings
from cdm_reader_mapper import read_tables
from cdm_reader_mapper.common.getting_files import load_file

from glamod_marine_processing.qc_suite.modules.next_level_qc import (
    perform_base_qc,
    perform_obs_qc,
)

dataset = "ICOADS_R3.0.2T"
_settings = get_settings(dataset)
cache_dir = f"./Eqc/{dataset}/qc/{_settings.deck}"
for table in [
    "header",
    "observations-at",
    "observations-dpt",
    "observations-slp",
    "observations-sst",
    "observations-wbt",
    "observations-wd",
    "observations-ws",
]:
    load_file(
        f"{_settings.input_dir}/cdm_tables/header-{_settings.cdm}.psv",
        cache_dir=cache_dir,
        within_drs=False,
    )


def test_header_all():
    db_header = read_tables(cache_dir, cdm_tables="header")
    db_header["report_quality"] = db_header.apply(
        lambda row: perform_base_qc(
            pt=row["platform_type"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            timestamp=row["report_timestamp"],
            parameters={},
        ),
        axis=1,
    )

    # Do some assertion


def test_at_all():
    db_header = read_tables(cache_dir, cdm_tables="observations-at")
    db_header["quality_flag"] = db_header.apply(
        lambda row: perform_obs_qc(at=row["observation_value"], parameters={}), axis=1
    )

    # Do some assertion


def test_dpt_all():
    db_header = read_tables(cache_dir, cdm_tables="observations-dpt")
    db_header["quality_flag"] = db_header.apply(
        lambda row: perform_obs_qc(dpt=row["observation_value"], parameters={}), axis=1
    )

    # Do some assertion


def test_slp_all():
    db_header = read_tables(cache_dir, cdm_tables="observations-slp")
    db_header["quality_flag"] = db_header.apply(
        lambda row: perform_obs_qc(slp=row["observation_value"], parameters={}), axis=1
    )

    # Do some assertion


def test_sst_all():
    db_header = read_tables(cache_dir, cdm_tables="observations-sst")
    db_header["quality_flag"] = db_header.apply(
        lambda row: perform_obs_qc(sst=row["observation_value"], parameters={}), axis=1
    )

    # Do some assertion


def test_wbt_all():
    db_header = read_tables(cache_dir, cdm_tables="observations-wbt")
    db_header["quality_flag"] = db_header.apply(
        lambda row: perform_obs_qc(wbt=row["observation_value"], parameters={}), axis=1
    )

    # Do some assertion


def test_wd_all():
    db_header = read_tables(cache_dir, cdm_tables="observations-wd")
    db_header["quality_flag"] = db_header.apply(
        lambda row: perform_obs_qc(wd=row["observation_value"], parameters={}), axis=1
    )

    # Do some assertion


def test_ws_all():
    db_header = read_tables(cache_dir, cdm_tables="observations-ws")
    db_header["quality_flag"] = db_header.apply(
        lambda row: perform_obs_qc(ws=row["observation_value"], parameters={}), axis=1
    )

    # Do some assertion
