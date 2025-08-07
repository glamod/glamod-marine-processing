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

import datetime
import logging
import os
import sys
from importlib import reload

import numpy as np
import pandas as pd
from _utilities import (
    date_handler,
    read_cdm_tables,
    save_quicklook,
    script_setup,
    write_cdm_tables,
)
from cdm_reader_mapper.cdm_mapper.tables.tables import get_cdm_atts
from marine_qc import qc_grouped_reports, qc_individual_reports, qc_sequential_reports
from marine_qc.multiple_row_checks import do_multiple_row_check

reload(logging)  # This is to override potential previous config of logging


# Functions--------------------------------------------------------------------
def get_single_qc_flag(df):
    """Get single QC flag from DataFrame containing multiple QC flags."""
    mask_0 = (df == 0).any(axis=1)
    mask_1 = (df == 1).any(axis=1)
    mask_2 = (df == 2).any(axis=1)
    mask_3 = (df == 3).any(axis=1)

    conditions = [mask_1, mask_0, mask_2, mask_3]
    choices = [1, 0, 2, 3]
    result = np.select(conditions, choices, default=3)
    return pd.Series(result, index=df.index, name="QC_FLAG")


def compare_quality_checks(df):
    """Compare entries with location_quality and report_time_quality."""
    df = df.mask(location_quality == "2", "1")
    df = df.mask(report_time_quality == "4", "1")
    df = df.mask(report_time_quality == "5", "1")
    return df


# Some other parameters -------------------------------------------------------
cdm_atts = get_cdm_atts()
obs_tables = [x for x in cdm_atts.keys() if x != "header"]
# obs_tables = []

try:
    history_tstmp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
except AttributeError:  # for python < 3.11
    history_tstmp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

# -----------------------------------------------------------------------------

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

return_method = "failed"

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
    sys.exit()

# Remove report_ids without any observations
report_ids = pd.Series()
for table_in in tables_in:
    if table_in not in data_dict.keys():
        db_ = read_cdm_tables(params, table_in)
        if db_.empty:
            continue
        data_dict[table_in] = db_[table_in]
    report_ids = pd.concat(
        [report_ids, data_dict[table_in]["report_id"]], ignore_index=True
    )

report_ids = report_ids[report_ids.duplicated()]

ql_dict = {}
for table, df in data_dict.items():
    df = df.set_index("report_id", drop=False)
    p_length = len(df)
    valid_indexes = df.index.intersection(report_ids)
    data_dict[table] = df.loc[valid_indexes]
    c_length = len(data_dict[table])
    r_length = p_length - c_length
    ql_dict[table] = {
        "total": c_length,
        "deleted": r_length,
    }

# DO SOME PREPROCESSING ------------------------------------------------------
for table in tables_in:
    if table not in data_dict.keys():
        continue
    data = data_dict[table]
    if table == "header":
        data["platform_type"] = data["platform_type"].astype(int)
        data["latitude"] = data["latitude"].astype(float)
        data["longitude"] = data["longitude"].astype(float)
        data["report_timestamp"] = pd.to_datetime(
            data["report_timestamp"],
            format="%Y-%m-%d %H:%M:%S",
            errors="coerce",
        )
        data["station_speed"] = data["station_speed"].astype(float)
        data["station_course"] = data["station_course"].astype(float)
        data["report_quality"] = data["report_quality"].astype(int)
        data["location_quality"] = data["location_quality"].astype(int)
        data["report_time_quality"] = data["report_time_quality"].astype(int)
    else:
        data["observation_value"] = data["observation_value"].astype(float)
        data["latitude"] = data["latitude"].astype(float)
        data["longitude"] = data["longitude"].astype(float)
        data["date_time"] = pd.to_datetime(
            data["date_time"],
            format="%Y-%m-%d %H:%M:%S",
            errors="coerce",
        )
        data["quality_flag"] = data["quality_flag"].astype(int)

# DO THE DATA PROCESSING ------------------------------------------------------

# 1. Observational checks
logging.info("1. Do individual checks")
# 1.1. Header
logging.info("1.1. Do header checks")
header_df = data_dict["header"].copy()
idx_blck = header_df[header_df["report_quality"] == 6].index
idx_gnrc = header_df[header_df["report_quality"] == 88].index

# Deselect rows on blacklist
data = header_df.drop(index=idx_blck)

# Select header quality flags
report_quality = data["report_quality"].copy()
location_quality = data["location_quality"].copy()
report_time_quality = data["report_time_quality"].copy()

