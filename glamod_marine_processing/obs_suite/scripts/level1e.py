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
    paths_exist,
    read_cdm_tables,
    save_quicklook,
    script_setup,
    write_cdm_tables,
)
from cdm_reader_mapper.cdm_mapper.tables.tables import get_cdm_atts

reload(logging)  # This is to override potential previous config of logging


# Functions--------------------------------------------------------------------
# This is to get the unique flag per parameter
def get_qc_flags(qc, qc_df_full):
    """Get QC flag."""
    qc_avail = True
    bad_flag = "1" if qc != "POS" else "2"
    good_flag = "0"
    qc_filename = os.path.join(
        qc_path,
        params.year,
        params.month,
        "_".join([qc, "qc", params.year + params.month, "CCIrun.csv"]),
    )
    logging.info(f"Reading {qc} qc file: {qc_filename}")
    qc_df = pd.read_csv(
        qc_filename,
        dtype=qc_dtype,
        usecols=qc_columns.get(qc),
        delimiter=qc_delimiter,
        on_bad_lines="skip",
    )
    # Map UID to CDM (hardcoded source ICOADS_R3.0.0T here!!!!!)
    # and keep only reports from current monthly table
    # qc_df['UID'] = 'ICOADS-30-' + qc_df['UID']
    qc_df.set_index("UID", inplace=True, drop=True)
    qc_df = qc_df.reindex(header_db.index)
    if len(qc_df.dropna(how="all")) == 0:
        # We can have files with nothing other than duplicates (which are not qced):
        # set qc to not available but don't fail: keep on generating level1e product afterwards
        logging.warning(f"No {qc} flags matching")
        qc_avail = False
        return qc_avail, qc_df_full

    locs_notna = qc_df.notna().all(axis=1)
    qc_df.loc[locs_notna, "total"] = qc_df.loc[locs_notna].sum(axis=1)
    qc_df.loc[locs_notna, "global"] = qc_df["total"].apply(
        lambda x: good_flag if x == 0 else bad_flag
    )
    qc_df.rename({"global": qc}, axis=1, inplace=True)
    # For measured params, eliminate resulting quality_flag when that parameter
    # is not available in a report ('noval'==1)
    # Mixing failing and missing is annoying for several things afterwards
    if qc != "POS":
        qc_df.loc[qc_df["noval"] == "1", qc] = np.nan
    qc_df_full[qc] = qc_df[qc]
    return qc_avail, qc_df_full


def add_report_quality(qc_df_full):
    """Add report quality."""
    failed_location = "2"
    pass_report = "0"
    failed_report = "1"
    not_checked_report = "2"
    # Initialize to not checked: there were lots of discussions with this!
    # override ICOADS IRF flag if not checked in C3S system? In the end we said yes.
    qc_df_full["report_quality"] = not_checked_report
    # First: all observed params fail -> report_quality = '1'
    qc_param = [x for x in qc_list if x != "POS"]
    qc_param_applied = qc_df_full[qc_param].count(axis=1)
    qc_param_sum = qc_df_full[qc_param].astype(float).sum(axis=1)
    qc_df_full.loc[
        (qc_param_sum >= qc_param_applied) & (qc_param_applied > 0), "report_quality"
    ] = failed_report
    # Second: at least one observed param passed -> report_quality = '0'
    qc_df_full.loc[qc_param_sum < qc_param_applied, "report_quality"] = pass_report
    # Third: POS qc fails, no matter how good the observed params are -> report_quality '1'
    qc_df_full.loc[qc_df_full["POS"] == failed_location, "report_quality"] = (
        failed_report
    )
    return qc_df_full


def compare_quality_checks(df):
    """Compare entries with location_quality and report_time_quality."""
    df = df.mask(location_quality == "2", "1")
    df = df.mask(report_time_quality == "4", "1")
    df = df.mask(report_time_quality == "5", "1")
    return df


