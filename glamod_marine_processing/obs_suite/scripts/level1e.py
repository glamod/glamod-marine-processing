"""
Created on Mon Jun 17 14:24:10 2019

See IMPORTANT NOTE!

Script to generate level1e CDM data: adding MO-QC (a.k.a. John's QC) flags

    - Reads QC files and creates unique flag per QC file (observed parameter)
      using columns from each QC file as parameterized at the very beginning.
      This is done with function get_qc_flags()
      See notes below on how QC files are expected to be

    - Creates the report_quality CDM field with function add_report_quality()
      See below notes on the rules to create it

    - Merge quality flags with CDM tables with function process_table()
      Here, additionally,  we set 'report_time_quality' to '2' to all reports

    - Log, per table, total number of records and qc flag counts

Note again that the following flagging is decided/set here, does not come from QC files:

    1) header.report_time_quality = '2', as by the time a report gets here we know
        that it is at least a valid datetime
    2) header.report_quality = following the rules in the notes below

Note also that if a report is not qced (not in QC files, like worst duplicates) we override the default
settings in the initial mappings (not all not-checked...) to not-checked with:

          -  observations*.quality_flag = '2'
          -  header.'report_time_quality' = '2'
          -  header.'report_quality' = '2'
          -  header.'location_quality' = '3'

The processing unit is the source-deck monthly set of CDM tables.

Outputs data to /<data_path>/<release>/<source>/level1e/<sid-dck>/table[i]-fileID.psv
Outputs quicklook info to:  /<data_path>/<release>/<source>/level1c/quicklooks/<sid-dck>/fileID.json

where fileID is yyyy-mm-release_tag-update_tag

Before processing starts:
    - checks the existence of all io subdirectories in level1d|e -> exits if fails
    - checks availability of the source header table -> exits if fails
    - checks existence of source observation tables -> exits if no obs tables -> requirement removed to
      give way to sid-dck monthly partitions with no obs tables
    - checks of existence of the monthly QC (POS) file -> exits if fails. See IMPORTANT NOTE!!!!
    - removes all level1e products on input file resulting from previous runs

Inargs:
-------
data_path: marine data path in file system
release: release tag
update: update tag
dataset: dataset tag
config_path: configuration file path
sid_dck: source-deck data partition (optional, from config_file otherwise)
year: data file year (yyyy) (optional, from config_file otherwise)
month: data file month (mm) (optional, from config_file otherwise)


On expected format and content of QC files:
-------------------------------------------

- qc monthly files in <data_path/<release>/<source>/metoffice_qc/base/<yyyy>/<mm>/<id>_qc_yyyymm_CCIrun.csv
  with id in [POS,SST,AT,SLP,DPT,W]
- qc monthly files assumed to have 1 hdr line (first) with column names
- qc monthly files with FS=','
- qc field names assumed as those listed in qc_columns below

Note that all the qc files have an entry per qced** report in its header table,
even if the corresponfing observed parameter does not have an entry in that report,
in which case has the 'noval' flag set to '1'

WE ASSUME HERE THAT ALL MEASURED PARAMETERS HAVE A NOVAL FLAG THAT WE USE TO
TELL APART MISSING AND FAILED

** per qced report, but duplicates are not qced....vaya caña!

Note also that since the qc files have a UID that is the imma UID, not the CDM
report_id, with the source prepended (ICOADS-30-UID for source ICOADS_R3.0.0),
and I still don't have the rules to build the CDM report_id from the source (any)
UID:

THE WAY QC-FILES UID AND CDM-TABLES REPORT_ID ARE LINKED HERE IS HARDCODED
IN FUNCTION get_qc_flags() TO RELEASE1 SOURCE ICOADS_R3.0.0T


report_quality flag rules:
--------------------------

+-----------------+--------------------+------------------------+
| POS             | PARAMS             | report_quality         |
+-----------------+--------------------+------------------------+
| passed          | all failed         | fail                   |
+-----------------+--------------------+------------------------+
|                 | rest               | pass                   |
+-----------------+--------------------+------------------------+
| failed          | all                | fail                   |
+-----------------+--------------------+------------------------+
| not checked     | at least 1 passed  | pass                   |
+-----------------+--------------------+------------------------+
| (3              | all failed         | fail                   |
+-----------------+--------------------+------------------------+
|                 | al not checked     | not checked            |
+-----------------+--------------------+------------------------+

Dev NOTES:
----------
There are some hardcoding for ICOADS_R3.0.0.T: we are looking for report_id in CDM
adding 'ICOADS_30' to the UID in the QC flags!!!!!

Maybe should pass a QC version configuration file, with the path
of the QC files relative to a set path (i.e. informing of the QC version)

.....

@author: iregon
"""