# 1.1.1. Position check
logging.info("1.1.1. Do positional checks")
# Deselect already failed location_qualities
data_pos = data[~location_quality.isin([2])]
idx_pos = data_pos.index

# Do position check
qc_dict = params.qc_settings.get("position_check", {}).get("header", {})
pos_qc = do_multiple_row_check(
    data=data_pos,
    qc_dict=qc_dict,
    return_method=return_method,
)
pos_qc = get_single_qc_flag(pos_qc)
location_quality.loc[idx_pos] = pos_qc

# 1.1.2. Time check
logging.info("1.1.2. Do time checks")
# Deselect already failed report_time_qualities
data_time = data[~report_time_quality.isin([4, 5])]
idx_time = data_time.index

# Do time check
qc_dict = params.qc_settings.get("time_check", {}).get("header", {})
time_qc = do_multiple_row_check(
    data=data_time,
    qc_dict=qc_dict,
    return_method=return_method,
)
time_qc = get_single_qc_flag(time_qc)
report_time_quality.loc[idx_time] = time_qc

# 1.1.3. Report quality
logging.info("1.1.3. Set report quality")
report_quality = compare_quality_checks(report_time_quality)

# 1.2. Observations
logging.info("1.2. Do observations checks")
quality_flags = {}
# 1.2.1. Do observation check
for obs_table in obs_tables:
    if obs_table not in data_dict.keys():
        continue
    logging.info(f"1.2.1. Do {obs_table} check")
    data = data_dict[obs_table].copy()
    # Select observation quality_flag
    quality_flag = data["quality_flag"]
    quality_flag.loc[idx_blck] = 6

    # Deselect rows on blacklist
    data = data.drop(index=idx_blck)

    # Deselect already failed quality_flags
    data_qc = data[~quality_flag.isin([1])]
    # Deselect already failed report_qualities
    data_qc = data_qc[~report_quality.isin([1])]
    idx_qc = data_qc.index

    preproc_dict = params.qc_settings.get("preprocessing", {}).get(obs_table, {})
    qc_dict = params.qc_settings.get("observations_check", {}).get(obs_table, {})
    obs_qc = do_multiple_row_check(
        data=data_qc,
        preproc_dict=preproc_dict,
        qc_dict=qc_dict,
        return_method=return_method,
    )
    obs_qc = get_single_qc_flag(obs_qc)

    # Flag quality_flag
    quality_flag.loc[idx_qc] = obs_qc["QC_FLAG"]
    quality_flags[obs_table] = compare_quality_checks(quality_flag)

# 1.2.2. Do combined observation check
qc_dict = params.qc_settings.get("observations_check", {}).get("combined", {})
for qc_name in qc_dict.keys():
    logging.info(f"1.2.2. Do {qc_name} check")
    func = getattr(qc_individual_reports, qc_dict[qc_name]["func"])
    tables = qc_dict[qc_name]["tables"]
    names = qc_dict[qc_name]["names"]
    inputs = {}
    for ivar, table in tables.items():
        data = data_dict[table].copy()
        column = names[ivar]
        inputs[ivar] = data[column]
    qc_flag = func(**inputs)
    idx_failed = qc_flag[qc_flag.isin([1])].index
    for table in tables.values():
        quality_flags[table].loc[idx_failed] = qc_flag.loc[idx_failed]

exit()
# 2. Track check
# 2.1. Header
# Deselect rows on blacklist
data = header_df.drop(index=idx_blck)
# Deselect already failed report_qualities
data = data[~report_quality.isin([[1]])]
# Deselect rows containing generic ids
data = data.drop(index=idx_gnrc)

qc_dict = params.qc_settings.get("track_check", {}).get("header", {})
for qc_name in qc_dict.keys():
    func = getattr(qc_sequential_reports, qc_dict[qc_name]["func"])
    names = qc_dict[qc_name].get("names", {})
    inputs = {k: data[v] for k, v in names.items()}
    kwargs = qc_dict[qc_name].get("arguments", {})
    track_qc = func(**inputs, **kwargs)
    idx_failed = track_qc[track_qc.isin([1])].index
    report_quality.loc[idx_failed] = track_qc.loc[idx_failed]

