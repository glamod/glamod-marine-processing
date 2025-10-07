"""Utility functions/classes for level scripts."""

from __future__ import annotations

import datetime
import glob
import itertools
import json
import logging
import os
import sys

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

level3_columns = [
    ("header", "station_name"),
    ("header", "primary_station_id"),
    ("header", "report_id"),
    ("observations-slp", "observation_id"),
    ("header", "longitude"),
    ("header", "latitude"),
    ("header", "height_of_station_above_sea_level"),
    ("header", "report_timestamp"),
    ("header", "report_meaning_of_timestamp"),
    ("header", "report_duration"),
    ("observations-slp", "observed_variable"),
    ("observations-slp", "units"),
    ("observations-slp", "observation_value"),
    ("observations-slp", "quality_flag"),
    ("header", "source_id"),
    ("observations-slp", "data_policy_licence"),
    ("header", "report_type"),
    ("observations-slp", "value_significance"),
]


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


def write_cdm_tables(params, df, tables=[], outname=None, **kwargs):
    """Write table to disk."""
    if df.empty:
        return
    if isinstance(tables, str):
        tables = [tables]
    for table in tables:
        if outname is None:
            outname = os.path.join(
                params.level_path, f"{FFS.join([table, params.fileID])}.psv"
            )
        try:
            df = df[table]
        except KeyError:
            logging.info(f"Table {table} is already selected.")
        df.to_csv(
            outname,
            index=False,
            sep=delimiter,
            header=True,
            mode="w",
            na_rep="null",
            **kwargs,
        )
