"""
Created on Mon Jun 17 14:24:10 2019

Script to generate the C3S CDM Marine level2 data: final release data after visual
inspection of data.

The processing unit is the source-deck.

Outputs included data to /<data_path>/<release>/<source>/level2/<sid-dck>/table[i]-fileID.psv
Outputs exluded data to /<data_path>/<release>/<source>/level2/excluded/<sid-dck>/table[i]-fileID.psv

where fileID is yyyy-mm-release_tag-update_tag

Before processing starts:
    - checks the existence of input data subdirectory in level1e -> exits if fails
    - checks the existence of the level2 selection file (level2_list) and that
      sid-dck is registered in it -> exits if fails
    - checks that a sid-dck to be included has at least an observation table
      registered to be included  -> exits if fails
    - removes level2 sid-dck subdirs (except log/sid-dck)

If at any point during copying an exception is raised, cleans sid-dck level2
before exiting.

Inargs:
-------
data_path: data release parent path (i.e./gws/nopw/c3s311_lot2/data/marine)
sid_dck: source-deck partition (sss-ddd)
release: release identifier
update: release update identifier
source: source dataset identifier
level2_list: path to file with level2 configuration

Uses level2_list:
-----------------
json file as created by L2_list_create.py.

.....

@author: iregon
"""

from __future__ import annotations

import glob
import json
import logging
import os
import shutil
import sys
from importlib import reload
from pathlib import Path

from _utilities import script_setup
from cdm_reader_mapper import cdm_mapper as cdm

reload(logging)  # This is to override potential previous config of logging


# FUNCTIONS -------------------------------------------------------------------
def clean_level():
    """Clean level."""
    for dirname in [L2_path, L2_reports_path, L2_excluded_path]:
        try:
            if os.path.isdir(dirname):
                logging.info(f"Removing directory {dirname}")
                os.remove(os.path.join(dirname, "*.psv"))
        except Exception:
            pass


def copyfiles(pattern, dest, mode="excluded"):
    """Copy file pattern to dest."""
    file_list = glob.glob(pattern)
    for file_ in file_list:
        file_name = Path(file_).name
        shutil.copyfile(file_, os.path.join(dest, file_name))
        logging.info(f"{file_name} {mode} from level2 in {dest}")


# MAIN ------------------------------------------------------------------------

# Process input and set up some things and make sure we can do something-------
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

params = script_setup([], args)

level = "level2"

# These to build the brace expansions for the out of release periods
left_min_period = 1600
right_max_period = 2100

release_path = os.path.join(params.data_path, params.release, params.dataset)
release_id = "-".join([params.release, params.update])
L1e_path = os.path.join(release_path, "level1e", params.sid_dck)
L2_path = os.path.join(release_path, level, params.sid_dck)
L2_excluded_path = os.path.join(release_path, level, "excluded", params.sid_dck)
L2_reports_path = os.path.join(release_path, level, "reports", params.sid_dck)

data_paths = [L1e_path]
if any([not os.path.isdir(x) for x in data_paths]):
    logging.error(
        "Could not find data paths: {}".format(
            ",".join([x for x in data_paths if not os.path.isdir(x)])
        )
    )
    sys.exit(1)

if not os.path.isfile(params.level2_list):
    logging.error(f"Level2 selection file {params.level2_list} not found")
    sys.exit(1)


# Clean previous L2 data and report subdirs -----------------------------------
clean_level()

# DO THE DATA SELECTION -------------------------------------------------------
# -----------------------------------------------------------------------------
cdm_tables = cdm.load_tables()
obs_tables = [x for x in cdm_tables if x != "header"]
with open(params.level2_list) as fileObj:
    include_list = json.load(fileObj)

if not include_list.get(params.sid_dck):
    logging.error(
        f"sid-dck {params.sid_dck} not registered in level2 list {params.level2_list}"
    )
    sys.exit(1)


# See if global release period has been changed for level 2 and apply to sid-dck
# For some strange reason the years are strings in the periods files...
year_init = int(include_list.get(params.sid_dck, {}).get("year_init"))
year_end = int(include_list.get(params.sid_dck, {}).get("year_end"))

init_global = include_list.get("year_init")
end_global = include_list.get("year_end")

if init_global:
    year_init = year_init if year_init >= int(init_global) else int(init_global)
if end_global:
    year_end = year_end if year_end <= int(end_global) else int(end_global)

exclude_sid_dck = include_list.get(params.sid_dck, {}).get("exclude")

exclude_param_global_list = include_list.get("params_exclude")
exclude_param_sid_dck_list = include_list.get(params.sid_dck, {}).get("params_exclude")

exclude_param_list = list(set(exclude_param_global_list + exclude_param_sid_dck_list))
include_param_list = [x for x in obs_tables if x not in exclude_param_list]

# Check that inclusion list makes sense
if not exclude_sid_dck and len(include_param_list) == 0:
    logging.error(
        f"sid-dck {params.sid_dck} is to be included, but include parameter list is empty"
    )
    sys.exit(1)

try:
    include_param_list.append("header")
    if exclude_sid_dck:
        for table in cdm_tables:
            pattern = os.path.join(L1e_path, table + "*.psv")
            copyfiles(pattern, L2_excluded_path)
    else:
        for table in exclude_param_list:
            pattern = os.path.join(L1e_path, table + "*.psv")
            copyfiles(pattern, L2_excluded_path)
        for table in include_param_list:
            for year in range(year_init, year_end + 1):
                pattern = os.path.join(L1e_path, f"{table}-*{str(year)}-??-*.psv")
                logging.warning(pattern)
                copyfiles(pattern, L2_path, mode="included")

        # Send out of release period to excluded
        for year in range(left_min_period, year_init):
            pattern = os.path.join(L1e_path, f"*{str(year)}-??-*.psv")
            copyfiles(pattern, L2_excluded_path)
        for year in range(year_end + 1, right_max_period + 1):
            pattern = os.path.join(L1e_path, f"*{str(year)}-??-*.psv")
            copyfiles(pattern, L2_excluded_path)

    logging.info("Level2 data succesfully created")
except Exception:
    logging.error("Error creating level2 data", exc_info=True)
    logging.info(f"Level2 data {params.sid_dck} removed")
    clean_level()