# 2.2. Observations
# 2.2.1. Do observation track check
qc_dict = params.qc_settings.get("track_check", {}).get("observations", {})
for obs_table in obs_tables:
    if obs_table not in data_dict.keys():
        continue
    quality_flag = quality_flags[obs_table]
    data = data_dict[obs_table].copy()
    # Deselect already failed quality_flags
    data = data[~quality_flag.isin([1])]
    # Deselect rows on blacklist
    data = data.drop(index=idx_blck)
    # Deselect rows containing generic ids
    data = data.drop(index=idx_gnrc)

    for qc_name in qc_dict.keys():
        func = getattr(qc_sequential_reports, qc_dict[qc_name]["func"])
        names = qc_dict[qc_name].get("names", {})
        inputs = {k: data[v] for k, v in names.items()}
        kwargs = qc_dict[qc_name].get("arguments", {})
        qc_flag = func(**inputs, **kwargs)
        idx_failed = qc_flag[qc_flag.isin([1])].index
        quality_flag.loc[idx_failed] = qc_flag.loc[idx_failed]
    quality_flags[obs_table] = quality_flag
    print(quality_flag)
    exit()
# 2.2.2. Do combined observations track check
qc_dict = params.qc_settings.get("track_check", {}).get("combined", {})
for qc_name in qc_dict.keys():
    func = getattr(qc_sequential_reports, qc_dict[qc_name]["func"])
    tables = qc_dict[qc_name]["tables"]
    names = qc_dict[qc_name]["names"]
    kwargs = qc_dict[qc_name]["arguments"]
    inputs = {}
    for ivar, table in tables.items():
        data = data_dict[table].copy()
        column = names[ivar]
        inputs[ivar] = data[column]
    # qc_flag = func(**inputs, **kwargs)
    # idx_failed = qc_flag[qc_flag.isin([1])].index
    # for table in tables.values():
    #    quality_flags[table].loc[idx_failed] = qc_flag.loc[idx_failed]

# 3. Buddy check
qc_dict = params.qc_settings.get("buddy_check", {}).get("observations", {})
for obs_table in obs_tables:
    if obs_table not in data_dict.keys():
        continue
    quality_flag = quality_flags[obs_table]
    data = data_dict[obs_table].copy()
    # Deselect already failed quality_flags
    data = data[~quality_flag.isin([1])]
    # Deselect on blacklist
    data = data.drop(index=idx_blck)
    # Deselect rows containing generic ids
    data = data.drop(index=idx_gnrc)
    for qc_name in qc_dict.keys():
        func = getattr(qc_grouped_reports, qc_dict[qc_name]["func"])
        names = qc_dict[qc_name].get("names", {})
        inputs = {k: data[v] for k, v in names.items()}
        kwargs = qc_dict[qc_name].get("arguments", {})
        qc_flag = func(**inputs, **kwargs)
        idx_failed = qc_flag[qc_flag.isin([1])].index
        quality_flag.loc[idx_failed] = qc_flag.loc[idx_failed]
    quality_flags[obs_table] = quality_flag

# WRITE QC FLAGS TO DATA ------------------------------------------------------
history_add = f";{history_tstmp}. {params.history_explain}"
header_df["location_quality"] = location_quality
header_df["report_time_quality"] = report_time_quality
header_df["report_quality"] = report_quality
ql_dict["header"]["location_quality_flag"] = location_quality.value_counts(
    dropna=False
).to_dict()
ql_dict["header"]["report_quality_flag"] = report_quality.value_counts(
    dropna=False
).to_dict()
ql_dict["header"]["report_time_quality_flag"] = report_time_quality.value_counts(
    dropna=False
).to_dict()
header_df.update(
    header_df.loc[~header_df.index.isin(idx_blck), "history"].apply(
        lambda x: x + history_add
    )
)
write_cdm_tables(params, header_df, tables="header")

for obs_table in obs_tables:
    obs_df = data_dict[obs_table].copy()
    obs_df["quality_flag"] = quality_flags[obs_table]
    ql_dict[obs_table]["quality_flag"] = (
        obs_df["quality_flag"].value_counts(dropna=False).to_dict()
    )
    write_cdm_tables(params, obs_df, tables=obs_table)

# ?. PROCESS QC FLAGS ---------------------------------------------------------
# Replace QC flags in C-RAID data; other approach needed!!!
# pass_time = None
# if params.no_qc_suite:
#    qc_avail = True
#    # Set report_quality to passed if report_quality is not checked
#    qc_df["report_quality"] = header_db["report_quality"]
#    qc_df["report_quality"] = qc_df["report_quality"].mask(
#        qc_df["report_quality"] == "2", "0"
#    )
#    pass_time = header_db["report_time_quality"]
#
# qc_df = qc_df[qc_df.index.isin(report_ids)]

# CHECKOUT --------------------------------------------------------------------
logging.info("Saving json quicklook")
save_quicklook(params, ql_dict, date_handler)
