"""Utility functions/classes for level scripts."""

from __future__ import annotations

import datetime
import glob
import itertools
import json
import logging
import os
import sys

delimiter = "|"
FFS = "-"

add_data_paths = {
    "level1a": ["level_excluded_path", "level_invalid_path"],
    "level1b": [],
    "level1c": ["level_invalid_path"],
    "level1d": ["level_log_path"],
    "level1e": ["level_log_path"],
    "level2": ["level_excluded_path", "level_reports_path"],
}


# Functions--------------------------------------------------------------------
class script_setup:
    """Create script."""

    def __init__(self, process_options, inargs, level, level_prev):
        self.data_path = inargs[1]
        self.release = inargs[2]
        self.update = inargs[3]
        self.dataset = inargs[4]
        self.configfile = inargs[5]

        try:
            with open(self.configfile) as fileObj:
                config = json.load(fileObj)
        except Exception:
            logging.error(
                f"Opening configuration file :{self.configfile}", exc_info=True
            )
            self.flag = False
            return

        if len(sys.argv) >= 8:
            logging.warning(
                "Removed option to provide sid_dck, year and month as arguments. Use config file instead"
            )
        if len(sys.argv) > 6:
            self.sid_dck = inargs[6]
            self.year = inargs[7]
            self.month = inargs[8]
        else:
            self.sid_dck = config.get("sid_dck")
            self.year = config.get("yyyy")
            self.month = config.get("mm")

        self.dck = self.sid_dck.split("-")[1]
        self.corrections = config.get("corrections")

        try:
            for opt in process_options:
                if not config.get(self.sid_dck, {}).get(opt):
                    setattr(self, opt, config.get(opt))
                else:
                    setattr(self, opt, config.get(self.sid_dck).get(opt))
            self.flag = True
        except Exception:
            logging.error(
                f"Parsing configuration from file :{self.configfile}", exc_info=True
            )
            self.flag = False

        self.filename = config.get("filename")
        self.level2_list = config.get("cmd_add_file")
        self.prev_fileID = config.get("prev_fileID")
        self.release_path = os.path.join(self.data_path, self.release, self.dataset)
        self.release_id = FFS.join([self.release, self.update])
        self.fileID = FFS.join(
            [str(self.year), str(self.month).zfill(2), self.release_id]
        )
        self.fileID_date = FFS.join([str(self.year), str(self.month)])
        if self.prev_fileID is None:
            self.prev_fileID = self.fileID

        if level == "level1a":
            self.prev_level_path = os.path.join(
                self.data_path, "datasets", self.dataset, "level0", self.sid_dck
            )
        else:
            self.prev_level_path = os.path.join(
                self.release_path, level_prev, self.sid_dck
            )
        self.level_path = os.path.join(self.release_path, level, self.sid_dck)
        self.level_ql_path = os.path.join(
            self.release_path, level, "quicklooks", self.sid_dck
        )
        self.level_log_path = os.path.join(
            self.release_path, level, "log", self.sid_dck
        )
        self.level_invalid_path = os.path.join(
            self.release_path, level, "invalid", self.sid_dck
        )
        self.level_excluded_path = os.path.join(
            self.release_path, level, "excluded", self.sid_dck
        )
        self.level_reports_path = os.path.join(
            self.release_path, level, "reports", self.sid_dck
        )
        data_paths = [
            self.prev_level_path,
            self.level_path,
            self.level_ql_path,
        ]
        for data_path in add_data_paths[level]:
            data_paths.append(getattr(self, data_path))
        paths_exist(data_paths)

        if len(glob.glob(self.filename)) == 0:
            logging.error(f"Previous level header files not found: {self.filename}")
            sys.exit(1)

        filenames = [
            glob.glob(f"{data_path}/**/*", recursive=True)
            for data_path in data_paths[1:]
        ]
        clean_level(filenames)


# This is for json to handle dates
def date_handler(obj):
    """Handle date."""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()


def table_to_csv(df, out_name, **kwargs):
    """Write table to disk."""
    if len(df) == 0:
        return
    df.to_csv(
        out_name,
        index=False,
        sep=delimiter,
        header=True,
        mode="w",
        na_rep="null",
        **kwargs,
    )


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
