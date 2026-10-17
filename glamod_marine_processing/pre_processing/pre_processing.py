"""Split original ICOADS data into monthly source and deck files."""

from __future__ import annotations

import glob
import json
import os
from pathlib import Path
from shutil import copyfile

import xarray as xr

# number of lines to store in each cache
maxLines = 1000
# columns for respective variables
parse_dict = {
    "dck": [118, 121],
    "sid": [121, 124],
    "platformType": [124, 126],
    "callsign": [34, 43],
    "year": [0, 4],
    "month": [4, 6],
    "day": [6, 8],
    "hour": [8, 12],
    "latitude": [12, 17],
    "longitude": [17, 23],
}

# default input file source pattern
_dataset = "ICOADS_R3.0.2T"
_source_pattern = {
    "ICOADS_R3.0.2T": "IMMA1_R3.0.*",
    "ICOADS_R3.0.0T": "IMMA1_R3.0.*",
    "C-MEMS_2.0": "GL_TS_DB_*",
}


def get_cell(lon, lat, xmin, xmax, xstep, ymin, ystep):
    """Get lat-lon cell."""
    nx = int((xmax - xmin) // xstep)
    xind = int((lon - xmin) // xstep)
    yind = int((lat - ymin) // ystep)
    cell = nx * yind + xind
    x1 = xind * xstep
    x2 = (xind + 1) * xstep
    y1 = yind * ystep
    y2 = (yind + 1) * ystep
    cell = {"id": cell, "xmin": x1, "xmax": x2, "ymin": y1, "ymax": y2, "count": 0}
    return cell


def parse_line(line, entry):
    """Parse line."""
    values = parse_dict[entry]
    return line[values[0] : values[-1]]


def get_outfile_name(basepath, tag, dataset, year, month):
    """Generate output file name."""
    filename = f"{dataset}_{tag}_{year:04d}-{month:02d}"
    return f"{basepath}/{tag}/{os.path.basename(filename)}"


class deck_store:
    """Class to store info for each source / deck."""

    def __init__(self, dataset, tag, year, month, basepath):
        Path(f"{basepath}/{tag}").mkdir(parents=True, exist_ok=True)
        self.outfile = get_outfile_name(basepath, tag, dataset, year, month)
        self.count = 0
        self.linecache = list()
        self.fh = open(self.outfile, "w")
        self.summary = dict()
        self.summary["bbox"] = dict()
        self.summary["bbox"]["minLongitude"] = 360
        self.summary["bbox"]["maxLongitude"] = -360
        self.summary["bbox"]["minLatitude"] = 90
        self.summary["bbox"]["maxLatitude"] = -90
        self.summary["callsigns"] = dict()
        self.summary["platforms"] = dict()
        self.summary["year"] = dict()
        self.summary["dck"] = dict()

    def set_path(self, dataset, tag, year, month, basepath):
        """Set data path."""
        outfile = get_outfile_name(basepath, tag, dataset, year, month)
        if self.outfile != outfile:
            self.close()
            self.outfile = outfile
            self.fh = open(self.outfile, "w")

    def add_line(self, line):
        """Extract the data to be used when summarising deck."""
        latitude = float(parse_line(line, "latitude")) * 0.01
        longitude = float(parse_line(line, "longitude")) * 0.01
        if longitude >= 180:
            longitude = longitude - 360
        year = int(parse_line(line, "year"))
        dck = parse_line(line, "dck")
        platform = parse_line(line, "platformType")
        callsign = parse_line(line, "callsign")
        cell = get_cell(longitude, latitude, -180, 180, 5, -90, 5)

        if callsign in self.summary["callsigns"]:
            self.summary["callsigns"][callsign] += 1
        else:
            self.summary["callsigns"][callsign] = 1

        if platform in self.summary["platforms"]:
            self.summary["platforms"][platform] += 1
        else:
            self.summary["platforms"][platform] = 1

        if year in self.summary["year"]:
            self.summary["year"][year]["count"] += 1
        else:
            self.summary["year"][year] = dict()
            self.summary["year"][year]["count"] = 1

        if cell["id"] not in self.summary["year"][year]:
            self.summary["year"][year][cell["id"]] = cell
        self.summary["year"][year][cell["id"]]["count"] += 1

        if dck in self.summary["dck"]:
            self.summary["dck"][dck] += 1
        else:
            self.summary["dck"][dck] = 1

        self.linecache.append(line)
        self.count += 1

        # add summary statistics

        self.summary["bbox"]["minLatitude"] = min(
            self.summary["bbox"]["minLatitude"], latitude
        )
        self.summary["bbox"]["maxLatitude"] = max(
            self.summary["bbox"]["maxLatitude"], latitude
        )

        # add summary statistics

        self.summary["bbox"]["minLongitude"] = min(
            self.summary["bbox"]["minLongitude"], longitude
        )
        self.summary["bbox"]["maxLongitude"] = max(
            self.summary["bbox"]["maxLongitude"], longitude
        )

        if len(self.linecache) == maxLines:
            self.write_cache()

    def write_cache(self):
        """Write line cache."""
        self.fh.writelines(self.linecache)
        self.linecache = list()

    def close(self):
        """Close file."""
        self.write_cache()
        self.fh.close()


def pre_processing(
    idir,
    odir,
    dataset=None,
    source_pattern=None,
    overwrite=False,
):
    """Split ICOADS data into monthly deck files.
    Use this function to create obs_suite level0 data.

    Parameters
    ----------
    idir: str
        Input data directory
    odir: str
        Output data directory
    dataset: str, default: ICOADS_R3.0.2T
        Name of input dataset.
    source_pattern: str, default: IMMA1_R3.0.*
        Input source pattern.
    overwrite: bool
        If True, overwrite already existing files.
    """
    # get list of files to process
    if dataset is None:
        dataset = _dataset
    if source_pattern is None:
        source_pattern = _source_pattern[dataset]
    infiles = sorted(glob.glob(f"{idir}/{source_pattern}"))
    # get number of files
    nfiles = len(infiles)
    print(f"{nfiles} files found in folder {idir}")
    # initialise dictionary to store data
    decks = dict()
    # now iterate over files
    for infile in infiles:
        # get current file to process
        print(f"Pre-Processing {infile}")

        if "ICOADS" in dataset:
            fh = open(infile, encoding="cp1252")

            for line in fh.readlines():
                # get source Id and deck
                dck = int(parse_line(line, "dck"))
                sid = int(parse_line(line, "sid"))
                year = int(parse_line(line, "year"))
                month = int(parse_line(line, "month"))
                # set tag for data
                tag = f"{sid:03d}-{dck:03d}"
                # Initialise deck or update output path
                if tag not in decks:
                    decks[tag] = deck_store(dataset, tag, year, month, odir)
                else:
                    decks[tag].set_path(dataset, tag, year, month, odir)
                # add ICOADS record to deck
                decks[tag].add_line(line)
            fh.close()

        elif "C-MEMS" in dataset:
            if ".nc" not in infile:
                continue

            ds = xr.open_dataset(infile)
            transmitter = ds.attrs.get("transmitter_system", None)
            ds.close()

            if transmitter != "IRIDIUM":
                print("Skip: not a IRIDIUM drifter.")
                continue

            ofile_name = infile.split("/")[-1]
            ofile_dir = os.path.join(odir, ofile_name.split(".")[0])
            if not os.path.exists(ofile_dir):
                os.mkdir(ofile_dir)

            ofile = os.path.join(ofile_dir, ofile_name)
            copyfile(infile, ofile)
            print(f"Copy IRIDIUM drifter to: {ofile}")
        else:
            raise ValueError(f"dataset: {dataset} must contain 'ICOADS' or 'C-MEMS'.")

    # now make sure all files are closed and write summaries to file
    if decks:
        for dck in decks:
            with open(f"{dck}.json", "w") as ofh:
                json.dump(decks[dck].summary, ofh)
            decks[dck].close()
