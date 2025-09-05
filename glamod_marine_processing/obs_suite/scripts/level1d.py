"""
Created on Mon Jun 17 14:24:10 2019

Script to generate the C3S CDM Marine level1d data: add external MD (pub47...):

    - Read header table and MD and see if there is anything to merge

    - Map MD to CDM with module cdm

    - Merge mapped MD with CDM tables by primary_station_id and
      save to file with function process_table()
      (if nothing to merge, just save the file to level1d...)

    - log, per table, total number of records and those with MD added/updated

The processing unit is the source-deck monthly set of CDM tables.

Outputs data to /<data_path>/<release>/<dataset>/level1d/<sid-dck>/table[i]-fileID.psv
Outputs quicklook info to:  /<data_path>/<release>/<dataset>/level1d/quicklooks/<sid-dck>/fileID.json
where fileID is yyyy-mm-release_tag-update_tag

Before processing starts:
    - checks the existence of all io subdirectories in level1c|d -> exits if fails
    - checks the existence of the source table to be converted (header only) -> exits if fails
    - checks the existence of the monthly MD file -> exits if fails
    - removes all level1d products on input file resulting from previous runs


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

On input data:
--------------
If the pre-processing of the MD changes, then how we map the MD in map_to_cdm()
 changes also. The mappings there as for MD pre-processing in Autumn2019

pub47 monthly files assumed to have 1 hdr line (first) with column names
pub47 monthly files with FS=';'
pub47 field names assumed: call;record;name;freq;vsslM;vssl;automation;rcnty;
valid_from;valid_to;uid;thmH1;platH;brmH1;anmH;anHL1;wwH;sstD1;th1;hy1;st1;bm1;an1

.....

@author: iregon
"""

from __future__ import annotations

import datetime
import logging
import os
import sys
from collections import Counter
from importlib import reload

import numpy as np
import pandas as pd
from _utilities import (
    date_handler,
    delimiter,
    paths_exist,
    read_cdm_tables,
    save_quicklook,
    script_setup,
    write_cdm_tables,
)
from cdm_reader_mapper import map_model
from cdm_reader_mapper.cdm_mapper import properties
from cdm_reader_mapper.cdm_mapper.tables.tables import get_cdm_atts

reload(logging)  # This is to override potential previous config of logging


def map_to_cdm(md_model, meta_df, log_level="INFO"):
    """Map to CDM."""
    # Atts is a minimum info on vars the cdm module requires
    meta_db = map_model(meta_df, imodel=md_model, log_level=log_level)
    for table in properties.cdm_tables:
        meta_db[table] = meta_db[table].astype(
            "object"
        )  # meta_cdm[meta_cdm_columns] = meta_cdm_dict[table]["data"].astype("object")
    return meta_db


def process_table(table_db, table):
    """Process table."""
    logging.info(f"Processing table {table}")
    if isinstance(table_db, str):
        # Assume 'header' and in a DF in table_df otherwise
        # Open table and reindex
        table_db = read_cdm_tables(params, table)
        if table_db is None or table_db.empty:
            logging.warning(f"Empty or non existing table {table}")
            return
        table_db.data = table_db[table]
        table_db.set_index("report_id", inplace=True, drop=False)
        header_ = header_db.copy()
        # by this point, header_df has its index set to report_id, hopefully ;)
        table_db.data = table_db[table_db.index.isin(header_.index)]
        table_db.data["primary_station_id"] = header_["primary_station_id"].loc[
            table_db.index
        ]

    ql_dict[table] = {"total": len(table_db), "updated": 0}
    if merge:
        ql_dict[table] = {"total": len(table_db), "updated": 0}
        table_db.set_index("primary_station_id", drop=False, inplace=True)

        if table == "header":
            meta_table = meta_cdm[[x for x in meta_cdm if x[0] == table]]
            meta_table.columns = [x[1] for x in meta_table]
            # which should be equivalent to: (but more felxible if table !=header)
            # meta_table = meta_cdm.loc[:, table]
        else:
            meta_table = meta_cdm[
                [
                    x
                    for x in meta_cdm
                    if x[0] == table
                    or (x[0] == "header" and x[1] == "primary_station_id")
                ]
            ]
            meta_table.columns = [x[1] for x in meta_table]

        meta_table.set_index("primary_station_id", drop=False, inplace=True)
        meta_table = meta_table.replace("null", np.nan)
        table_db.data.update(meta_table[~meta_table.index.duplicated()])

        updated_locs = [x for x in table_db.index if x in meta_table.index]
        ql_dict[table]["updated"] = len(updated_locs)

        if table == "header":
            missing_ids = [x for x in table_db.index if x not in meta_table.index]
            if len(missing_ids) > 0:
                ql_dict["non " + params.md_model + " ids"] = {
                    k: v for k, v in Counter(missing_ids).items()
                }
            history_add = ";{}. {}".format(history_tstmp, "metadata fix")
            locs = table_db.data["primary_station_id"].isin(updated_locs)
            table_db.data["history"].loc[locs] = (
                table_db.data["history"].loc[locs] + history_add
            )

    write_cdm_tables(params, table_db, tables=table, columns=cdm_atts.get(table).keys())