from __future__ import annotations

import copy
import logging
import os
import sys
from importlib import reload

import pandas as pd
from _qc_utilities import do_qc
from _utilities import (
    date_handler,
    paths_exist,
    read_cdm_tables,
    save_quicklook,
    script_setup,
    write_cdm_tables,
)
from marine_qc import plot_qc_outcomes as pqo
from marine_qc.auxiliary import isvalid

reload(logging)  # This is to override potential previous config of logging


# Functions--------------------------------------------------------------------

dtype_conversion = {
    "header": {
        "platform_type": {
            "dtype": int,
        },
        "latitude": {
            "dtype": float,
        },
        "longitude": {
            "dtype": float,
        },
        "report_timestamp": {
            "dtype": "datetime",
            "format": "%Y-%m-%d %H:%M:%S",
        },
        "station_speed": {
            "dtype": float,
        },
        "station_course": {
            "dtype": float,
        },
        "report_quality": {
            "dtype": int,
        },
        "location_quality": {
            "dtype": int,
        },
        "report_time_quality": {
            "dtype": int,
        },
    },
    "observations": {
        "latitude": {
            "dtype": float,
        },
        "longitude": {
            "dtype": float,
        },
        "date_time": {
            "dtype": "datetime",
            "format": "%Y-%m-%d %H:%M:%S",
        },
        "quality_flag": {
            "dtype": int,
        },
    },
    "observations-at": {
        "observation_value": {
            "dtype": float,
        }
    },
    "observations-dpt": {
        "observation_value": {
            "dtype": float,
        }
    },
    "observations-slp": {
        "observation_value": {
            "dtype": float,
        }
    },
    "observations-sst": {
        "observation_value": {
            "dtype": float,
        }
    },
    "observations-wbt": {
        "observation_value": {
            "dtype": float,
        }
    },
    "observations-wd": {
        "observation_value": {
            "dtype": float,
        }
    },
    "observations-ws": {
        "observation_value": {
            "dtype": float,
        }
    },
}


def remove_invalid_positions(df):
    """Remove rows where latitude and/or longitude is None."""
    df.dropna(subset=["latitude", "longitude"], inplace=True)


def value_counts(series):
    """Count values in pandas Series."""
    return series.value_counts(dropna=False).to_dict()


def convert_dtypes(df, table, mode="qc"):
    """Convert data type."""
    if table == "header":
        convert_dict = dtype_conversion["header"]
    else:
        convert_dict_general = dtype_conversion["observations"]
        convert_dict_special = dtype_conversion[table]
        convert_dict = {**convert_dict_general, **convert_dict_special}
    for col, col_kwargs in convert_dict.items():
        dtype = col_kwargs["dtype"]
        if dtype == "datetime":
            fmt = col_kwargs.get("format")
            if mode == "qc":
                df[col] = pd.to_datetime(df[col], format=fmt, errors="coerce")
            elif mode == "orig":
                df[col] = df[col].dt.strftime(fmt)
        else:
            if mode == "qc":
                df[col] = df[col].astype(dtype)
            elif mode == "orig":
                decimals = col_kwargs.get("decimal_places", 0)
                df[col] = df[col].map(lambda x: f"{x:.{decimals}f}")
                df[col] = df[col].replace("nan", "null")
    return df


def update_dtypes(data_df, table):
    """Update dtypes in DataFrame."""
    if data_df.empty:
        pass
    else:
        convert_dtypes(data_df, table)
    return data_df


def get_valid_indexes(df, table):
    """Get valid indexes."""
    if df.empty:
        return pd.Index([])
    valid_indexes = isvalid(df["latitude"]) & isvalid(df["longitude"])
    if table == "header":
        valid_indexes = (
            valid_indexes
            & isvalid(df["report_timestamp"])
            & (df["report_quality"] != 6)
            & (df["report_quality"] != 1)
        )
    else:
        valid_indexes = (
            valid_indexes
            & isvalid(df["date_time"])
            & (df["quality_flag"] != 6)
            & (df["quality_flag"] != 1)
            & isvalid(df["observation_value"])
        )
    return valid_indexes


