from __future__ import annotations

import pandas as pd
import pytest  # noqa
from _settings import get_settings
from cdm_reader_mapper import DataBundle, read_tables
from cdm_reader_mapper.common.getting_files import load_file

import glamod_marine_processing.qc_suite.modules.qc as qc
from glamod_marine_processing.qc_suite.modules.external_clim import Climatology
from glamod_marine_processing.qc_suite.modules.icoads_identify import (
    is_buoy,
    is_drifter,
    is_in_valid_list,
    is_ship,
)
from glamod_marine_processing.qc_suite.modules.multiple_row_checks import (
    do_multiple_row_check,
)
from glamod_marine_processing.qc_suite.modules.next_level_qc import (
    do_anomaly_check,
    do_climatology_plus_stdev_check,
    do_climatology_plus_stdev_plus_lowbar_check,
    do_date_check,
    do_day_check,
    do_hard_limit_check,
    do_missing_value_check,
    do_no_normal_check,
    do_position_check,
    do_sst_freeze_check,
    do_supersaturation_check,
    do_time_check,
    do_wind_consistency_check,
)


@pytest.fixture(scope="session")
def testdata():
    dataset = "ICOADS_R3.0.2T"
    _settings = get_settings(dataset)
    cache_dir = f".pytest_cache/Eqc/{dataset}/qc/{_settings.deck}"
    tables = [
        "header",
        "observations-at",
        "observations-dpt",
        "observations-slp",
        "observations-sst",
        "observations-wd",
        "observations-ws",
    ]
    for table in tables:
        load_file(
            f"{_settings.input_dir}/cdm_tables/{table}-{_settings.cdm}.psv",
            cache_dir=cache_dir,
            within_drs=False,
        )

    data_dict = {}
    db_tables = read_tables(cache_dir)

    for table in tables:
        db_table = DataBundle()
        db_table.data = db_tables[table].copy()
        if table == "header":
            db_table.data["platform_type"] = db_table["platform_type"].astype(int)
            db_table.data["latitude"] = db_table["latitude"].astype(float)
            db_table.data["longitude"] = db_table["longitude"].astype(float)
            db_table.data["report_timestamp"] = pd.to_datetime(
                db_table["report_timestamp"],
                format="%Y-%m-%d %H:%M:%S",
                errors="coerce",
            )
        else:
            db_table.data["observation_value"] = db_table["observation_value"].astype(
                float
            )
            db_table.data["latitude"] = db_table["latitude"].astype(float)
            db_table.data["longitude"] = db_table["longitude"].astype(float)
            db_table.data["date_time"] = pd.to_datetime(
                db_table["date_time"],
                format="%Y-%m-%d %H:%M:%S",
                errors="coerce",
            )
        if table == "observations-slp":
            db_table.data["observation_value"] = db_table.data["observation_value"]

        data_dict[table] = db_table

    return data_dict


@pytest.fixture(scope="session")
def climdata():
    kwargs = {
        "cache_dir": ".pytest_cache/metoffice_qc",
        "within_drs": False,
        "branch": "qc_ext_files",
    }
    clim_dict = {}
    clim_dict["AT"] = {
        "mean": load_file(
            "metoffice_qc/external_files/AT_pentad_climatology.nc",
            **kwargs,
        ),
        "stdev": load_file(
            "metoffice_qc/external_files/AT_pentad_stdev_climatology.nc",
            **kwargs,
        ),
    }
    clim_dict["DPT"] = {
        "mean": load_file(
            "metoffice_qc/external_files/DPT_pentad_climatology.nc",
            **kwargs,
        ),
        "stdev": load_file(
            "metoffice_qc/external_files/DPT_pentad_stdev_climatology.nc",
            **kwargs,
        ),
    }
    clim_dict["SLP"] = {
        "mean": load_file(
            "metoffice_qc/external_files/SLP_pentad_climatology.nc",
            **kwargs,
        ),
        "stdev": load_file(
            "metoffice_qc/external_files/SLP_pentad_stdev_climatology.nc",
            **kwargs,
        ),
    }
    clim_dict["SST"] = {
        "mean": load_file(
            "metoffice_qc/external_files/SST_daily_climatology_january.nc",
            **kwargs,
        ),
    }
    return clim_dict


@pytest.mark.parametrize(
    "column, valid_list, expected",
    [
        [
            "platform_type",
            [4, 5, 6],
            pd.Series([qc.failed] * 13),
        ],  # platform type is 2 which is not a buoy (4: moored buoy, 5: drifting buoy, 6: ice buoy)
        [
            "platform_type",
            5,
            pd.Series([qc.failed] * 13),
        ],  # platform type is 2 which is not a drfiting buoy (5: drifting buoy)
        [
            "platform_type",
            2,
            pd.Series([qc.passed] * 13),
        ],  # platform type is 2 which is a ship
    ],
)
def test_is_in_valid_list(testdata, column, valid_list, expected):
    db_ = testdata["header"].copy()
    results = db_.apply(
        lambda row: is_in_valid_list(value=row[column], valid_list=valid_list),
        axis=1,
    )
    pd.testing.assert_series_equal(results, expected)