# END FUNCTIONS ---------------------------------------------------------------


# %% MAIN ------------------------------------------------------------------------

# Process input and set up some things and make sure we can do something-------
logging.basicConfig(
    format="%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s",
    level=logging.DEBUG,
    datefmt="%Y%m%d %H:%M:%S",
    filename=None,
)

process_options = [
    "md_model",
    "md_subdir",
    "md_version",
    "history_explain",
    "md_first_yr_avail",
    "md_last_yr_avail",
    "md_not_avail",
]
params = script_setup(process_options, sys.argv)

paths_exist(params.level_log_path)

md_avail = True if not params.md_not_avail else False

if md_avail:
    if params.corrections_mod.get("pub47_path"):
        md_path = params.corrections_mod.get("pub47_path")
    else:
        md_path = os.path.join(
            params.data_path, "datasets", params.md_subdir, params.md_version
        )
    logging.info(f"Setting MD path to {md_path}")
    metadata_filename = os.path.join(md_path, f"pub47_{params.year}_{params.month}.csv")

    if not os.path.isfile(metadata_filename):
        if int(params.year) > int(params.md_last_yr_avail) or int(params.year) < int(
            params.md_first_yr_avail
        ):
            md_avail = False
            logging.warning(
                f"Metadata source available only in period {str(params.md_first_yr_avail)}-{str(params.md_last_yr_avail)}"
            )
            logging.warning("level1d data will be created with no merging")
        else:
            logging.error(f"Metadata file not found: {metadata_filename}")
            sys.exit(1)
else:
    logging.info(f"Metadata not available for data source-deck {params.sid_dck}")
    logging.info("level1d data will be created with no merging")

ql_dict = {}

# DO THE DATA PROCESSING ------------------------------------------------------
# -----------------------------------------------------------------------------
try:
    history_tstmp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
except AttributeError:  # for python < 3.11
    history_tstmp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

cdm_atts = get_cdm_atts()
obs_tables = [x for x in cdm_atts.keys() if x != "header"]

# 1. SEE STATION ID's FROM BOTH DATA STREAMS AND SEE IF THERE'S ANYTHING TO
# MERGE AT ALL
# Read the header table
header_db = read_cdm_tables(params, "header")
header_db.data = header_db["header"]

if header_db.empty:
    logging.error("Empty or non-existing header table")
    sys.exit(1)

# Read the metadata
if md_avail:
    meta_df = pd.read_csv(
        metadata_filename,
        delimiter=delimiter,
        dtype="object",
        header=0,
        na_values="MSNG",
    )

    if len(meta_df) == 0:
        logging.error("Empty or non-existing metadata file")
        sys.exit(1)

# See if there's anything to do
header_db.set_index("primary_station_id", drop=False, inplace=True)
merge = True if md_avail else False
if md_avail:
    meta_df = meta_df.loc[
        meta_df["ship_callsign"].isin(header_db["primary_station_id"])
    ]
    if len(meta_df) == 0:
        logging.warning("No metadata to merge in file")
        merge = False

# 2. MAP PUB47 MD TO CDM FIELDS -----------------------------------------------
if merge:
    logging.info("Mapping metadata to CDM")
    meta_cdm = map_to_cdm(params.md_model, meta_df, log_level="DEBUG")

# 3. UPDATE CDM WITH PUB47 OR JUST COPY PREV LEVEL TO CURRENT -----------------
# This is only valid for the header
process_table(header_db, "header")

header_db.set_index("report_id", inplace=True, drop=False)

for table in obs_tables:
    process_table(table, table)

# 4. SAVE QUICKLOOK -----------------------------------------------------------
logging.info("Saving json quicklook")
save_quicklook(params, ql_dict, date_handler)
