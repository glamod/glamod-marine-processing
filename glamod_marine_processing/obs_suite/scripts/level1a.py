"""Created on Mon Jun 17 14:24:10 2019.

Script to generate the C3S CDM Marine level1a data.

    - Reads dataset data (and supp if avail) file with module mdf_reader. This
      includes a data model validation mask.
    - fixes known PT type errors in source dataset with module metmetpy
    - selects data reports according to filtering requests
    - rejects data reports not validiting against its data model
    - maps to the C3S CDM header and observations tables if there is data left
      after cleaning (table[i].psv CDM table-like files)

The processing unit is the source-deck monthly file.
Outputs data to /<data_path>/<release>/<dataset>/level1a/<sid-dck>/table[i]-fileID.psv
Outputs invalid data to /<data_path>/<release>/<dataset>/level1a/invalid/<sid-dck>/fileID-data|mask.psv
Outputs exluded data to /<data_path>/<release>/<dataset>/level1a/excluded/<sid-dck>/fileID-<element>.psv
Outputs quicklook info to:  /<data_path>/<release>/<dataset>/level1a/quicklooks/<sid-dck>/fileID.json
where fileID is year-month-release-update
Before processing starts:

    - checks the existence of all output subdirectories in level1a -> exits if fails
    - checks the existence of the source file to be converted -> exits if fails
    - removes all level1a products on input file resulting from previous runs

On input data:
--------------
Records of input data assumed to be in sid-dck monthly partitions which imply:

    - data for same month-year period
    - data from a unique data model

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
configfile:
----------
To specify processing options that may be shared in different processing
settings:

    - main data model
    - supplemental data model
    - processing options: supplemental replacements,
      record selection/filtering by field (i.e. PT....)

.....

@author: iregon
"""

from __future__ import annotations

import datetime
import logging
import os
import sys
from importlib import reload
from io import StringIO

import numpy as np
import pandas as pd
import simplejson
from _utilities import FFS, date_handler, script_setup
from cdm_reader_mapper import cdm_mapper as cdm
from cdm_reader_mapper import mdf_reader, metmetpy
from cdm_reader_mapper.common import pandas_TextParser_hdlr
from cdm_reader_mapper.operations import inspect, select

reload(logging)  # This is to override potential previous config of logging


# FUNCTIONS -------------------------------------------------------------------
def write_out_junk(dataObj, filename):
    """Write to disk."""
    v = [dataObj] if not read_kwargs.get("chunksize") else dataObj
    c = 0
    for df in v:
        wmode = "a" if c > 0 else "w"
        header = False if c > 0 else True
        df.to_csv(filename, sep="|", mode=wmode, header=header)
        c += 1


# MAIN ------------------------------------------------------------------------

# PROCESS INPUT AND MAKE SOME CHECKS ------------------------------------------
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

process_options = [
    "data_model",
    "read_sections",
    "filter_reports_by",
    "cdm_map",
]
params = script_setup(process_options, args, "level1a", "level0")

if not params.flag:
    logging.error("Error parsing initial configuration")
    sys.exit(1)

correction_path = os.path.join(params.data_path, params.release, params.corrections)

L0_filename = os.path.join(params.prev_level_path, params.filename)
if not os.path.isfile(L0_filename):
    logging.error(f"Could not find data input file: {L0_filename}")
    sys.exit(1)

# DO THE DATA PROCESSING ------------------------------------------------------
data_model = params.data_model
dataset = params.dataset
io_dict = {}

# 1. Read input file to dataframe
logging.info("Reading dataset data")

read_kwargs = {
    "data_model": params.data_model,
    "sections": params.read_sections,
    "chunksize": 200000,
}
data_in = mdf_reader.read(L0_filename, **read_kwargs)
logging.info(data_in.data)
io_dict["read"] = {"total": inspect.get_length(data_in.data)}

# 2. PT fixing, filtering and invalid rejectionselect_true
# 2.1. Fix platform type