def create_consistent_datadict(
    data_dict,
    convert_dtypes=True,
    remove_invalids=False,
    drop_positions=True,
):
    """Remove report_ids without any observations."""
    report_ids = pd.Series()
    for table_in in data_dict.keys():
        if drop_positions is True:
            remove_invalid_positions(data_dict[table_in])
        if convert_dtypes is True:
            update_dtypes(data_dict[table_in], table_in)
        if remove_invalids is True:
            valid_indexes = get_valid_indexes(data_dict[table_in], table_in)
            data_dict[table_in] = data_dict[table_in].loc[valid_indexes]
        report_ids = pd.concat(
            [report_ids, data_dict[table_in]["report_id"]], ignore_index=True
        )

    report_ids = report_ids[report_ids.duplicated()]

    ql_dict = {}
    for table, df in data_dict.items():
        df = df.set_index("report_id", drop=False)
        p_length = len(df)
        valid_indexes = df.index.intersection(report_ids)
        df = df.loc[valid_indexes]

        data_dict[table] = df

        c_length = len(df)
        r_length = p_length - c_length
        ql_dict[table] = {
            "total": c_length,
            "deleted": r_length,
        }
    return data_dict, ql_dict


def update_data_dict(
    data_dict,
    report_quality,
    location_quality,
    report_time_quality,
    quality_flags,
    history,
):
    """Update data_dict with new quality flags."""
    for table in data_dict.keys():
        df = data_dict[table]
        if table == "header":
            df = data_dict[table]
            df["report_quality"] = report_quality
            df["location_quality"] = location_quality
            df["report_time_quality"] = report_time_quality
            df["history"] = history
        else:
            df["quality_flag"] = quality_flags[table]
        convert_dtypes(df, table, mode="orig")


def configure_month_params(params):
    """Configure params for both previous and next months."""
    year = int(params.year)
    month = int(params.month)
    if month == 12:
        month_next = 1
        year_next = year + 1
    else:
        month_next = month + 1
        year_next = year
    if month == 1:
        month_prev = 12
        year_prev = year - 1
    else:
        month_prev = month - 1
        year_prev = year

    year_curr = f"{params.year:04}"
    year_prev = f"{year_prev:04}"
    year_next = f"{year_next:04}"
    month_curr = f"{params.month:02}"
    month_prev = f"{month_prev:02}"
    month_next = f"{month_next:02}"

    params_prev = copy.deepcopy(params)
    params_prev.prev_fileID = params_prev.prev_fileID.replace(year_curr, year_prev)
    params_prev.prev_fileID = params_prev.prev_fileID.replace(month_curr, month_prev)
    params_next = copy.deepcopy(params)
    params_next.prev_fileID = params_next.prev_fileID.replace(year_curr, year_next)
    params_next.prev_fileID = params_next.prev_fileID.replace(month_curr, month_next)
    return params_prev, params_next


def get_qc_columns(data_dict):
    """Copy data dictionary, convert values and get quality flags."""
    quality_flags = {}
    report_quality = pd.Series()
    location_quality = pd.Series()
    report_time_quality = pd.Series()
    history = pd.Series()
    data_dict_qc = {}

    for table, df in data_dict.items():
        data_dict_qc[table] = df.copy()

        if table == "header":
            report_quality = df["report_quality"].copy()
            location_quality = df["location_quality"].copy()
            report_time_quality = df["report_time_quality"].copy()
            history = df["history"].copy()
        else:
            quality_flags[table] = df["quality_flag"].copy()

    return (
        data_dict_qc,
        report_quality,
        location_quality,
        report_time_quality,
        quality_flags,
        history,
    )


def concat_data_dicts(*dicts, dictref):
    """Concatenate data dicts."""
    dictout = {}
    dictref = {"header": {}, "observations-sst": {}}
    for table in dictref.keys():
        dfs = []
        for d in dicts:
            dfs.append(d.get(table, pd.DataFrame()))
        df = pd.concat(dfs)

        dictout[table] = df

    return dictout