def test_is_buoy(testdata):
    db_ = testdata["header"].copy()
    results = db_.apply(
        lambda row: is_buoy(platform_type=row["platform_type"], valid_list=[4, 5, 6]),
        axis=1,
    )
    expected = pd.Series(
        [qc.failed] * 13
    )  # platform type is 2 which is not a buoy (4: moored buoy, 5: drifting buoy, 6: ice buoy)
    pd.testing.assert_series_equal(results, expected)


def test_is_drifter(testdata):
    db_ = testdata["header"].copy()
    results = db_.apply(
        lambda row: is_drifter(platform_type=row["platform_type"], valid_list=5), axis=1
    )
    expected = pd.Series(
        [qc.failed] * 13
    )  # platform type is 2 which is not a drifting buoy (5: drifting buoy)
    pd.testing.assert_series_equal(results, expected)


def test_is_ship(testdata):
    db_ = testdata["header"].copy()
    results = db_.apply(
        lambda row: is_ship(platform_type=row["platform_type"], valid_list=2), axis=1
    )
    expected = pd.Series([qc.passed] * 13)  # platform type is 2 which is a ship
    pd.testing.assert_series_equal(results, expected)


def test_do_position_check(testdata):
    db_ = testdata["header"].copy()
    results = db_.apply(
        lambda row: do_position_check(
            latitude=row["latitude"], longitude=row["longitude"]
        ),
        axis=1,
    )
    expected = pd.Series([qc.passed] * 13)  # all positions are valid
    pd.testing.assert_series_equal(results, expected)


