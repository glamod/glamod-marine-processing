"""Utility functions/classes for level scripts."""

from __future__ import annotations

import datetime
import glob
import itertools
import json
import logging
import os
import sys
from pathlib import Path

import pandas as pd
from cdm_reader_mapper import DataBundle, read_tables

from glamod_marine_processing.utilities import save_simplejson

delimiter = "|"
FFS = "-"

add_data_paths = {
    "level1a": ["level_excluded_path", "level_invalid_path"],
    "level1b": [],
    "level1c": ["level_invalid_path"],
    "level1d": ["level_log_path"],
    "level1e": ["level_log_path"],
    "level2": ["level_excluded_path", "level_reports_path"],
    "level3": [],
}

chunksizes = {
    "C-RAID_1.1": None,
    "C-RAID_1.2": None,
    "ICOADS_R3.0.2T": 200000,
    "ICOADS_R3.0.0T": 200000,
}

level3_source_ids = {
    "ICOADS-3-0-0T": 1,
    "ICOADS-3-0-2T": 2,
    "CRAID-1.2": 3,
}

level3_columns = [
    "station_name",
    "primary_station_id",
    "report_id",
    "observation_id",
    "longitude",
    "latitude",
    "height_of_station_above_sea_level",
    "report_timestamp",
    "report_meaning_of_time_stamp",
    "report_duration",
    "observed_variable",
    "units",
    "observation_value",
    "quality_flag",
    "source_id",
    "data_policy_licence",
    "platform_type",
    "report_type",
    "value_significance",
]

level3_mappings = {
    "header": {
        "station_name": "station_name",
        "primary_station_id": "primary_station_id",
        "report_id": "report_id",
        "longitude": "longitude",
        "latitude": "latitude",
        "height_of_station_above_sea_level": "height_of_station_above_sea_level",
        "report_timestamp": "report_timestamp",
        "report_meaning_of_time_stamp": "report_meaning_of_timestamp",
        "report_duration": "report_duration",
        "source_id": "source_id",
        "report_type": "report_type",
        "platform_type": "platform_type",
    },
    "observations": {
        "observation_id": "observation_id",
        "observed_variable": "observed_variable",
        "units": "units",
        "observation_value": "observation_value",
        "quality_flag": "quality_flag",
        "data_policy_licence": "data_policy_licence",
        "value_significance": "value_significance",
    },
}

level3_dtypes = {
    "station_name": "string",
    "primary_station_id": "string",
    "report_id": "string",
    "observation_id": "string",
    "longitude": "float64",
    "latitude": "float64",
    "height_of_station_above_sea_level": "float64",
    "report_timestamp": "datetime64[ns, UTC]",
    "report_meaning_of_time_stamp": "Int64",
    "report_duration": "Int64",
    "observed_variable": "Int64",
    "units": "Int64",
    "observation_value": "float64",
    "quality_flag": "Int64",
    "source_id": "Int64",
    "data_policy_licence": "Int64",
    "platform_type": "Int64",
    "report_type": "Int64",
    "value_significance": "Int64",
}


def add_utc_offset(series):
    """Add utc offset +00 to datetime object string."""
    return series.astype(str) + "+00"


def get_integer_source_id(series):
    """Rank source id as integer value."""
    return series.rank(method="dense").astype(int)


def set_default_source_id(series):
    """Set default source_id (dataset-specific)."""
    pattern = "|".join(level3_source_ids.keys())
    s = series.str.extract(rf"({pattern})")[0]
    return s.map(level3_source_ids)


def set_default_report_duration(series):
    """Set default report_duration 8 (10 minutes)."""
    s = series[:].copy()
    s[:] = "8"
    return s


level3_conversions = {
    "report_timestamp": add_utc_offset,
    "source_id": set_default_source_id,
    "report_duration": set_default_report_duration,
}


def convert_dtypes(df, dtypes):
    """Convert data types."""
    for col, dtype in dtypes.items():
        if dtype.startswith("datetime64[ns]"):
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.tz_convert("UTC")
        else:
            df[col] = df[col].astype(dtype)

    return df


