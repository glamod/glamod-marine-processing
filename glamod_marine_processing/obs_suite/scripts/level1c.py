"""
Created on Mon Jun 17 14:24:10 2019

Script to generate the C3S CDM Marine level1c data: validate
header.report_timestamp and header.primary_station_id and apply outcome to rest
of tables, rejecting reports not validating any of these two fields.

    - Read header data

    - Initialized mask for id and datetime to True

    - Validate header.report_timestamp (see Notes below)
    - Validate header.primary_station_id (see Notes below)

    - Output all reports not validating timestamp to:
        -> /level1c/invalid/sid-dck/header-fileID-report_timsetamp.psv
    - Output all reports not validating primary_station_id to:
        -> /level1c/invalid/sid-dck/header-fileID-primary_station_id.psv

    - Merge report_timestamp and primary_station_id in a single validation rule
      (fail if any fails)
    - Drop corresponding records from all tables

    - Log to json dropped per table per validated field and final number of
      records in the resulting tables
    - Log to json unique primary_station_id counts
    - Log to json primary_station_id validation rules numbers:
        1. callsings
        2. rest
        3. restored because output from Liz's process

The processing unit is the source-deck monthly set of CDM tables.

On reading the table files from the source level (1b), it read:
    1. master table file (table-yyyy-mm-release-update.psv)
    2. datetime leak files (table-yyyy-mm-release-update-YYYY-MM.psv), where
       YYYY-MM indicates the initial yyyy-mm stamp of the reports contained in that
       leak file upon arrival to level1b.

Outputs data to /<data_path>/<release>/<dataset>/level1c/<sid-dck>/table[i]-fileID.psv
Outputs invalid data to /<data_path>/<release>/<dataset>/level1c/invalid/<sid-dck>/header-fileID-<element>.psv
Outputs quicklook info to:  /<data_path>/<release>/<dataset>/level1c/quicklooks/<sid-dck>/fileID.json

where fileID is yyyy-mm-release-update

Before processing starts:
    - checks the existence of all io subdirectories in level1b|c -> exits if fails
    - checks the existence of the source table to be converted (header only) -> exits if fails
    - removes all level1c products on input file resulting from previous runs

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

Notes on validations:
---------------------
** HEADER.REPORT_TIMESTAMP VALIDATION **
This validation is just trying to convert to a datetime object the content of
the field. Where empty, this conversion (and validation) will fail.
And will be empty if during the mapping in level1a the report_timestamp could
not be built from the source data, or if there was any kind of messing in level1b
datetime corrections......

** HEADER.PRIMARY_STATION_ID VALIDATION **
Due to various reasons, the validation is done in 3 stages and using different methods:

    1. Callsign IDs: use set of validation patterns hardcoded here
    2. Rest of IDs: use set of valid patterns per dck in NOC_ANC_INFO json files
    3. All: set all that Liz's ID linkage modified to True. We are parsing the
       history field for a "Corrected primary_station_id" text...maybe it should
       read this from the level1b config file? But then we need to give this
       file as an argument....

Dev notes:
----------

1) This script is fully tailored to the idea of how validation and cleaning should
be at the time of developing it. It is not parameterized and is hardly flexible.

2) Why don't we just pick the NaN dates as invalid, instead of looking where conversion
fails?

.....

@author: iregon
"""

from __future__ import annotations

import datetime
import glob
import json
import logging
import os
import re
import sys
from importlib import reload

import numpy as np
import pandas as pd
from _utilities import (
    FFS,
    date_handler,
    paths_exist,
    read_cdm_tables,
    save_quicklook,
    script_setup,
    write_cdm_tables,
)
from cdm_reader_mapper.cdm_mapper import properties

reload(logging)  # This is to override potential previous config of logging


