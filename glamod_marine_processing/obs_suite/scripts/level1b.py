"""
Created on Mon Jun 17 14:24:10 2019

Script to generate the C3S CDM Marine level1b data:

    - read linkage and duplicate identification output (previously pre-processed)
    - merge with CDM tables on record_id
    - re-assign dates
    - save tables to ascii

Uses modules cdm and pandas_operations to read CDM tables and handle corrections

The processing unit is the source-deck monthly set of CDM observation tables (header + observations-...).

Outputs data to /<data_path>/<release>/<dataset>/level1b/<sid-dck>/table[i]-fileID.psv
Outputs quicklook info to:  /<data_path>/<release>/<dataset>/level1b/quicklooks/<sid-dck>/fileID.json
where fileID is yyyy-mm-release_tag-update_tag

If any data in dataset yyyy-mm is identified to be in a different yyyy-mm (mainly after datetime corrections):
Outputs data to /<data_path>/<release>/<dataset>/level1b/<sid-dck>/table[i]-fileLeakID.psv
where fileLeakID is yyyy-mm(real)-release_tag-update_tag-yyyy-mm(dataset)

Before processing starts:
    - checks the existence of all io subdirectories in level1a|b -> exits if fails
    - checks the existence of the dataset table to be converted (header only) -> exits if fails
    - removes all level1b products on input file resulting from previous runs

Inargs:
-------
data_path: marine data path in file system
release: release tag
update: udpate tag
dataset: dataset tag
config_path: configuration file path
sid_dck: source-deck data partition (optional, from config_file otherwise)
year: data file year (yyyy) (optional, from config_file otherwise)
month: data file month (mm) (optional, from config_file otherwise)


configfile includes:
--------------------
- NOC_corrections version
- CDM tables elements with subdirectory prefix where corrections are in release/NOC_corrections/version
- subdirectory prefix with history event to append to history field

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
import simplejson
from _utilities import (
    FFS,
    date_handler,
    delimiter,
    paths_exist,
    script_setup,
    table_to_csv,
)
from cdm_reader_mapper import cdm_mapper as cdm
from cdm_reader_mapper.operations import replace

reload(logging)  # This is to override potential previous config of logging


# MAIN ------------------------------------------------------------------------
# Process input and set up some things ----------------------------------------
logging.basicConfig(
    format="%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s",
    level=logging.INFO,
    datefmt="%Y%m%d %H:%M:%S",
    filename=None,
)
if len(sys.argv) > 1:
    logging.info("Reading command line arguments")
    args = sys.argv
else:
    logging.error("Need arguments to run!")
    sys.exit(1)

process_options = ["correction_version", "corrections", "histories", "ignore_columns"]
params = script_setup(process_options, args, "level1b", "level1a")

cor_ext = ".txt.gz"

L1b_main_corrections = os.path.join(
    params.data_path, params.release, "NOC_corrections", params.correction_version
)

logging.info(f"Setting corrections path to {L1b_main_corrections}")
if params.correction_version != "null":
    paths_exist(L1b_main_corrections)

correction_dict = {table: {} for table in cdm.properties.cdm_tables}

# Do the data processing ------------------------------------------------------
isChange = "1"
dupNotEval = "4"
cdm_tables = cdm.get_cdm_atts()

# 1. Do it a table at a time....
history_tstmp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
for table in cdm.properties.cdm_tables:
    datetime_col = "report_timestamp" if table == "header" else "date_time"
    logging.info(params.prev_level_path)
    logging.info(params.prev_fileID)
    logging.info(table)
    table_df = cdm.read_tables(
        params.prev_level_path, params.prev_fileID, cdm_subset=[table]
    )
    if len(table_df) == 0:
        logging.warning(f"Empty or non-existing table {table}")
        correction_dict[table]["read"] = 0
        continue

    table_df.set_index("report_id", inplace=True, drop=False)
    correction_dict[table]["read"] = len(table_df)

    if params.corrections is None:
        table_corrections = {}
    else:
        table_corrections = params.corrections.get(table)
    if len(table_corrections) == 0:
        logging.warning(f"No corrections defined for table {table}")

    correction_dict[table]["date leak out"] = {}
    correction_dict[table]["corrections"] = {}

    for correction, element in table_corrections.items():
        correction_dict[table]["corrections"][element] = {"applied": 1, "number": 0}
        logging.info(f"Applying corrections for element {element}")
        columns = ["report_id", element, element + ".isChange"]
        if params.correction_version != "null":

            cor_path = os.path.join(
                L1b_main_corrections, correction, params.fileID_date + cor_ext
            )
            if not os.path.isfile(cor_path):
                logging.warning(f"Correction file {cor_path} not found")
                continue

            correction_df = pd.read_csv(
                cor_path,
                delimiter=delimiter,
                dtype="object",
                header=None,
                usecols=[0, 1, 2],
                names=columns,
                quotechar=None,
                quoting=3,
            )
        else:
            correction_df = pd.Dataframe(columns=columns)
        if len(correction_df) > 0:
            correction_df.set_index("report_id", inplace=True, drop=False)
            try:
                correction_df = correction_df.loc[table_df.index].drop_duplicates()
            except Exception:
                logging.warning(
                    logging.warning(f"No {correction} corrections matching")
                )
                continue

        correction_dict[table]["corrections"][element]["applied"] = 0
        table_df[element + ".former"] = table_df[element]
        table_df[element + ".isChange"] = ""
        table_df = replace.replace_columns(
            table_df,
            correction_df,
            pivot_c="report_id",
            rep_c=[element, element + ".isChange"],
        )
        table_df.set_index(
            "report_id", inplace=True, drop=False
        )  # because it gets reindexed in every replacement....
        replaced = table_df[element + ".isChange"] == isChange

        not_replaced = table_df[element + ".isChange"] != isChange
        table_df[element].loc[not_replaced] = table_df[element + ".former"].loc[
            not_replaced
        ]
        correction_dict[table]["corrections"][element]["number"] = len(
            np.where(replaced)[0]
        )
        logging.info(
            "No. of corrections applied {}".format(
                correction_dict[table]["corrections"][element]["number"]
            )
        )
        # THIS IS A DIRTY THNIG TO DO, BUT WILL LEAVE IT AS IT IS FOR THIS RUN:
        # we only keep a lineage of the changes applied to the header
        # (some of these are shared with obs tables like position and datetime, although the name for the cdm element might not be the same....)
        if table == "header":
            table_df["history"].loc[replaced] = (
                table_df["history"].loc[replaced]
                + f"; {history_tstmp}. {params.histories.get(correction)}"
            )

        table_df.drop(element + ".former", axis=1)
        table_df.drop(element + ".isChange", axis=1)

    # Track duplicate status
    if table == "header":
        correction_dict["duplicates"] = {}
        if params.correction_version == "null":
            DupDetect = cdm.duplicate_check(
                table_df, ignore_columns=params.ignore_columns
            )
            DupDetect.flag_duplicates()
            table_df = DupDetect.result
        contains_info = table_df["duplicate_status"] != dupNotEval
        logging.info("Logging duplicate status info")
        if len(np.where(contains_info)[0]) > 0:
            counts = table_df["duplicate_status"].value_counts()
            for k in counts.index:
                correction_dict["duplicates"][k] = int(
                    counts.loc[k]
                )  # otherwise prints null to json!!!
        else:
            correction_dict["duplicates"][dupNotEval] = correction_dict[table]["read"]

    # Now get ready to write out, extracting eventual leaks of data to a different monthly table
    cdm_columns = cdm_tables.get(table).keys()
    # BECAUSE LIZ'S datetimes have UTC info:
    # ValueError: Tz-aware datetime.datetime cannot be converted to datetime64 unless utc=True
    table_df["monthly_period"] = pd.to_datetime(
        table_df[datetime_col], errors="coerce", utc=True
    ).dt.to_period("M")
    monthly_periods = list(table_df["monthly_period"].dropna().unique())
    source_mon_period = (
        pd.Series(data=[datetime.datetime(int(params.year), int(params.month), 1)])
        .dt.to_period("M")
        .iloc[0]
    )
    # This is to account for files with no datetime and no datetime correction: we have to assume it pertains to
    # the date in the file
    if len(monthly_periods) == 0:
        monthly_periods.append(source_mon_period)
    table_df["monthly_period"].fillna(source_mon_period, inplace=True)
    table_df.set_index("monthly_period", inplace=True, drop=True)
    len_df = len(table_df)
    if source_mon_period in monthly_periods:
        logging.info(
            "Writing {} data to {} table file".format(
                source_mon_period.strftime("%Y-%m"), table
            )
        )
        filename = os.path.join(
            params.level_path, FFS.join([table, params.fileID]) + ".psv"
        )
        table_to_csv(
            table_df.loc[[source_mon_period], :], filename, columns=cdm_columns
        )
        table_df.drop(source_mon_period, inplace=True)
        len_df_i = len_df
        len_df = len(table_df)
        correction_dict[table]["total"] = len_df_i - len_df
    else:
        correction_dict[table]["total"] = 0
        logging.warning(
            "No original period ({}) data found in table {} after datetime reordering".format(
                source_mon_period.strftime("%Y-%m"), table
            )
        )

    datetime_leaks = [m for m in monthly_periods if m != source_mon_period]
    if len(datetime_leaks) > 0:
        logging.info("Datetime leaks found:")
        for leak in datetime_leaks:
            logging.info(
                "Writing {} data to {} table file".format(leak.strftime("%Y-%m"), table)
            )
            L1b_idl = FFS.join(
                [
                    table,
                    leak.strftime("%Y-%m"),
                    params.release_id,
                    source_mon_period.strftime("%Y-%m"),
                ]
            )
            filename = os.path.join(params.level_path, L1b_idl + ".psv")
            table_to_csv(table_df.loc[[leak], :], filename, columns=cdm_columns)
            table_df.drop(leak, inplace=True)
            len_df_i = len_df
            len_df = len(table_df)
            correction_dict[table]["date leak out"][leak.strftime("%Y-%m")] = (
                len_df_i - len_df
            )
        correction_dict[table]["date leak out"]["total"] = sum(
            [v for k, v in correction_dict[table]["date leak out"].items()]
        )
    else:
        correction_dict[table]["date leak out"]["total"] = 0


correction_dict["date processed"] = datetime.datetime.now()

logging.info("Saving json quicklook")
L1b_io_filename = os.path.join(params.level_ql_path, params.fileID + ".json")
with open(L1b_io_filename, "w") as fileObj:
    simplejson.dump(
        {"-".join([params.year, params.month]): correction_dict},
        fileObj,
        default=date_handler,
        indent=4,
        ignore_nan=True,
    )
