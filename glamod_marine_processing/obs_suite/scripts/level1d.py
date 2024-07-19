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
update: udpate tag
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
import subprocess
import sys
from collections import Counter
from importlib import reload

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

reload(logging)  # This is to override potential previous config of logging


def map_to_cdm(md_model, meta_df, log_level="INFO"):
    """Map to CDM."""
    # Atts is a minimum info on vars the cdm mocule requires
    meta_cdm_dict = cdm.map_model(md_model, meta_df, {}, log_level=log_level)
    meta_cdm = pd.DataFrame()
    for table in cdm_tables:
        meta_cdm_columns = [(table, x) for x in meta_cdm_dict[table]["data"].columns]
        meta_cdm[meta_cdm_columns] = meta_cdm_dict[table]["data"].astype("object")
    return meta_cdm


def process_table(table_df, table_name):
    """Process table."""
    logging.info(f"Processing table {table_name}")
    if isinstance(table_df, str):
        # Assume 'header' and in a DF in table_df otherwise
        # Open table and reindex
        table_df = pd.DataFrame()
        if local:
            table_df = cdm.read_tables(
                scratch_path, params.prev_fileID, cdm_subset=[table_name]
            )
        else:
            table_df = cdm.read_tables(
                params.prev_level_path, params.prev_fileID, cdm_subset=[table_name]
            )
        if table_df is None or len(table_df) == 0:
            logging.warning(f"Empty or non existing table {table_name}")
            return
        table_df.set_index("report_id", inplace=True, drop=False)
        # by this point, header_df has its index set to report_id, hopefully ;)
        table_df["primary_station_id"] = header_df["primary_station_id"].loc[
            table_df.index
        ]

    meta_dict[table_name] = {"total": len(table_df), "updated": 0}
    if merge:
        meta_dict[table_name] = {"total": len(table_df), "updated": 0}
        table_df.set_index("primary_station_id", drop=False, inplace=True)

        if table_name == "header":
            meta_table = meta_cdm[[x for x in meta_cdm if x[0] == table_name]]
            meta_table.columns = [x[1] for x in meta_table]
            # which should be equivalent to: (but more felxible if table_name !=header)
            # meta_table = meta_cdm.loc[:, table_name]
        else:
            meta_table = meta_cdm[
                [
                    x
                    for x in meta_cdm
                    if x[0] == table_name
                    or (x[0] == "header" and x[1] == "primary_station_id")
                ]
            ]
            meta_table.columns = [x[1] for x in meta_table]

        meta_table.set_index("primary_station_id", drop=False, inplace=True)
        table_df.update(meta_table[~meta_table.index.duplicated()])

        updated_locs = [x for x in table_df.index if x in meta_table.index]
        meta_dict[table_name]["updated"] = len(updated_locs)

        if table_name == "header":
            missing_ids = [x for x in table_df.index if x not in meta_table.index]
            if len(missing_ids) > 0:
                meta_dict["non " + params.md_model + " ids"] = {
                    k: v for k, v in Counter(missing_ids).items()
                }
            history_add = ";{}. {}".format(history_tstmp, "metadata fix")
            locs = table_df["primary_station_id"].isin(updated_locs)
            table_df["history"].loc[locs] = table_df["history"].loc[locs] + history_add

    cdm_columns = cdm_tables.get(table_name).keys()
    odata_filename = os.path.join(
        params.level_path, FFS.join([table_name, params.fileID]) + ".psv"
    )
    table_to_csv(table_df, odata_filename, columns=cdm_columns)


# END FUNCTIONS ---------------------------------------------------------------


# %% MAIN ------------------------------------------------------------------------

# Process input and set up some things and make sure we can do something-------
logging.basicConfig(
    format="%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s",
    level=logging.DEBUG,
    datefmt="%Y%m%d %H:%M:%S",
    filename=None,
)
if len(sys.argv) > 1:
    logging.info("Reading command line arguments")
    args = sys.argv
