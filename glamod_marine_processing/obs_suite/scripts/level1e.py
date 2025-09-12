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

import logging
import os
import sys
from importlib import reload

import pandas as pd
from _qc_utilities import do_qc, get_qc_columns
from _utilities import (
    date_handler,
    paths_exist,
    read_cdm_tables,
    save_quicklook,
    script_setup,
    write_cdm_tables,
)
from cdm_reader_mapper.cdm_mapper.tables.tables import get_cdm_atts

reload(logging)  # This is to override potential previous config of logging


# Functions--------------------------------------------------------------------
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
            continue

        df["quality_flag"] = quality_flags[table]


def value_counts(series):
    """Count values in pandas Series."""
    return series.value_counts(dropna=False).to_dict()


# Some other parameters -------------------------------------------------------
cdm_atts = get_cdm_atts()
obs_tables = [x for x in cdm_atts.keys() if x != "header"]

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
    df = df.loc[valid_indexes]

    data_dict[table] = df

    c_length = len(df)
    r_length = p_length - c_length
    ql_dict[table] = {
        "total": c_length,
        "deleted": r_length,
    }

# DO THE DATA PROCESSING ------------------------------------------------------
if params.no_qc_suite is not True:
    (
        data_dict_qc,
        report_quality,
        location_quality,
        report_time_quality,
        quality_flags,
        history,
    ) = get_qc_columns(data_dict)

    report_quality, location_quality, report_time_quality, quality_flags, history = (
        do_qc(
            data_dict_qc=data_dict_qc,
            report_quality=report_quality,
            location_quality=location_quality,
            report_time_quality=report_time_quality,
            quality_flags=quality_flags,
            history=history,
            params=params,
            ext_path=ext_path,
        )
    )
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

    write_cdm_tables(params, df, tables=table)

# CHECKOUT --------------------------------------------------------------------
logging.info("Saving json quicklook")
save_quicklook(params, ql_dict, date_handler)
