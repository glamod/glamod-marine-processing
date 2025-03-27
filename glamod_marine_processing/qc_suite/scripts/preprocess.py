"""
Created on Wed Aug  3 09:37:04 2022

@author: sbiri
"""

from __future__ import annotations

import argparse
import json
import os

import numpy as np
import pandas as pd
from _qc_settings import excols_, obs_vals_, outcols_, selcols_, usecols_
from cdm_reader_mapper.cdm_mapper import read_tables

"""
simplified version of preprocess.py in qc_suite
 It reads in:
    valid data from level1d
    level1a PT=7 data (in invalid or excluded directory)
It exports a psv file
"""

print("########################")
print("Running preprocessing")
print("########################")

parser = argparse.ArgumentParser(description="Marine QC system, preprocessing program")
parser.add_argument(
    "-source", type=str, help="Path to level1d data files", required=True
)
parser.add_argument("-dck_list", type=str, help="Deck list txt file.", required=True)
parser.add_argument(
    "-dck_period", type=str, help="Deck list period json file.", required=True
)
parser.add_argument(
    "-destination", type=str, help="Path to output directory", required=True
)
parser.add_argument(
    "-release", type=str, help="Release identifier, e.g. release_8.0", required=True
)
parser.add_argument(
    "-update", type=str, help="Update identifier, e.g. 000000", required=True
)

args = parser.parse_args()

in_dir = args.source
out_dir = args.destination
dck_lst = args.dck_list
dck_p = args.dck_period
rel_id = args.release
upd_id = args.update

with open(dck_lst) as fO:
    dck_list = fO.read().splitlines()

with open(dck_p) as fO:
    dck_period = json.load(fO)

if "year_init" in dck_period.keys():
    yi = dck_period.get("year_init")
    ye = dck_period.get("year_end")
else:
    for dl in dck_list[0]:
        yi = dck_period[dl].get("year_init")
        ye = dck_period[dl].get("year_end")
        if yi and ye:
            break

y_init = np.minimum(yi, 2022)
y_end = np.maximum(ye, 1948)