# This is to apply the qc flags and write out flagged tables
def process_table(table_df, table, pass_time=None):
    """Process table."""
    if pass_time is None:
        pass_time = "2"
    not_checked_report = "2"
    not_checked_location = "3"
    not_checked_param = "2"
    logging.info(f"Processing table {table}")

    if isinstance(table_df, str):
        # Assume 'header' and in a DF in table_df otherwise
        # Open table and reindex
        table_df = read_cdm_tables(params, table)

        if table_df is None or table_df.empty:
            logging.warning(f"Empty or non existing table {table}")
            return
        table_df = table_df[table].set_index("report_id", drop=False)

    previous = len(table_df)
    table_df = table_df[table_df["report_id"].isin(report_ids)]
    total = len(table_df)
    removed = previous - total
    ql_dict[table] = {
        "total": total,
        "deleted": removed,
    }
    if table_df.empty:
        logging.warning(f"Empty table {table}.")
        return

    if flag:
        qc = table_qc.get(table).get("qc")
        element = table_qc.get(table).get("element")
        qc_table = qc_df[[qc]]
        qc_table = qc_table.rename({qc: element}, axis=1)
        table_df.update(qc_table)

        updated_locs = qc_table.loc[qc_table.notna().all(axis=1)].index

        if table != "header":
            ql_dict[table]["quality_flag"] = (
                table_df[element].value_counts(dropna=False).to_dict()
            )

        if table == "header":
            table_df.update(qc_df["report_quality"])
            history_add = f";{history_tstmp}. {params.history_explain}"
            table_df.loc[:, "report_time_quality"] = pass_time
            ql_dict[table]["location_quality_flag"] = (
                table_df["location_quality"].value_counts(dropna=False).to_dict()
            )
            ql_dict[table]["report_quality_flag"] = (
                table_df["report_quality"].value_counts(dropna=False).to_dict()
            )
            table_df.update(
                table_df.loc[updated_locs, "history"].apply(lambda x: x + history_add)
            )
    # Here very last minute change to account for reports not in QC files:
    # need to make sure it is all not-checked!
    # Test new things with 090-221. See 1984-03.
    # What happens if not POS flags matching?
    else:
        if table != "header":
            table_df.loc[:, "quality_flag"] = not_checked_param
        else:
            table_df.loc[:, "report_time_quality"] = pass_time
            table_df.loc[:, "report_quality"] = not_checked_report
            table_df.loc[:, "location_quality"] = not_checked_location

    if table != "header":
        table_df.loc[:, "quality_flag"] = compare_quality_checks(
            table_df["quality_flag"]
        )
    if table == "header":
        table_df.loc[:, "report_quality"] = compare_quality_checks(
            table_df["report_quality"]
        )

    write_cdm_tables(params, table_df, tables=table)


# ------------------------------------------------------------------------------

# PARAMETERIZE HOW TO HANDLE QC FILES AND HOW TO APPLY THESE TO THE CDM FIELDS-
# -----------------------------------------------------------------------------
# 1. These are the columns we actually use from the qc files, regardless of the
# existence of others. These names must be the same as the ones in the QC file
# header (1st line)
qc_columns = dict()
qc_columns["SST"] = ["UID", "bud", "clim", "nonorm", "freez", "noval", "hardlimit"]
qc_columns["AT"] = [
    "UID",
    "bud",
    "clim",
    "nonorm",
    "noval",
    "mat_blacklist",
    "hardlimit",
]
qc_columns["SLP"] = ["UID", "bud", "clim", "nonorm", "noval"]
qc_columns["DPT"] = ["UID", "bud", "clim", "nonorm", "ssat", "noval", "rep", "repsat"]
qc_columns["POS"] = ["UID", "trk", "date", "time", "pos", "blklst"]
qc_columns["W"] = ["UID", "noval", "hardlimit", "consistency", "wind_blacklist"]

# 2. This is to what table-element pair each qc file is pointing to
qc_cdm = {
    "SST": ("observations-sst", "quality_flag"),
    "SLP": ("observations-slp", "quality_flag"),
    "AT": ("observations-at", "quality_flag"),
    "DPT": [("observations-dpt", "quality_flag"), ("observations-wbt", "quality_flag")],
    "W": [("observations-ws", "quality_flag"), ("observations-wd", "quality_flag")],
    "POS": ("header", "location_quality"),
}

# 3. This is the same as above but with different indexing,
# to ease certain operations
table_qc = {}
for k, v in qc_cdm.items():
    if isinstance(v, list):
        for t in v:
            table_qc[t[0]] = {"qc": k, "element": t[1]}
    else:
        table_qc[v[0]] = {"qc": k, "element": v[1]}

qc_dtype = {"UID": "object"}
qc_delimiter = ","
# -----------------------------------------------------------------------------

# Some other parameters -------------------------------------------------------
cdm_atts = get_cdm_atts()
obs_tables = [x for x in cdm_atts.keys() if x != "header"]

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
    "history_explain",
    "qc_first_date_avail",
    "qc_last_date_avail",
    "no_qc_suite",
]
params = script_setup(process_options, sys.argv)

if params.year_init:
    setattr(params, "qc_first_date_avail", f"{params.year_init}-01")
if params.year_end:
    setattr(params, "qc_last_date_avail", f"{params.year_end}-12")
qc_path = os.path.join(params.data_path, params.release, "metoffice_qc", "base")

# Check we have all the dirs!
paths_exist(qc_path)