else:
    logging.error("Need arguments to run!")
    sys.exit(1)

process_options = [
    "md_model",
    "md_subdir",
    "history_explain",
    "md_first_yr_avail",
    "md_last_yr_avail",
    "md_not_avail",
]
level = "level1d"
params = script_setup(process_options, args, level, "level1c")

local = True

scratch_ = os.path.join(params.release_path, level, "scratch")
scratch_path = os.path.join(scratch_, params.sid_dck)
os.makedirs(scratch_path, exist_ok=True)
paths_exist(params.level_log_path)

md_avail = True if not params.md_not_avail else False

if md_avail:
    md_path = os.path.join(
        params.data_path, params.release, params.md_subdir, "monthly"
    )
    logging.info(f"Setting MD path to {md_path}")
    metadata_filename = os.path.join(
        md_path, FFS.join([params.year, params.month, "01.csv"])
    )
    # removed .gz to make sure unzipping is not causing high I/O (just a guess)
    metadata_fn_scratch = os.path.join(
        scratch_path, FFS.join([params.year, params.month, "01.csv"])
    )

    if not os.path.isfile(metadata_filename):
        if (
            int(params.year) > params.md_last_yr_avail
            or int(params.year) < params.md_first_yr_avail
        ):
            md_avail = False
            logging.warning(
                "Metadata source available only in period {}-{}".format(
                    str(params.md_first_yr_avail), str(params.md_last_yr_avail)
                )
            )
            logging.warning("level1d data will be created with no merging")
        else:
            logging.error(f"Metadata file not found: {metadata_filename}")
            sys.exit(1)
else:
    logging.info(f"Metadata not available for data source-deck {params.sid_dck}")
    logging.info("level1d data will be created with no merging")

meta_dict = {}

# DO THE DATA PROCESSING ------------------------------------------------------
# -----------------------------------------------------------------------------
history_tstmp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
cdm_tables = cdm.load_tables()
obs_tables = [x for x in cdm_tables.keys() if x != "header"]

# 1. SEE STATION ID's FROM BOTH DATA STREAMS AND SEE IF THERE'S ANYTHING TO
# MERGE AT ALL
# Read the header table
table = "header"
if local:
    logging.info(f"cp -L {params.prev_level_path}/*.psv {scratch_path}")
    subprocess.call(f"cp -L {params.prev_level_path}/*.psv {scratch_path}", shell=True)
header_df = pd.DataFrame()
if local:
    header_df = cdm.read_tables(scratch_path, cdm_subset=[table], na_values="null")
else:
    header_df = cdm.read_tables(
        params.prev_level_path, cdm_subset=[table], na_values="null"
    )

if len(header_df) == 0:
    logging.error("Empty or non-existing header table")
    sys.exit(1)

# Read the metadona
if md_avail:
    if local:
        subprocess.call(f"cp -L {metadata_filename} {metadata_fn_scratch}", shell=True)
    meta_df = pd.DataFrame()
    if local:
        meta_df = pd.read_csv(
            metadata_fn_scratch,
            delimiter=delimiter,
            dtype="object",
            header=0,
            na_values="MSNG",
        )
    else:
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
header_df.set_index("primary_station_id", drop=False, inplace=True)
merge = True if md_avail else False
if md_avail:
    meta_df = meta_df.loc[
        meta_df["ship_callsign"].isin(header_df["primary_station_id"])
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
table = "header"
process_table(header_df, table)

header_df.set_index("report_id", inplace=True, drop=False)
# for obs
for table in obs_tables:
    process_table(table, table)

# 4. SAVE QUICKLOOK -----------------------------------------------------------
logging.info("Saving json quicklook")
level_io_filename = os.path.join(params.level_ql_path, params.fileID + ".json")
with open(level_io_filename, "w") as fileObj:
    simplejson.dump(
        {"-".join([params.year, params.month]): meta_dict},
        fileObj,
        default=date_handler,
        indent=4,
        ignore_nan=True,
    )

logging.info("End")