def get_nearest_to_hour(series, groupby=None):
    """Get time stamps nearest to each whole hour."""
    hours = series.dt.floor("H")
    delta = (series - hours).abs()
    df = pd.DataFrame({"timestamp": series, "hour": hours, "delta": delta})

    group_keys = ["hour"]
    if groupby is not None:
        aligned_group = groupby.reindex(series.index)
        df["group"] = aligned_group.values
        group_keys = ["group"] + group_keys

    nearest = df.loc[df.groupby(group_keys)["delta"].idxmin()]

    return nearest[["timestamp"]]


def update_decimals(table_in, key):
    """Update decimal places."""
    columns = list(dtype_conversion[key].keys())
    for col in columns:
        if dtype_conversion[key][col]["dtype"] == "datetime":
            continue
        for value in data_dict[table_in][col]:
            if pd.isna(value):
                continue
            value = str(value)
            if value == "null":
                continue
            if "." in value:
                decimals = len(value.split(".")[-1])
            else:
                decimals = 0
            dtype_conversion[key][col]["decimal_places"] = decimals
            break


def create_data_dict(data_dict, tables_in, params, get_decimals=False):
    """Create data dictionary."""
    obs = False
    for table_in in tables_in:
        if table_in not in data_dict.keys():
            db_ = read_cdm_tables(params, table_in)
            if db_.empty:
                continue
            data_dict[table_in] = db_[table_in]

        if get_decimals is False:
            continue

        update_decimals(table_in, table_in)
        if table_in != "header" and obs is False:
            update_decimals(table_in, "observations")
            obs = True

    return data_dict


# MAIN ------------------------------------------------------------------------

# Process input, set up some things and make sure we can do something   -------
logging.basicConfig(
    format="%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s",
    level=logging.INFO,
    datefmt="%Y%m%d %H:%M:%S",
    filename=None,
)

process_options = [
    "qc_settings",
    "history_explain",
    "no_qc_suite",
]
params = script_setup(process_options, sys.argv)

# Some other parameters -------------------------------------------------------
obs_tables = [x for x in params.cdm_tables if x != "header"]

# -----------------------------------------------------------------------------

# DO SOME PREPROCESSING ------------------------------------------------------

# Set file path to external files
ext_path = os.path.join(params.data_path, "external_files")
paths_exist(ext_path)

# Do some additional checks before clicking go, do we have a valid header?
header_filename = params.filename
if not os.path.isfile(header_filename):
    logging.error(f"Header table file not found: {header_filename}")
    sys.exit(1)

header_db = read_cdm_tables(params, "header")

if header_db.empty:
    logging.error("Empty or non-existing header table")
    sys.exit(1)

data_dict = {}
data_dict["header"] = header_db["header"]

# See what CDM tables are available for this fileID
tables_in = ["header"]
for table in obs_tables:
    table_filename = header_filename.replace("header", table)
    if not os.path.isfile(table_filename):
        logging.warning(f"CDM table not available: {table_filename}")
        continue
    tables_in.append(table)

if len(tables_in) == 1:
    logging.error(
        f"NO OBS TABLES AVAILABLE: {params.sid_dck}, period {params.year}-{params.month}"
    )
    sys.exit(1)

data_dict = create_data_dict(data_dict, tables_in, params, get_decimals=True)

# Remove report_ids without any observations
data_dict, ql_dict = create_consistent_datadict(data_dict)

# DO THE DATA PROCESSING ------------------------------------------------------

# Update dtypes and get QC columns
(
    data_dict_qc,
    report_quality,
    location_quality,
    report_time_quality,
    quality_flags,
    history,
) = get_qc_columns(data_dict)


if params.no_qc_suite is True:
    data_dict_add = {}
    data_dict_buoy = {}
    for table, df in data_dict.items():
        data_dict_add[table] = pd.DataFrame(columns=df.columns)
        data_dict_buoy[table] = pd.DataFrame(columns=df.columns)