# dataset = ICOADS_R3.0.0T is not "registered" in metmetpy, but icoads_r3000
# Modify metmetpy so that it maps ICOADS_R3.0.0T to its own alliaeses
# we now do the dirty trick here: dataset_metmetpy = icoads_r3000

logging.info("Applying platform type fixtures")
dataset_metmetpy = "icoads_r3000_NRT"
data_model_metmetpy = "imma1"
data_in.data = metmetpy.correct_pt.correct(
    data_in.data, dataset_metmetpy, data_model_metmetpy, params.dck
)

# 2.2. Apply record selection (filter by) criteria: PT types.....
if hasattr(params, "filter_reports_by"):
    logging.info("Applying selection filters")
    io_dict["not_selected"] = {}
    data_excluded = {}
    data_excluded["attrs"] = data_in.attrs.copy()
    data_excluded["data"] = {}
    # 3.1. Select by report_filters options
    for k, v in params.filter_reports_by.items():
        io_dict["not_selected"][k] = {}
        logging.info("Selecting {} values: {}".format(k, ",".join(v)))
        filter_location = tuple(k.split("."))
        col = filter_location[0] if len(filter_location) == 1 else filter_location
        values = v
        selection = {col: values}
        data_in.data, data_excluded["data"][k], index = select.select_from_list(
            data_in.data, selection, out_rejected=True, in_index=True
        )
        data_in.mask = select.select_from_index(data_in.mask, index)
        io_dict["not_selected"][k]["total"] = inspect.get_length(
            data_excluded["data"][k]
        )
        if io_dict["not_selected"][k]["total"] > 0:
            if data_in.attrs[col]["column_type"] in ["str", "object", "key"]:
                io_dict["not_selected"][k].update(
                    inspect.count_by_cat(data_excluded["data"][k], col)
                )
    io_dict["not_selected"]["total"] = sum(
        [v.get("total") for k, v in io_dict["not_selected"].items()]
    )

io_dict["pre_selected"] = {"total": inspect.get_length(data_in.data)}

# 2.3. Keep track of invalid data
# First create a global mask and count failure occurrences
newmask_buffer = StringIO()
logging.info("Removing invalid data")
for data, mask in zip(data_in.data, data_in.mask):
    mask["global_mask"] = mask.all(axis=1)
    mask.to_csv(newmask_buffer, header=False, mode="a", encoding="utf-8", index=False)

    # 2.3.2. Invalid reports counts and values
    # Initialize counters if first chunk
    masked_columns = [
        x for x in mask if not all(mask[x].isna()) and x != ("global_mask", "")
    ]
    if not io_dict.get("invalid"):
        io_dict["invalid"] = {
            ".".join(k): {"total": 0, "values": []} for k in masked_columns
        }
    for col in masked_columns:
        k = ".".join(col)
        io_dict["invalid"][k]["total"] += len(mask[col].loc[~mask[col]])
        if col in data:  # cause some masks are not in data (datetime....)
            io_dict["invalid"][k]["values"].extend(data[col].loc[~mask[col]].values)

newmask_buffer.seek(0)
chunksize = (
    None
    if isinstance(data_in.mask, pd.DataFrame)
    else data_in.mask.orig_options["chunksize"]
)
data_in.mask = pd.read_csv(newmask_buffer, names=[x for x in mask], chunksize=chunksize)
data_in.data = pandas_TextParser_hdlr.restore(data_in.data)
# Now see what fails
for col in masked_columns:
    k = ".".join(col)
    if io_dict["invalid"][k]["total"] > 0:
        if data_in.attrs.get(col, {}).get("column_type") in cdm.properties.object_types:
            ivalues = list(set(io_dict["invalid"][k]["values"]))
            # This is because sorting fails on strings if nan
            if np.nan in ivalues:
                ivalues.remove(np.nan)
                ivalues.sort()
                ivalues.append(np.nan)
            else:
                ivalues.sort()
            io_dict["invalid"][k].update(
                {i: io_dict["invalid"][k]["values"].count(i) for i in ivalues}
            )
            sush = io_dict["invalid"][k].pop("values", None)
        elif (
            data_in.attrs.get(col, {}).get("column_type")
            in cdm.properties.numeric_types
        ):
            values = io_dict["invalid"][k]["values"]
            values = np.array(values)[~pd.isnull(values)]
            if len(values > 0):
                [counts, edges] = np.histogram(values)
                # Following binning approach only if at most 1 sign digit!
                bins = [
                    "-".join([f"{edges[i]:.1f}", f"{edges[i+1]:.1f}"])
                    for i in range(0, len(edges) - 1)
                ]
                io_dict["invalid"][k].update(
                    {b: counts for b, counts in zip(bins, counts)}
                )
            else:
                io_dict["invalid"][k].update(
                    {"nan?": len(io_dict["invalid"][k]["values"])}
                )
            sush = io_dict["invalid"][k].pop("values", None)
    else:
        sush = io_dict["invalid"].pop(k, None)