def validate_id(idSeries):
    """Validate ID."""
    json_file = os.path.join(id_validation_path, "dck" + params.dck + ".json")
    if not os.path.isfile(json_file):
        logging.warning(f"NO noc ancillary info file {json_file} available")
        logging.warning("Adding match-all regex to validation patterns")
        patterns = [".*?"]
    else:
        logging.info(f"Reading ID validation patterns from NOC ANC FILE {json_file}")
        try:
            with open(json_file) as fO:
                jDict = json.load(fO)

            valid_patterns = jDict.get("patterns")
            patterns = list(valid_patterns.values())
        except Exception:
            logging.error(f"Error reading NOC ANC FILE {json_file}", exc_info=True)
            sys.exit(1)

    # At some point we might expect acceptance of no IDs as valid to be
    # configurable...
    patterns.append("^$")
    logging.warning("NaN values will validate to True")

    na_values = True if "^$" in patterns else False
    combined_compiled = re.compile("|".join(patterns))

    return idSeries.str.match(combined_compiled, na=na_values)


def read_table_files(table):
    """Read table files."""
    logging.info(f"Reading data from {table} table files")
    table_df = pd.DataFrame()

    # First read the master file, if any, then append leaks
    # If no yyyy-mm master file, can still have reports from datetime leaks
    # On reading 'header' read null as NaN so that we can validate null ids as NaN easily
    table_df = read_cdm_tables(params, table)
    try:
        len(table_df)
    except Exception:
        logging.warning(
            "Empty or non-existing master {} table. Attempting \
                        to read datetime leak files".format(
                table
            )
        )
    leak_pattern = FFS.join([table, params.fileID, "????" + FFS + "??.psv"])
    leak_files = glob.glob(os.path.join(params.prev_level_path, leak_pattern))
    leaks_in = 0
    if len(leak_files) > 0:
        for leak_file in leak_files:
            logging.info(f"Reading datetime leak file {leak_file}")
            table_dfi = read_cdm_tables(params, table)
            if len(table_dfi) == 0:
                logging.error(f"Could not read leak file or is empty {leak_file}")
                sys.exit(1)
            leaks_in += len(table_dfi)
            table_df = pd.concat([table_df, table_dfi], axis=0, sort=False)
    if len(table_df) > 0:
        ql_dict[table] = {"leaks_in": leaks_in}
    return table_df


def process_table(table_df, table):
    """Process table."""
    if isinstance(table_df, str):
        # Open table and reindex
        table_df = read_table_files(table)
        if table_df is None or len(table_df) == 0:
            logging.warning(f"Empty or non existing table {table}")
            return
        table_df.set_index((table, "report_id"), inplace=True, drop=False)

    table_df = table_df[table_df.index.isin(mask_df.index)]
    table_mask = mask_df[mask_df.index.isin(table_df.index)]
    if table == "header":
        table_df["history"] = table_df["history"] + f";{history_tstmp}. {history}"
        ql_dict["unique_ids"] = (
            table_df.loc[table_mask["all"], "primary_station_id"]
            .value_counts(dropna=False)
            .to_dict()
        )
    if not table_df[table_mask["all"]].empty:
        write_cdm_tables(params, table_df[table_mask["all"]], tables=table)
    else:
        logging.warning(f"Table {table} is empty. No file will be produced")

    ql_dict[table]["total"] = len(table_df[table_mask["all"]])


# MAIN ------------------------------------------------------------------------

# Process input and set up some things and make sure we can do something-------
logging.basicConfig(
    format="%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s",
    level=logging.INFO,
    datefmt="%Y%m%d %H:%M:%S",
    filename=None,
)

params = script_setup([], sys.argv)

id_validation_path = os.path.join(
    params.data_path, params.release, "NOC_ANC_INFO", "json_files"
)

paths_exist([id_validation_path, params.level_invalid_path])

ql_dict = {table: {} for table in properties.cdm_tables}

# DO THE DATA PROCESSING ------------------------------------------------------

# -----------------------------------------------------------------------------
# Settings in configuration file
validated = ["report_timestamp", "primary_station_id"]
history = "Performed report_timestamp (date_time) and primary_station_id validation"
history_tstmp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

# 1. READ THE DATA-------------------------------------------------------------