else:
    # Get additional data: month +/-1
    # SHIP
    params_prev, params_next = configure_month_params(params)
    data_dict_prev = create_data_dict({}, tables_in, params_prev)
    data_dict_prev, _ = create_consistent_datadict(data_dict_prev, remove_invalids=True)
    data_dict_next = create_data_dict({}, tables_in, params_prev)
    data_dict_next, _ = create_consistent_datadict(data_dict_next, remove_invalids=True)

    data_dict_add = concat_data_dicts(data_dict_prev, data_dict_next, dictref=data_dict)

    # BUOY
    params_buoy = copy.deepcopy(params)
    qc_dict = copy.deepcopy(params.qc_settings.get("grouped_reports"))
    buoy_dataset = copy.deepcopy(qc_dict.get("buoy_dataset", "None"))
    buoy_dck = copy.deepcopy(qc_dict.get("buoy_dck", "None"))

    params_buoy.prev_level_path = params_buoy.prev_level_path.replace(
        params.dataset, buoy_dataset
    )
    params_buoy.prev_level_path = params_buoy.prev_level_path.replace(
        params.sid_dck, buoy_dck
    )
    params_buoy_prev, params_buoy_next = configure_month_params(params_buoy)
    data_dict_buoy_prev = create_data_dict({}, tables_in, params_buoy_prev)
    data_dict_buoy_prev, _ = create_consistent_datadict(
        data_dict_buoy_prev, remove_invalids=True
    )
    data_dict_buoy_curr = create_data_dict({}, tables_in, params_buoy)
    data_dict_buoy_curr, _ = create_consistent_datadict(
        data_dict_buoy_curr, remove_invalids=True
    )
    data_dict_buoy_next = create_data_dict({}, tables_in, params_buoy_next)
    data_dict_buoy_next, _ = create_consistent_datadict(
        data_dict_buoy_next, remove_invalids=True
    )

    data_dict_buoy = concat_data_dicts(
        data_dict_buoy_prev, data_dict_buoy_curr, data_dict_buoy_next, dictref=data_dict
    )

    if not data_dict_buoy["header"].empty:
        ids = data_dict_buoy["header"]["primary_station_id"]
        for table, df in data_dict_buoy.items():
            if df.empty:
                continue
            if table == "header":
                time_axis = "report_timestamp"
            else:
                time_axis = "date_time"

            time_data = get_nearest_to_hour(df[time_axis], groupby=ids)
            data_dict_buoy[table] = df.loc[time_data.index]

    for table in data_dict_qc.keys():
        if table not in data_dict_add.keys():
            data_dict_add[table] = pd.DataFrame()
        if table not in data_dict_buoy.keys():
            data_dict_buoy[table] = pd.DataFrame()

# Perform QC
report_quality, location_quality, report_time_quality, quality_flags, history = do_qc(
    data_dict_qc=data_dict_qc,
    report_quality=report_quality,
    location_quality=location_quality,
    report_time_quality=report_time_quality,
    quality_flags=quality_flags,
    history=history,
    params=params,
    ext_path=ext_path,
    data_dict_add=data_dict_add,
    data_dict_buoy=data_dict_buoy,
    perform_qc=not params.no_qc_suite,
)

# Optionally, copy quality_flags
if params.no_qc_suite is False and params.qc_settings["copies"]:
    for table, table_cp in params.qc_settings["copies"].items():
        if table in data_dict.keys():
            intersec = quality_flags[table].index.intersection(
                quality_flags[table_cp].index
            )
            quality_flags[table].loc[intersec] = quality_flags[table_cp].loc[intersec]
        else:
            logging.warning(f"Could not copy {table}.")

# Update data_dict with reworked QC columns
update_data_dict(
    data_dict,
    report_quality,
    location_quality,
    report_time_quality,
    quality_flags,
    history,
)

# WRITE QC FLAGS TO DATA ------------------------------------------------------
for table, df in data_dict.items():
    if table == "header":
        ql_dict[table]["report_quality_flag"] = value_counts(df["report_quality"])
        ql_dict[table]["location_quality_flag"] = value_counts(df["location_quality"])
        ql_dict[table]["report_time_quality_flag"] = value_counts(
            df["report_time_quality"]
        )
    else:
        ql_dict[table]["quality_flag"] = value_counts(df["quality_flag"])
        pqo.latitude_variable_plot(
            df["latitude"],
            df["observation_value"],
            df["quality_flag"],
            filename=os.path.join(
                params.level_ql_path, f"{table}_{params.fileID}_lat_var.png"
            ),
        )
        pqo.latitude_longitude_plot(
            df["latitude"],
            df["longitude"],
            df["quality_flag"],
            filename=os.path.join(
                params.level_ql_path, f"{table}_{params.fileID}_lat_lon.png"
            ),
        )

    write_cdm_tables(params, df, tables=table)

# CHECKOUT --------------------------------------------------------------------
logging.info("Saving json quicklook")
save_quicklook(params, ql_dict, date_handler)