# 2.4. Discard invalid data.
data_invalid = {}
data_invalid["attrs"] = data_in.attrs.copy()
data_in.data, data_invalid["data"] = select.select_true(
    data_in.data, data_in.mask, out_rejected=True
)
data_in.mask, data_invalid["valid_mask"] = select.select_true(
    data_in.mask, data_in.mask, out_rejected=True
)
io_dict["invalid"]["total"] = inspect.get_length(data_invalid["data"])
io_dict["processed"] = {"total": inspect.get_length(data_in.data)}

process = True
if io_dict["processed"]["total"] == 0:
    process = False
    logging.warning("No data to map to CDM after selection and cleaning")


# 3. Map to common data model and output files
if process:
    logging.info("Mapping to CDM")
    tables = [
        "header",
        "observations-at",
        "observations-sst",
        "observations-dpt",
        "observations-wbt",
        "observations-wd",
        "observations-ws",
        "observations-slp",
    ]
    obs_tables = tables[1:]
    io_dict.update({table: {} for table in tables})
    mapping = params.cdm_map
    logging.debug(f"Mapping attributes: {data_in.attrs}")
    cdm_tables = cdm.map_model(mapping, data_in.data, data_in.attrs, log_level="INFO")

    logging.info("Printing tables to psv files")
    cdm.cdm_to_ascii(
        cdm_tables,
        log_level="DEBUG",
        out_dir=params.level_path,
        suffix=params.fileID,
        prefix=None,
    )

    for table in tables:
        io_dict[table]["total"] = inspect.get_length(cdm_tables[table]["data"])

io_dict["date processed"] = datetime.datetime.now()
logging.info("Saving json quicklook")
L1a_io_filename = os.path.join(params.level_ql_path, params.fileID + ".json")
with open(L1a_io_filename, "w") as fileObj:
    simplejson.dump(
        {"-".join([params.year, params.month]): io_dict},
        fileObj,
        default=date_handler,
        indent=4,
        ignore_nan=True,
    )

# Output exluded and invalid ---------------------------------------------
if hasattr(params, "filter_reports_by"):
    for k, v in data_excluded["data"].items():
        if inspect.get_length(data_excluded["data"][k]) > 0:
            excluded_filename = os.path.join(
                params.level_excluded_path,
                params.fileID + FFS + "_".join(k.split(".")) + ".psv",
            )
            logging.info(f"Writing {k} excluded data to file {excluded_filename}")
            write_out_junk(v, excluded_filename)

if inspect.get_length(data_invalid["data"]) > 0:
    invalid_data_filename = os.path.join(
        params.level_invalid_path, params.fileID + FFS + "data.psv"
    )
    invalid_mask_filename = os.path.join(
        params.level_invalid_path, params.fileID + FFS + "mask.psv"
    )
    logging.info(f"Writing invalid data to file {invalid_data_filename}")
    write_out_junk(data_invalid["data"], invalid_data_filename)
    logging.info(f"Writing invalid data mask to file {invalid_mask_filename}")
    write_out_junk(data_invalid["valid_mask"], invalid_mask_filename)

logging.info("End")