# Read the header table file(s) and init the mask to True
# Table files can be multiple for a yyyy-mm if datetime corrections
# in level1b resulted in a change in the month
table = "header"
table_db = read_table_files(table)
columns = table_db.columns
table_db.data = table_db[table]
if table_db.empty:
    logging.error(f"No data could be read for file partition {params.fileID}")
    sys.exit(1)

table_db.set_index("report_id", inplace=True, drop=False)
# Initialize mask
mask_df = pd.DataFrame(index=table_db.index, columns=validated + ["all"])
mask_df[validated] = True

# 2. VALIDATE THE FIELDS-------------------------------------------------------
# 2.1. Validate datetime
field = "report_timestamp"
mask_df[field] = pd.to_datetime(
    table_db[field], format="mixed", errors="coerce"
).notna()

# 2.2. Validate primary_station_id
field = "primary_station_id"
ql_dict["id_validation_rules"] = {}

# First get callsigns:
logging.info("Applying callsign id validation")
p_id_scheme = "primary_station_id_scheme"
pt = "platform_type"
callsigns = table_db[p_id_scheme].isin(["5"]) & table_db[pt].isin(["2", "33"])
nocallsigns = ~callsigns
relist = ["^([0-9]{1}[A-Z]{1}|^[A-Z]{1}[0-9]{1}|^[A-Z]{2})[A-Z0-9]{1,}$", "^[0-9]{5}$"]
callre = re.compile("|".join(relist))
mask_df.loc[callsigns, field] = (
    table_db[field].loc[callsigns].str.match(callre, na=True)
)
# Then the rest according to general validation rules
logging.info("Applying general id validation")
mask_df.loc[nocallsigns, field] = validate_id(table_db[field].loc[callsigns])

# And now set back to True all that the linkage provided
# Instead, read in the header history field and check if it contains
# 'Corrected primary_station_id'
logging.info("Restoring linked IDs")
linked_history = "Corrected primary_station_id"
linked_IDs = (
    table_db["history"].str.contains(linked_history)
    & table_db["history"].str.contains("ID identification").notna()
)

linked_IDs_no = (linked_IDs).sum()

if linked_IDs_no > 0:
    mask_df.loc[linked_IDs, field] = True
    ql_dict["id_validation_rules"]["idcorrected"] = linked_IDs_no

ql_dict["id_validation_rules"]["callsign"] = len(np.where(callsigns)[0])
ql_dict["id_validation_rules"]["noncallsign"] = len(np.where(~callsigns)[0])

# 3. OUTPUT INVALID REPORTS - HEADER ------------------------------------------
for field in validated:
    if False in mask_df[field].value_counts().index:
        ioutname = os.path.join(
            params.level_invalid_path,
            FFS.join(["header", params.fileID, field]) + ".psv",
        )
        write_cdm_tables(
            params, table_db[~mask_df[field]], tables=table, outname=ioutname
        )


# 4. REPORT INVALIDS PER FIELD  -----------------------------------------------
# Now clean, keep only all valid:
mask_df["all"] = mask_df.all(axis=1)
# Report invalids
ql_dict["invalid"] = {}
ql_dict["invalid"]["total"] = len(table_db[~mask_df["all"]])
for field in validated:
    mask_df = mask_df.fillna(False)
    ql_dict["invalid"][field] = len(mask_df[field].loc[~mask_df[field]])

# 5. CLEAN AND OUTPUT TABLES  -------------------------------------------------
# Now process tables and log final numbers and some specifics in header table
# First header table, already open
logging.info("Cleaning table header")
process_table(table_db, table)
obs_tables = [x for x in properties.cdm_tables if x != "header"]
for table in obs_tables:
    table_pattern = FFS.join([table, params.prev_fileID]) + "*.psv"
    table_files = glob.glob(os.path.join(params.prev_level_path, table_pattern))
    if len(table_files) > 0:
        logging.info(f"Cleaning table {table}")
        process_table(table, table)

logging.info("Saving json quicklook")
save_quicklook(params, ql_dict, date_handler)