# Check we have QC files!
logging.info(f"Using qc files in {qc_path}")
qc_pos_filename = os.path.join(
    qc_path,
    params.year,
    params.month,
    "_".join(["POS", "qc", params.year + params.month, "CCIrun.csv"]),
)
qc_avail = True
if not os.path.isfile(qc_pos_filename):
    file_date = datetime.datetime.strptime(
        str(params.year) + "-" + str(params.month), "%Y-%m"
    )
    last_date = datetime.datetime.strptime(params.qc_last_date_avail, "%Y-%m")
    first_date = datetime.datetime.strptime(params.qc_first_date_avail, "%Y-%m")
    if file_date > last_date or file_date < first_date:
        qc_avail = False
        logging.warning(
            f"QC only available in period {str(params.qc_first_date_avail)} to {str(params.qc_last_date_avail)}"
        )
        logging.warning("level1e data will be created with no merging")
    else:
        logging.warning(f"POSITION QC file not found: {qc_pos_filename}")
        qc_avail = False

# Do some additional checks before clicking go, do we have a valid header?
header_filename = params.filename
if not os.path.isfile(header_filename):
    logging.error(f"Header table file not found: {header_filename}")
    sys.exit(1)

header_db = read_cdm_tables(params, "header")["header"]

if header_db.empty:
    logging.error("Empty or non-existing header table")
    sys.exit(1)

# See what CDM tables are available for this fileID
tables_in = ["header"]
for table in obs_tables:
    table_filename = header_filename.replace("header", table)
    if not os.path.isfile(table_filename):
        logging.warning(f"CDM table not available: {table_filename}")
    else:
        tables_in.append(table)

if len(tables_in) == 1:
    logging.error(
        f"NO OBS TABLES AVAILABLE: {params.sid_dck}, period {params.year}-{params.month}"
    )
    sys.exit()

# Remove report_ids without any observations
report_ids = pd.Series()
for table_in in tables_in:
    db_ = read_cdm_tables(params, table_in)
    if not db_.empty:
        db_ = db_[table_in]
        report_ids = pd.concat([report_ids, db_["report_id"]], ignore_index=True)
report_ids = report_ids[report_ids.duplicated()]

# DO THE DATA PROCESSING ------------------------------------------------------
header_db.set_index("report_id", inplace=True, drop=False)
ql_dict = {}

# 1. PROCESS QC FLAGS ---------------------------------------------------------
# GET THE QC FILES WE NEED FOR THE CURRENT SET OF CDM TABLES
# AND CREATE A DF WITH THE UNIQUE FLAGS PER QC AND HAVE IT INDEXED TO FULL CDM
# TABLE (ALL REPORTS)
# ALSO BUILD FROM FULL QC FLAGS SET THE REPORT_QUALITY FLAG
qc_list = list({table_qc.get(table).get("qc") for table in tables_in})
qc_df = pd.DataFrame(index=header_db.index, columns=qc_list)
if qc_avail:
    # Make sure POS is first as we need it to process the rest!
    # The use of POS in other QCs is probably a need inherited from BetaRelease,
    # where param qc was merged with POS QC. Now we don't do that, so I am quite
    # positive we don't use POS in assigning quality_flag in obs table
    qc_list.remove("POS")
    qc_list.insert(0, "POS")
    for qc in qc_list:
        qc_avail, qc_df = get_qc_flags(qc, qc_df)
        if not qc_avail:
            break

if qc_avail:
    qc_df = add_report_quality(qc_df)

pass_time = None
if params.no_qc_suite:
    qc_avail = True
    # Set report_quality to passed if report_quality is not checked
    qc_df["report_quality"] = header_db["report_quality"]
    qc_df["report_quality"] = qc_df["report_quality"].mask(
        qc_df["report_quality"] == "2", "0"
    )
    pass_time = header_db["report_time_quality"]

qc_df = qc_df[qc_df.index.isin(report_ids)]

# 2. APPLY FLAGS, LOOP THROUGH TABLES -----------------------------------------

# Test new things with 090-221. See 1984-03. What happens if not POS flags matching?
# Need to make sure we override with 'not-checked'(2 or 3 depending on element!) default settings:
#    header.report_quality = default ICOADS IRF flag to not-checked ('2')
#    observations.quality_flag = default not-checked ('2') to not-checked('2')
#    header.location_quality = default not-checked ('3') to not-checked('3')

# First header, then rest.
location_quality = header_db["location_quality"].copy()
report_time_quality = header_db["report_time_quality"].copy()

flag = True if qc_avail else False
process_table(header_db, "header", pass_time=pass_time)
for table in obs_tables:
    flag = True if table in tables_in and qc_avail else False
    process_table(table, table, pass_time=pass_time)

# CHECKOUT --------------------------------------------------------------------
logging.info("Saving json quicklook")
save_quicklook(params, ql_dict, date_handler)
