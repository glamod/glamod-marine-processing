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
update: update tag
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
from _utilities import (  # table_to_csv,
    FFS,
    date_handler,
    delimiter,
    paths_exist,
    read_cdm_tables,
    save_quicklook,
    script_setup,
    write_cdm_tables,
)
from cdm_reader_mapper.cdm_mapper import properties

reload(logging)  # This is to override potential previous config of logging


def drop_qualities(df, drop_dict):
    """Drop rows with bad quality flags."""
    for column, values in drop_dict.items():
        if not isinstance(values, list):
            values = [values]
        df = df[~df[column].isin(values)]

    return df


# MAIN ------------------------------------------------------------------------
# Process input and set up some things ----------------------------------------
logging.basicConfig(
    format="%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s",
    level=logging.INFO,
    datefmt="%Y%m%d %H:%M:%S",
    filename=None,
)

process_options = [
    "correction_version",
    "corrections",
    "histories",
    "duplicates",
    "drop_qualities",
]
params = script_setup(process_options, sys.argv)

cor_ext = ".txt.gz"
if params.corrections_mod.get("noc_version"):
    params.correction_version = params.corrections_mod.get("noc_version")

if params.corrections_mod.get("noc_path"):
    L1b_main_corrections = params.corrections_mod.get("noc_path")
    params.correction_version = "not_null"
else:
    L1b_main_corrections = os.path.join(
        params.data_path, params.release, "NOC_corrections", params.correction_version
    )

logging.info(f"Setting corrections path to {L1b_main_corrections}")
if params.correction_version != "null":
    paths_exist(L1b_main_corrections)

ql_dict = {table: {} for table in properties.cdm_tables}

# Do the data processing ------------------------------------------------------
isChange = "1"
dupNotEval = "4"

# 1. Do it a table at a time....
history_tstmp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
for table in properties.cdm_tables:
    datetime_col = (
        ("header", "report_timestamp") if table == "header" else (table, "date_time")
    )
    logging.info(params.prev_level_path)
    logging.info(params.prev_fileID)
    logging.info(table)
    table_db = read_cdm_tables(params, table)

    if table_db.empty:
        logging.warning(f"Empty or non-existing table {table}")
        ql_dict[table]["read"] = 0
        continue

    table_db.set_index((table, "report_id"), inplace=True, drop=False)
    ql_dict[table]["read"] = len(table_db)

    if params.corrections is None:
        table_corrections = {}
    else:
        table_corrections = params.corrections.get(table)
    if len(table_corrections) == 0:
        logging.warning(f"No corrections defined for table {table}")

    ql_dict[table]["date leak out"] = {}
    ql_dict[table]["corrections"] = {}

    for correction, element in table_corrections.items():
        ql_dict[table]["corrections"][element] = {"applied": 1, "number": 0}
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
        if not correction_df.empty:
            correction_df.set_index("report_id", inplace=True, drop=False)
            try:
                correction_df = correction_df.loc[table_db.index].drop_duplicates()
            except Exception:
                logging.warning(
                    logging.warning(f"No {correction} corrections matching")
                )
                continue

        ql_dict[table]["corrections"][element]["applied"] = 0
        table_db[element + ".former"] = table_db[element]
        table_db[element + ".isChange"] = ""
        table_db.replace_columns(
            correction_df,
            pivot_c="report_id",
            rep_c=[element, element + ".isChange"],
            inplace=True,
        )
        table_db.set_index(
            "report_id", inplace=True, drop=False
        )  # because it gets reindexed in every replacement....
        replaced = table_db[element + ".isChange"] == isChange

        not_replaced = table_db[element + ".isChange"] != isChange
        table_db[element].loc[not_replaced] = table_db[element + ".former"].loc[
            not_replaced
        ]
        ql_dict[table]["corrections"][element]["number"] = len(np.where(replaced)[0])
        logging.info(
            "No. of corrections applied {}".format(
                ql_dict[table]["corrections"][element]["number"]
            )
        )
        # THIS IS A DIRTY THING TO DO, BUT WILL LEAVE IT AS IT IS FOR THIS RUN:
        # we only keep a lineage of the changes applied to the header
        # (some of these are shared with obs tables like position and datetime, although the name for the cdm element might not be the same....)
        if table == "header":
            table_db["history"].loc[replaced] = (
                table_db["history"].loc[replaced]
                + f"; {history_tstmp}. {params.histories.get(correction)}"
            )

        table_db.drop(element + ".former", axis=1)
        table_db.drop(element + ".isChange", axis=1)

    if table_db.empty:
        logging.warning("Empty table {table}")
        continue
    # Track duplicate status
    if table == "header":
        ql_dict["duplicates"] = {}
        if params.correction_version == "null":
            if params.drop_qualities:
                table_db[table] = drop_qualities(table_db[table], params.drop_qualities)
            table_db.duplicate_check(**params.duplicates)
            table_db.flag_duplicates(inplace=True)
        contains_info = table_db[(table, "duplicate_status")] != dupNotEval
        logging.info("Logging duplicate status info")
        if len(np.where(contains_info)[0]) > 0:
            counts = table_db[(table, "duplicate_status")].value_counts()
            for k in counts.index:
                ql_dict["duplicates"][k] = int(
                    counts.loc[k]
                )  # otherwise prints null to json!!!
        else:
            ql_dict["duplicates"][dupNotEval] = ql_dict[table]["read"]
    # Now get ready to write out, extracting eventual leaks of data to a different monthly table
    # cdm_columns = cdm_tables.get(table).keys()
    # BECAUSE LIZ'S datetimes have UTC info:
    # ValueError: Tz-aware datetime.datetime cannot be converted to datetime64 unless utc=True
    if table_db.empty:
        continue

    table_db[(table, "monthly_period")] = pd.to_datetime(
        table_db[datetime_col], errors="coerce", utc=True
    ).dt.to_period("M")
    monthly_periods = list(table_db[(table, "monthly_period")].dropna().unique())
    source_mon_period = (
        pd.Series(data=[datetime.datetime(int(params.year), int(params.month), 1)])
        .dt.to_period("M")
        .iloc[0]
    )
    # This is to account for files with no datetime and no datetime correction: we have to assume it pertains to
    # the date in the file
    if len(monthly_periods) == 0:
        monthly_periods.append(source_mon_period)
    table_db[(table, "monthly_period")].fillna(source_mon_period, inplace=True)
    table_db.set_index((table, "monthly_period"), inplace=True, drop=True)
    len_db = len(table_db)
    if source_mon_period in monthly_periods:
        logging.info(
            "Writing {} data to {} table file".format(
                source_mon_period.strftime("%Y-%m"), table
            )
        )
        write_cdm_tables(params, table_db.loc[[source_mon_period]], tables=table)

        table_db.drop(source_mon_period, inplace=True)
        len_db_i = len_db
        len_db = len(table_db)
        ql_dict[table]["total"] = len_db_i - len_db
    else:
        ql_dict[table]["total"] = 0
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
            write_cdm_tables(
                params, table_db.loc[[leak]], tables=table, outname=filename
            )
            table_db.drop(leak, inplace=True)
            len_db_i = len_db
            len_db = len(table_db)
            ql_dict[table]["date leak out"][leak.strftime("%Y-%m")] = len_db_i - len_db
        ql_dict[table]["date leak out"]["total"] = sum(
            [v for k, v in ql_dict[table]["date leak out"].items()]
        )
    else:
        ql_dict[table]["date leak out"]["total"] = 0

logging.info("Saving json quicklook")
save_quicklook(params, ql_dict, date_handler)