for yr in range(y_init - 1, y_end + 2):
    # expanded to include dec of the previous year and jan of the following, for buddy checks (i think)
    if yr == y_init - 1:
        mos = [12]
    elif yr == y_end + 1:
        mos = [1]
    else:
        mos = range(1, 13)

    for mo in mos:
        print(yr, mo)
        # %% load duplicates flags
        data = pd.DataFrame()

        for dl in dck_list:
            print(dl)
            data_dl = pd.DataFrame()
            # read tables from level1d
            # from header get YR, MO, 'DY', 'HR', 'LAT', 'LON', 'ID',
            # 'DCK', 'SID', 'PT', 'UID', 'IRF', 'DS', 'VS'
            fn = os.path.join(
                in_dir,
                dl,
                "header-" + str(yr) + "-" + f"{mo:02d}" + f"-{rel_id}-{upd_id}.psv",
            )
            tmp = read_tables(
                os.path.join(in_dir, dl),
                f"{yr}-{mo:02d}-{rel_id}-{upd_id}",
                cdm_subset=["header"],
            )
            if not tmp.empty:
                tmp = tmp.rename(
                    columns={
                        "latitude": "LAT",
                        "longitude": "LON",
                        "primary_station_id": "ID",
                        "platform_type": "PT",
                        "report_id": "UID",
                        "report_quality": "IRF",
                        "station_course": "DS",
                        "station_speed": "VS",
                        "duplicate_status": "dup_flag",
                        "duplicates": "dups",
                    }
                )
                tmp["YR"] = tmp["report_timestamp"].apply(lambda x: x[0:4])
                tmp["MO"] = tmp["report_timestamp"].apply(lambda x: x[5:7])
                tmp["DY"] = tmp["report_timestamp"].apply(lambda x: x[8:10])
                tmp["HR"] = tmp["report_timestamp"].apply(lambda x: x[11:13])
                tmp["DCK"] = tmp["source_id"].apply(lambda x: x[18:21])
                tmp["SID"] = tmp["source_id"].apply(lambda x: x[14:17])
                data_dl = tmp[usecols_]
                # reset IRF as in imma before cdm
                loc0 = data_dl.IRF != 1
                loc1 = data_dl.IRF == 1
                data_dl.loc[loc0].IRF = 1
                data_dl.loc[loc1].IRF = 0
                data_dl = data_dl.set_index("UID")

            for obs_val, obs_name in obs_vals_.items():
                # %%from obsevations_at,
                tmp = read_tables(
                    os.path.join(in_dir, dl),
                    f"{yr}-{mo:02d}-{rel_id}-{upd_id}",
                    cdm_subset=[f"observations-{obs_name}"],
                )
                if not tmp.empty:
                    tmp = tmp.rename(
                        columns={
                            "report_id": "UID",
                            "observation_value": obs_val,
                        }
                    )
                    if obs_val not in ["W", "D"]:
                        tmp = tmp.astype({obs_val: "float"})
                    tmp = tmp[["UID", obs_val]].set_index("UID")
                    if obs_val in ["AT", "SST", "DPT"]:
                        tmp[obs_val] = tmp[obs_val] - 273.15  # reset to Celsius
                    elif obs_val == "SLP":
                        tmp[obs_val] = tmp[obs_val] / 100
                    data_dl = data_dl.merge(tmp, on="UID", how="left")

            # %% 'bad_data' set to False
            if not data_dl.empty:
                data_dl["bad_data"] = False
                # #%% 'outfile' set to MSNG
                data_dl["outfile"] = None

            # %% load drifter data PT=7 from level1a excluded
            fn = os.path.join(
                in_dir.replace("level1d", "level1a"),
                "excluded",
                dl,
                str(yr) + "-" + f"{mo:02d}" + f"-{rel_id}-{upd_id}-c1_PT.psv",
            )
            if os.path.exists(fn):
                print("Looking for drifters")
                drifters = pd.read_csv(
                    fn,
                    delimiter="|",
                    dtype="object",
                    header=None,
                    skiprows=2,
                    names=excols_,
                    usecols=lambda c: c in set(selcols_),
                )

                drifters = drifters[drifters["PT"] == "7"]
                if not drifters.empty:
                    print("Adding drifters")
                    drifters["bad_data"] = False
                    drifters["outfile"] = None
                    drifters["dup_flag"] = None
                    # here UID is source_uid; add prepend
                    prepend = "ICOADS-302-"
                    drifters["UID"] = prepend + drifters["UID"]
                    drifters = drifters.set_index("UID")
                    # add to data dataframe
                    data_dl = pd.concat([data_dl, drifters])  # , ignore_index=True)

            if data_dl.empty:
                print("Dataframe is empty. Skipping")
                continue

            # find duplicates in list
            # unique_duplicates = list(set(duplicates))
            # %% merge duplicate flags
            # Need to replace NaNs in dup_flag column with 4s
            data_dl["dup_flag"] = data_dl["dup_flag"].fillna("4")
            # For drifters we need to replace dup with the IRF flag

            data_dl.loc[
                (data_dl["PT"] == "7") & (data_dl["IRF"] == "1"), "dup_flag"
            ] = "0"  # unique
            data_dl.loc[
                (data_dl["PT"] == "7") & (data_dl["IRF"] != "1"), "dup_flag"
            ] = "3"  # worst duplicate

            # convert to int
            data_dl = data_dl.astype({"dup_flag": "int32"})
            data_dl = data_dl.astype({"PT": "int32"})
            # exclude bad rows and rows we dont otherwise want to process
            # -----------------------------------------------------------
            # bad data_dl (that didn't validate against IMMA schema)
            bad_data = data_dl["bad_data"]

            # ship only
            ship = [np.nan, 0, 1, 2, 3, 4, 5, 7]
            ship_mask = data_dl["PT"].apply(lambda x: x in ship)

            # Duplicate  flags
            dups_to_use = [0, 1, 4]
            dup_field = "dup_flag"
            duplicate_mask = data_dl[dup_field].apply(lambda x: x in dups_to_use)

            # now apply masking to data frame
            data_dl = data_dl[((~bad_data) & ship_mask & duplicate_mask)]

            data = pd.concat([data, data_dl])

        # data.reset_index(inplace=True)
        if data.empty:
            print("All dataframes are empty")
        else:
            out_file = os.path.join(out_dir, f"{yr:04d}-{mo:02d}.psv")
            print(f"Writing file: {out_file}")
            data = data.sort_values(
                ["YR", "MO", "DY", "HR", "UID"], axis=0, ascending=True
            )
            data["UID"] = data.index
            data = data.reindex(columns=outcols_)
            data.to_csv(
                out_file,
                sep="|",
                header=False,
                index=False,
                compression="infer",
            )
