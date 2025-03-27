"""
Script to convert C3S CDM Marine level2 data into CDM OBS CORE pressure only data.

The processing unit is the source-deck.

Outputs included data to /<data_path>/<release>/<source>/level3/<sid-dck>/table[i]-fileID.psv

where fileID is yyyy-mm-release_tag-update_tag

Before processing starts:
    - checks the existence of input data subdirectory in level2 -> exits if fails
    - checks the existence of the level3 selection file (level3_list) and that
      sid-dck is registered in it -> exits if fails
    - checks that a sid-dck to be included has at least an observation table
      registered to be included  -> exits if fails

If at any point during copying an exception is raised, cleans sid-dck level3
before exiting.

Inargs:
-------
data_path: data release parent path (i.e./gws/nopw/c3s311_lot2/data/marine)
sid_dck: source-deck partition (sss-ddd)
release: release identifier
update: release update identifier
source: source dataset identifier
"""

from __future__ import annotations

import datetime
import logging
import sys
from importlib import reload

from _utilities import level3_columns, read_cdm_tables, script_setup, write_cdm_tables

reload(logging)  # This is to override potential previous config of logging


# FUNCTIONS -------------------------------------------------------------------
def process_table(table_df):
    """Process table."""
    cdm_obs_core_df = table_df[level3_columns]
    new_cols = [col[1] for col in cdm_obs_core_df.columns]
    cdm_obs_core_df.columns = new_cols

    cdm_obs_core_df = cdm_obs_core_df[cdm_obs_core_df["observation_value"].notnull()]

    write_cdm_tables(params, cdm_obs_core_df, tables="pressure-data")


# MAIN ------------------------------------------------------------------------

# Process input and set up some things and make sure we can do something-------
logging.basicConfig(
    format="%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s",
    level=logging.INFO,
    datefmt="%Y%m%d %H:%M:%S",
    filename=None,
)

params = script_setup([], sys.argv)

# DO THE DATA SELECTION -------------------------------------------------------
# -----------------------------------------------------------------------------
obs_table = "observations-slp"
header_table = "header"
cdm_tables = [header_table, obs_table]

history_tstmp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

table_df = read_cdm_tables(params, cdm_tables)

if not table_df.empty:
    process_table(table_df)
else:
    logging.warning(f"No CDM tables available for: {params.prev_fileID}.")
