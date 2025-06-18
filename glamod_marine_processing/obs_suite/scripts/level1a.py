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
Outputs excluded data to /<data_path>/<release>/<dataset>/level1a/excluded/<sid-dck>/fileID-<element>.psv
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
update: update tag
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

import logging
import os
import sys
from importlib import reload
from io import StringIO

import numpy as np
import pandas as pd
from _utilities import FFS, chunksizes, date_handler, save_quicklook, script_setup
from cdm_reader_mapper import read_mdf
from cdm_reader_mapper.cdm_mapper import properties
from cdm_reader_mapper.common import inspect, pandas_TextParser_hdlr

import glamod_marine_processing.obs_suite.modules.blacklisting as blacklist_funcs

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

process_options = [
    "data_model",
    "read_sections",
    "filter_reports_by",
    "blacklisting",
]
params = script_setup(process_options, sys.argv)

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
chunksize = chunksizes[params.dataset]
read_kwargs = {
    "imodel": data_model,
    "sections": params.read_sections,
    "chunksize": chunksize,
}

data_in = read_mdf(L0_filename, **read_kwargs)

io_dict["read"] = {"total": len(data_in)}

# 2. PT fixing, filtering and invalid rejectionselect_true
# 2.1. Fix platform type

# dataset = ICOADS_R3.0.0T is not "registered" in metmetpy, but icoads_r3000
# Modify metmetpy so that it maps ICOADS_R3.0.0T to its own alliaeses
# we now do the dirty trick here: dataset_metmetpy = icoads_r3000
logging.info("Applying platform type fixtures")
data_in.correct_pt(inplace=True)

# 2.2. Apply record selection (filter by) criteria: PT types.....
if params.filter_reports_by:
    logging.info("Applying selection filters")
    io_dict["not_selected"] = {}
    data_excluded = {}
    data_excluded["data"] = {}
    # 3.1. Select by report_filters options
    for k, v in params.filter_reports_by.items():
        io_dict["not_selected"][k] = {}
        logging.info("Selecting {} values: {}".format(k, ",".join(v)))
        filter_location = tuple(k.split("."))
        col = filter_location[0] if len(filter_location) == 1 else filter_location
        values = v
        selection = {col: values}
        data_in, data_excl = data_in.split_by_column_entries(selection)
        data_excluded["data"][k] = data_excl.data
        io_dict["not_selected"][k]["total"] = len(data_excl)
        if io_dict["not_selected"][k]["total"] > 0:
            if data_in.dtype.get(col, {}) in ["str", "object", "key"]:
                io_dict["not_selected"][k].update(data_excl.unique(columns=col))
    io_dict["not_selected"]["total"] = sum(
        [v.get("total") for k, v in io_dict["not_selected"].items()]
    )

io_dict["pre_selected"] = {"total": len(data_in)}
# 2.3. Keep track of invalid data
# First create a global mask and count failure occurrences
newmask_buffer = StringIO()
logging.info("Removing invalid data")
if chunksize:
    zipped = zip(data_in.data, data_in.mask)
else:
    zipped = zip([data_in.data], [data_in.mask])
for data, mask in zipped:
    mask["global_mask"] = mask.all(axis=1)
    mask.to_csv(newmask_buffer, header=False, mode="a", encoding="utf-8", index=False)

    # 2.3.2. Invalid reports counts and values
    # Initialize counters if first chunk
    masked_columns = [x for x in mask if not all(mask[x].isna()) and x != "global_mask"]
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
if chunksize:
    data_in.mask = pd.read_csv(
        newmask_buffer, names=[x for x in mask], chunksize=chunksize
    )
    data_in.data = pandas_TextParser_hdlr.restore(data_in.data)

# Now see what fails
for col in masked_columns:
    k = ".".join(col)
    if io_dict["invalid"][k]["total"] > 0:
        if data_in.dtypes.get(col, {}) in properties.object_types:
            ivalues = list(set(io_dict["invalid"][k]["values"]))
            # This is because sorting fails on strings if nan
            if np.nan in ivalues:
                ivalues.remove(np.nan)
                ivalues.sort()
                ivalues.append(str(np.nan))
            elif pd.NaT in ivalues:
                ivalues.remove(pd.NaT)
                ivalues.sort()
                ivalues.append(str(pd.NaT))
            else:
                ivalues.sort()
            io_dict["invalid"][k].update(
                {i: io_dict["invalid"][k]["values"].count(i) for i in ivalues}
            )
            sush = io_dict["invalid"][k].pop("values", None)
        elif data_in.dtypes.get(col, {}) in properties.numeric_types:
            values = io_dict["invalid"][k]["values"]
            values = np.array(values)[~pd.isnull(values)]
            if len(values > 0):
                [counts, edges] = np.histogram(values)
                # Following binning approach only if at most 1 sign digit!
                bins = [
                    "-".join([f"{edges[i]:.1f}", f"{edges[i + 1]:.1f}"])
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
data_in, data_false = data_in.split_by_boolean_true()
data_invalid["data"] = data_false.data
data_invalid["valid_mask"] = data_false.mask
io_dict["invalid"]["total"] = len(data_false)
io_dict["processed"] = {"total": len(data_in)}

process = True
if io_dict["processed"]["total"] == 0:
    process = False
    logging.warning("No data to map to CDM after selection and cleaning")

# 2.5 Flag data on blacklist
blck_dict = {}
if params.blacklisting:
    logging.info("Flag data on blacklist")
    if not chunksize:
        data_in_data = [data_in.data]
    else:
        data_in_data = data_in.data

    for data in data_in_data:
        for cdm_table, inputs in params.blacklisting.items():
            func = getattr(blacklist_funcs, inputs["func"])
            kwargs = {}
            for param, columns in inputs["params"].items():
                if isinstance(columns, list):
                    columns = tuple(columns)
                kwargs[param] = columns

            qc_flag = inputs["flag"]
            qc_column = inputs["cdm_column"]
            qc_mask = data.apply(
                lambda row: func(**{k: row[v] for k, v in kwargs.items()}), axis=1
            ).reset_index(drop=True)
            qc_mask.name = qc_column
            qc_mask.flag = qc_flag
            if cdm_table in blck_dict:
                blck_dict[cdm_table] += qc_mask
            else:
                blck_dict[cdm_table] = qc_mask

    if chunksize:
        data_in.data = pandas_TextParser_hdlr.restore(data_in.data)

# 3. Map to common data model and output files
if process:
    logging.info("Mapping to CDM")
    tables = properties.cdm_tables
    io_dict.update({table: {} for table in tables})
    logging.debug(f"Mapping attributes: {data_in.dtypes}")
    data_in.map_model(log_level="INFO", inplace=True)
    for cdm_table, qc_mask in blck_dict.items():
        qc_column = (cdm_table, qc_mask.name)
        cond = qc_mask & data_in.data[qc_column].notna()
        data_in.data.loc[cond, qc_column] = qc_mask.flag
    logging.info("Printing tables to psv files")
    data_in.write(
        out_dir=params.level_path,
        suffix=params.fileID,
    )

    for table in tables:
        io_dict[table]["total"] = inspect.get_length(data_in.data[table])

logging.info("Saving json quicklook")
save_quicklook(params, io_dict, date_handler)


# Output excluded and invalid ---------------------------------------------
if params.filter_reports_by:
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