# Functions--------------------------------------------------------------------
class script_setup:
    """Create script."""

    def __init__(self, process_options, inargs, clean=False):
        if len(inargs) <= 1:
            logging.error("Need arguments to run!")
            sys.exit(1)

        configfile = inargs[1]

        try:
            with open(configfile) as fileObj:
                config = json.load(fileObj)
        except Exception:
            logging.error(f"Opening configuration file: {configfile}", exc_info=True)
            sys.exit(1)

        if len(sys.argv) >= 8:
            logging.warning(
                "Removed option to provide sid_dck, year and month as arguments. Use config file instead"
            )
        self.dataset = config["abbreviations"].get("dataset")

        sid_dck = config.get("sid_dck")
        self.sid_dck = sid_dck
        self.year = config.get("yyyy")
        self.month = config.get("mm")

        self.year_init = config.get("year_init")
        self.year_end = config.get("year_end")

        if "-" in sid_dck:
            self.dck = sid_dck.split("-")[1]
        else:
            self.dck = sid_dck
        self.corrections = config.get("corrections")
        self.corrections_mod = config.get("corrections_mod")

        try:
            for opt in process_options:
                if not config.get(sid_dck, {}).get(opt):
                    setattr(self, opt, config.get(opt))
                else:
                    setattr(self, opt, config.get(sid_dck).get(opt))
        except Exception:
            logging.error(
                f"Parsing configuration from file: {configfile}", exc_info=True
            )
            sys.exit(1)

        self.data_path = config["paths"].get("data_directory")
        self.release = config["abbreviations"].get("release")

        self.filename = config.get("filename")
        self.level2_list = config.get("cmd_add_file")
        self.prev_fileID = config.get("prev_fileID")
        self.release_id = config["abbreviations"].get("release_tag")
        self.fileID = FFS.join(
            [str(self.year), str(self.month).zfill(2), self.release_id]
        )
        self.fileID_date = FFS.join([str(self.year), str(self.month)])
        if self.prev_fileID is None:
            self.prev_fileID = self.fileID

        self.prev_level_path = os.path.join(
            config["paths"]["source_directory"], sid_dck
        )
        level_path = config["paths"]["destination_directory"]
        self.level_path = os.path.join(level_path, sid_dck)
        self.level_ql_path = os.path.join(level_path, "quicklooks", sid_dck)
        self.level_log_path = os.path.join(level_path, "log", sid_dck)
        self.level_invalid_path = os.path.join(level_path, "invalid", sid_dck)
        self.level_excluded_path = os.path.join(level_path, "excluded", sid_dck)
        self.level_reports_path = os.path.join(level_path, "reports", sid_dck)
        data_paths = [
            self.prev_level_path,
            self.level_path,
            self.level_ql_path,
        ]
        for data_path in add_data_paths[config["level"]]:
            data_paths.append(getattr(self, data_path))
        paths_exist(data_paths)
        if len(glob.glob(self.filename)) == 0:
            logging.error(f"Previous level header files not found: {self.filename}")
            sys.exit(1)

        filenames = [
            glob.glob(f"{data_path}/**/*", recursive=True)
            for data_path in data_paths[1:]
        ]

        if clean is True:
            clean_level(filenames)


def date_handler(obj):
    """Handle date."""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()


def clean_level(filenames):
    """Clean level."""
    filenames = list(itertools.chain(*filenames))
    for filename in filenames:
        try:
            logging.info(f"Removing previous file: {filename}")
            os.remove(filename)
        except Exception:
            logging.warning(f"Could not remove previous file: {filename}")
            pass


def paths_exist(data_paths):
    """Check whether path(s) exist(s)."""
    if not isinstance(data_paths, list):
        data_paths = [data_paths]
    exit = False
    for data_path in data_paths:
        if not os.path.isdir(data_path):
            exit = True
            logging.error(f"Could not find data paths: {data_path}")
    if exit is True:
        sys.exit(1)


def save_quicklook(params, ql_dict, date_handler):
    """Save quicklook file."""
    ql_filename = os.path.join(params.level_ql_path, f"{params.fileID}.json")
    ql_dict["date processed"] = datetime.datetime.now()
    ql_dict = {params.fileID_date: ql_dict}
    save_simplejson(
        ql_dict, ql_filename, default=date_handler, indent=4, ignore_nan=True
    )


def read_cdm_tables(params, table, ifile=None):
    """Read CDM tables."""
    kwargs = {
        "cdm_subset": table,
        "na_values": "null",
    }
    if ifile is None:
        ifile_pattern = os.path.join(
            params.prev_level_path, f"{table}*{params.prev_fileID}*"
        )
        if len(glob.glob(ifile_pattern)) == 0:
            logging.warning(f"CDM file pattern not found: {ifile_pattern}.")
            return DataBundle()
        return read_tables(params.prev_level_path, suffix=params.prev_fileID, **kwargs)

    if not os.path.isfile(ifile):
        logging.warning(f"CDM file not found: {ifile}.")
        return DataBundle()

    db = read_tables(ifile, **kwargs)
    db.data.columns = pd.MultiIndex.from_tuples([table, col] for col in db.data.columns)
    return db


def write_cdm_tables(
    params, df, tables=[], outname=None, mode="csv", dtypes={}, **kwargs
):
    """Write table to disk."""
    if df.empty:
        return
    if isinstance(tables, str):
        tables = [tables]
    for table in tables:
        if mode == "csv":
            ext = "psv"
        elif mode == "parquet":
            ext = "pq"
        else:
            raise ValueError(f"Unknown mode: {mode}. Use 'csv' or 'parquet'.")
        if outname is None:
            outname = os.path.join(
                params.level_path, f"{FFS.join([table, params.fileID])}"
            )
        p = Path(outname)
        if p.suffix == "":
            outname = f"{outname}.{ext}"
        try:
            df = df[table]
        except KeyError:
            logging.info(f"Table {table} is already selected.")
        df = convert_dtypes(df, dtypes)
        if mode == "csv":
            df.to_csv(
                outname,
                index=False,
                sep=delimiter,
                header=True,
                mode="w",
                na_rep="null",
                **kwargs,
            )
        elif mode == "parquet":
            df.to_parquet(
                outname,
                index=False,
                engine="pyarrow",
                compression="snappy",
                **kwargs,
            )
        logging.info(f"Output file written: {outname}.")
