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
import os
import sys
from importlib import reload

import pandas as pd
from _utilities import (
    level3_columns,
    level3_conversions,
    level3_dtypes,
    level3_mappings,
    read_cdm_tables,
    script_setup,
    write_cdm_tables,
)
from cdm_reader_mapper.cdm_mapper import properties

reload(logging)  # This is to override potential previous config of logging


# FUNCTIONS -------------------------------------------------------------------
def process_table(table_df):
    """Process table."""
    tables = table_df.columns.get_level_values(0).unique().tolist()
    header_mappings = level3_mappings["header"]
    observations_mappings = level3_mappings["observations"]

    header_df = table_df["header"][list(header_mappings.values())].copy()
    header_df.columns = [c for c in header_mappings.keys()]

    for table in tables:
        if table == "header":
            continue
        obs_df = table_df[table][list(observations_mappings.values())].copy()
        obs_df.columns = [c for c in observations_mappings.keys()]
        obs_df = pd.concat([header_df, obs_df], axis=1)
        obs_df = obs_df[level3_columns]
        obs_df = obs_df.dropna(subset=["observation_value"], ignore_index=True)

        for column, func in level3_conversions.items():
            obs_df[column] = func(obs_df[column])

        params.fileID = (
            f"insitu-observations-surface-marine_{params.year}-{params.month}"
        )
        outname = os.path.join(
            params.level_path,
            f"insitu-{table}-surface-marine_{params.year}-{params.month}",
        )
        write_cdm_tables(
            params,
            obs_df,
            tables=table,
            outname=outname,
            dtypes=level3_dtypes,
            mode="parquet",
        )


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
try:
    history_tstmp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
except AttributeError:  # for python < 3.11
    history_tstmp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

table_df = read_cdm_tables(params, properties.cdm_tables)

if not table_df.empty:
    process_table(table_df)
else:
    logging.warning(f"No CDM tables available for: {params.prev_fileID}.")