def test_do_date_check(testdata):
    db_ = testdata["header"].copy()
    results = db_.apply(lambda row: do_date_check(date=row["report_timestamp"]), axis=1)
    expected = pd.Series(
        [
            qc.untestable,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )  # first entry is null
    pd.testing.assert_series_equal(results, expected)


def test_do_time_check(testdata):
    db_ = testdata["header"].copy()
    results = db_.apply(
        lambda row: do_time_check(hour=row["report_timestamp"].hour), axis=1
    )
    expected = pd.Series(
        [
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )  # first entry is null
    pd.testing.assert_series_equal(results, expected)


def test_do_day_check(testdata):
    db_ = testdata["header"].copy()
    results = db_.apply(
        lambda row: do_day_check(
            date=row["report_timestamp"],
            latitude=row["latitude"],
            longitude=row["longitude"],
        ),
        axis=1,
    )
    expected = pd.Series([qc.failed] * 13)  # observations are at night
    pd.testing.assert_series_equal(results, expected)


def test_do_at_missing_value_check(testdata):
    db_ = testdata["observations-at"].copy()
    results = db_.apply(
        lambda row: do_missing_value_check(value=row["observation_value"]),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.passed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_at_hard_limit_check(testdata):
    db_ = testdata["observations-at"].copy()
    results = db_.apply(
        lambda row: do_hard_limit_check(
            value=row["observation_value"],
            hard_limits=[193.15, 338.15],  # K
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.passed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_at_no_normal_check(testdata, climdata):
    db_ = testdata["observations-at"].copy()
    climatology = Climatology.open_netcdf_file(
        climdata["AT"]["mean"],
        "at",
        obs_name="AT",
        statistics="mean",
        time_axis="pentad_time",
    )
    results = db_.apply(
        lambda row: do_no_normal_check(
            climatology=climatology,
            lat=row["latitude"],
            lon=row["longitude"],
            date=row["date_time"],
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_at_anomaly_check(testdata, climdata):
    db_ = testdata["observations-at"].copy()
    climatology = Climatology.open_netcdf_file(
        climdata["AT"]["mean"],
        "at",
        obs_name="AT",
        statistics="mean",
        time_axis="pentad_time",
        target_units="K",
        source_units="degC",
    )
    results = db_.apply(
        lambda row: do_anomaly_check(
            value=row["observation_value"],
            climatology=climatology,
            maximum_anomaly=10.0,  # K
            lat=row["latitude"],
            lon=row["longitude"],
            date=row["date_time"],
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.failed,
            qc.failed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_at_climatology_plus_stdev_check(testdata, climdata):
    db_ = testdata["observations-at"].copy()
    climatology = Climatology.open_netcdf_file(
        climdata["AT"]["mean"],
        "at",
        obs_name="AT",
        statistics="mean",
        time_axis="pentad_time",
        target_units="K",
        source_units="degC",
    )
    stdev = Climatology.open_netcdf_file(
        climdata["AT"]["stdev"],
        "at",
        obs_name="AT",
        statistics="stdev",
        time_axis="pentad_time",
    )
    results = db_.apply(
        lambda row: do_climatology_plus_stdev_check(
            value=row["observation_value"],
            climatology=climatology,
            stdev=stdev,
            minmax_standard_deviation=[1.0, 4.0],  # K
            maximum_standardised_anomaly=5.5,  # K
            lat=row["latitude"],
            lon=row["longitude"],
            date=row["date_time"],
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_slp_missing_value_check(testdata):
    db_ = testdata["observations-slp"].copy()
    results = db_.apply(
        lambda row: do_missing_value_check(value=row["observation_value"]),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.passed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_slp_no_normal_check(testdata, climdata):
    db_ = testdata["observations-slp"].copy()
    climatology = Climatology.open_netcdf_file(
        climdata["SLP"]["mean"], "slp", obs_name="SLP", statistics="mean"
    )
    results = db_.apply(
        lambda row: do_no_normal_check(
            climatology=climatology,
            lat=row["latitude"],
            lon=row["longitude"],
            date=row["date_time"],
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_slp_climatology_plus_stdev_plus_lowbar_check(testdata, climdata):
    db_ = testdata["observations-slp"].copy()
    climatology = Climatology.open_netcdf_file(
        climdata["SLP"]["mean"],
        "slp",
        obs_name="SLP",
        statistics="mean",
        target_units="Pa",
    )
    stdev = Climatology.open_netcdf_file(
        climdata["SLP"]["stdev"],
        "slp",
        obs_name="SLP",
        statistics="stdev",
        target_units="Pa",
        source_units="hPa",
    )
    results = db_.apply(
        lambda row: do_climatology_plus_stdev_plus_lowbar_check(
            value=row["observation_value"],
            climatology=climatology,
            stdev=stdev,
            limit=300,  # Pa
            lowbar=1000,  # Pa
            lat=row["latitude"],
            lon=row["longitude"],
            date=row["date_time"],
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_dpt_missing_value_check(testdata):
    db_ = testdata["observations-dpt"].copy()
    results = db_.apply(
        lambda row: do_missing_value_check(value=row["observation_value"]),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_dpt_hard_limit_check(testdata):
    db_ = testdata["observations-dpt"].copy()
    results = db_.apply(
        lambda row: do_hard_limit_check(
            value=row["observation_value"],
            hard_limits=[193.15, 338.15],  # K
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_dpt_no_normal_check(testdata, climdata):
    db_ = testdata["observations-dpt"].copy()
    climatology = Climatology.open_netcdf_file(
        climdata["DPT"]["mean"],
        "dpt",
        obs_name="DPT",
        statistics="mean",
        time_axis="pentad_time",
    )
    results = db_.apply(
        lambda row: do_no_normal_check(
            climatology=climatology,
            lat=row["latitude"],
            lon=row["longitude"],
            date=row["date_time"],
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_dpt_climatology_plus_stdev_check(testdata, climdata):
    db_ = testdata["observations-dpt"].copy()
    climatology = Climatology.open_netcdf_file(
        climdata["DPT"]["mean"],
        "dpt",
        obs_name="DPT",
        statistics="mean",
        time_axis="pentad_time",
        target_units="K",
        source_units="degC",
    )
    stdev = Climatology.open_netcdf_file(
        climdata["DPT"]["stdev"],
        "dpt",
        obs_name="DPT",
        statistics="stdev",
        time_axis="pentad_time",
    )

    results = db_.apply(
        lambda row: do_climatology_plus_stdev_check(
            value=row["observation_value"],
            climatology=climatology,
            stdev=stdev,
            minmax_standard_deviation=[1.0, 4.0],  # K
            maximum_standardised_anomaly=5.5,  # K
            lat=row["latitude"],
            lon=row["longitude"],
            date=row["date_time"],
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_supersaturation_check(testdata):
    db_ = testdata["observations-at"].copy()
    db2_ = testdata["observations-dpt"].copy()
    db_.data["observation_value_dpt"] = db2_["observation_value"]

    results = db_.apply(
        lambda row: do_supersaturation_check(
            dpt=row["observation_value_dpt"],
            at2=row["observation_value"],
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_sst_missing_value_check(testdata):
    db_ = testdata["observations-sst"].copy()
    results = db_.apply(
        lambda row: do_missing_value_check(value=row["observation_value"]),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.passed,
            qc.passed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_sst_freeze_check(testdata):
    db_ = testdata["observations-sst"].copy()
    results = db_.apply(
        lambda row: do_sst_freeze_check(
            sst=row["observation_value"],
            freezing_point=271.35,
            freeze_check_n_sigma=2.0,
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.passed,
            qc.passed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_sst_hard_limit_check(testdata):
    db_ = testdata["observations-sst"].copy()
    results = db_.apply(
        lambda row: do_hard_limit_check(
            value=row["observation_value"],
            hard_limits=[268.15, 318.15],
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.passed,
            qc.passed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_sst_no_normal_check(testdata, climdata):
    db_ = testdata["observations-sst"].copy()
    climatology = Climatology.open_netcdf_file(
        climdata["SST"]["mean"],
        "sst",
        obs_name="SST",
        statistics="mean",
        valid_ntime=31,
    )
    results = db_.apply(
        lambda row: do_no_normal_check(
            climatology=climatology,
            lat=row["latitude"],
            lon=row["longitude"],
            date=row["date_time"],
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.failed,
            qc.passed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_sst_anomaly_check(testdata, climdata):
    db_ = testdata["observations-sst"].copy()
    climatology = Climatology.open_netcdf_file(
        climdata["SST"]["mean"],
        "sst",
        obs_name="SST",
        statistics="mean",
        valid_ntime=31,
    )
    results = db_.apply(
        lambda row: do_anomaly_check(
            value=row["observation_value"],
            climatology=climatology,
            maximum_anomaly=1.0,
            lat=row["latitude"],
            lon=row["longitude"],
            date=row["date_time"],
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.failed,
            qc.passed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_wind_speed_missing_value_check(testdata):
    db_ = testdata["observations-ws"].copy()
    results = db_.apply(
        lambda row: do_missing_value_check(value=row["observation_value"]),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.passed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_wind_speed_hard_limit_check(testdata):
    db_ = testdata["observations-ws"].copy()
    results = db_.apply(
        lambda row: do_hard_limit_check(
            value=row["observation_value"],
            hard_limits=[0, 13],
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.passed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_wind_direction_missing_value_check(testdata):
    db_ = testdata["observations-wd"].copy()
    results = db_.apply(
        lambda row: do_missing_value_check(value=row["observation_value"]),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.passed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_wind_direction_hard_limit_check(testdata):
    db_ = testdata["observations-wd"].copy()
    results = db_.apply(
        lambda row: do_hard_limit_check(
            value=row["observation_value"], hard_limits=[0, 360]
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.passed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_do_wind_consistency_check(testdata):
    db_ = testdata["observations-ws"].copy()
    db2_ = testdata["observations-wd"].copy()
    db_.data["observation_value_wd"] = db2_["observation_value"]
    results = db_.apply(
        lambda row: do_wind_consistency_check(
            wind_speed=row["observation_value"],
            wind_direction=row["observation_value_wd"],
        ),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.passed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
            qc.failed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)


def test_multiple_row_check(testdata, climdata):
    db_ = testdata["observations-at"].copy()
    climatology = Climatology.open_netcdf_file(
        climdata["AT"]["mean"],
        "at",
        obs_name="AT",
        statistics="mean",
        time_axis="pentad_time",
        target_units="K",
        source_units="degC",
    )
    stdev = Climatology.open_netcdf_file(
        climdata["AT"]["stdev"],
        "at",
        obs_name="AT",
        statistics="stdev",
        time_axis="pentad_time",
    )
    qc_dict = {
        "do_missing_value_check": {"names": {"value": "observation_value"}},
        "do_no_normal_check": {
            "names": {
                "lat": "latitude",
                "lon": "longitude",
                "date": "date_time",
            },
            "arguments": {"climatology": climatology},
        },
        "do_hard_limit_check": {
            "names": {"value": "observation_value"},
            "arguments": {"hard_limits": [193.15, 338.15]},  # K
        },
        "do_anomaly_check": {
            "names": {
                "value": "observation_value",
                "lat": "latitude",
                "lon": "longitude",
                "date": "date_time",
            },
            "arguments": {
                "climatology": climatology,
                "maximum_anomaly": 10.0,  # K
            },
        },
        "do_climatology_plus_stdev_check": {
            "names": {
                "value": "observation_value",
                "lat": "latitude",
                "lon": "longitude",
                "date": "date_time",
            },
            "arguments": {
                "climatology": climatology,
                "stdev": stdev,
                "minmax_standard_deviation": [1.0, 4.0],  # K
                "maximum_standardised_anomaly": 5.5,  # K
            },
        },
    }
    results = db_.apply(
        lambda row: do_multiple_row_check(data=row, qc_dict=qc_dict),
        axis=1,
    )
    expected = pd.Series(
        [
            qc.failed,
            qc.failed,
            qc.failed,
            qc.passed,
            qc.failed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
            qc.passed,
        ]
    )
    pd.testing.assert_series_equal(results, expected)
