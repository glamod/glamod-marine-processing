from __future__ import annotations

import numpy as np

data_model = "icoads"
release = "r302"
deck = "d992"
input_dir = f"{data_model}/{release}/{deck}"
cdm = f"icoads_{release}_{deck}_2022-01-01_subset"
suffix = "imma"
level0 = f"{input_dir}/input/{cdm}.{suffix}"
release = "release_8.0"

process_list = "114-992"
year_init = "2020"
year_end = "2025"

table_names = [
    "header",
    "observations-at",
    "observations-dpt",
    "observations-slp",
    "observations-sst",
    "observations-wbt",
    "observations-wd",
    "observations-ws",
]

table_names_next = [
    "header",
    "observations-at",
    "observations-dpt",
    "observations-slp",
    "observations-sst",
    "observations-wd",
    "observations-ws",
]

prev_level = {
    "level1a": "level0",
    "level1b": "level1a",
    "level1c": "level1b",
    "level1d": "level1c",
    "level1e": "level1d",
    "level2": "level1e",
    "level3": "level2",
}

level_input = {
    "level1a": "datasets",
    "level1b": release,
    "level1c": release,
    "level1d": release,
    "level1e": release,
    "level2": release,
    "level3": release,
}

which_tables = {
    "level1a": table_names,
    "level1b": table_names_next,
    "level1c": table_names_next,
    "level1d": table_names_next,
    "level1e": table_names_next,
    "level2": table_names_next,
    "level3": table_names_next,
}

pattern = {
    "level1a": "icoads_r???_d???_????-??-??_subset.imma",
    "level1b": "header-icoads_r???_d???_????-??-??_subset.psv",
    "level1c": "header-icoads_r???_d???_????-??-??_subset.psv",
    "level1d": "header-icoads_r???_d???_????-??-??_subset.psv",
    "level1e": "header-icoads_r???_d???_????-??-??_subset.psv",
    "level2": "header-icoads_r???_d???_????-??-??_subset.psv",
    "level3": "header-icoads_r???_d???_????-??-??_subset.psv",
}
pattern_out = {"level3": f"pressure-data-2022-01-{release}-000000.psv"}

manipulation = {
    "level1b": {
        ("header", "duplicate_status"): [
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "1",
            "1",
            "3",
            "3",
            "3",
        ],
        ("header", "report_quality"): [
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "1",
            "1",
            "1",
        ],
        ("header", "duplicates"): [
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "{ICOADS-302-LQWUT8}",
            "{ICOADS-302-LQWUT6,ICOADS-302-LQWUT7}",
            "{ICOADS-302-LQWUT5}",
            "{ICOADS-302-LQWUT5}",
            "{ICOADS-302-LQWUT4}",
        ],
    },
    "level1d": {
        ("header", "station_name"): [
            "null",
            "FF HELMER HANSEN",
            "WAVERIDER TFSTD",
            "null",
            "WAVERIDER TFDRN",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
        ],
        ("header", "platform_sub_type"): [
            "null",
            "RV",
            "OT",
            "null",
            "OT",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
        ],
        ("header", "station_record_number"): [
            "1",
            "1",
            "0",
            "1",
            "0",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
        ],
        ("header", "report_duration"): [
            "11",
            "HLY",
            "11",
            "11",
            "11",
            "11",
            "11",
            "11",
            "11",
            "11",
            "11",
            "11",
            "11",
        ],
        ("observations-at", "sensor_id"): [
            "null",
            "AT",
            np.nan,
            "null",
            np.nan,
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
        ],
        ("observations-dpt", "sensor_id"): [
            np.nan,
            "HUM",
            np.nan,
            "null",
            np.nan,
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
        ],
        ("observations-slp", "sensor_id"): [
            "null",
            "SLP",
            np.nan,
            "null",
            np.nan,
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
        ],
        ("observations-sst", "sensor_id"): [
            "null",
            "SST",
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
        ],
        ("observations-wd", "sensor_id"): [
            "null",
            "WSPD",
            np.nan,
            "null",
            np.nan,
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
        ],
        ("observations-ws", "sensor_id"): [
            "null",
            "WSPD",
            np.nan,
            "null",
            np.nan,
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
            "null",
        ],
        ("observations-at", "sensor_automation_status"): [
            "5",
            "3",
            np.nan,
            "5",
            np.nan,
            "5",
            "5",
            "5",
            "5",
            "5",
            "5",
            "5",
            "5",
        ],
        ("observations-dpt", "sensor_automation_status"): [
            np.nan,
            "3",
            np.nan,
            "5",
            np.nan,
            "5",
            "5",
            "5",
            "5",
            "5",
            "5",
            "5",
            "5",
        ],
        ("observations-slp", "sensor_automation_status"): [
            "5",
            "3",
            np.nan,
            "5",
            np.nan,
            "5",
            "5",
            "5",
            "5",
            "5",
            "5",
            "5",
            "5",
        ],
        ("observations-sst", "sensor_automation_status"): [
            "5",
            "3",
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
        ],
        ("observations-wd", "sensor_automation_status"): [
            "5",
            "3",
            np.nan,
            "5",
            np.nan,
            "5",
            "5",
            "5",
            "5",
            "5",
            "5",
            "5",
            "5",
        ],
        ("observations-ws", "sensor_automation_status"): [
            "5",
            "3",
            np.nan,
            "5",
            np.nan,
            "5",
            "5",
            "5",
            "5",
            "5",
            "5",
            "5",
            "5",
        ],
    },
    "level1e": {
        ("header", "report_quality"): [
            "0",
            "0",
            "1",
            "0",
            "1",
            "0",
            "0",
            "0",
            "0",
            "0",
            "2",
            "2",
            "2",
        ],
        ("observations-at", "quality_flag"): [
            "1",
            "1",
            np.nan,
            "0",
            np.nan,
            "0",
            "0",
            "0",
            "0",
            "0",
            "2",
            "2",
            "2",
        ],
        ("observations-dpt", "quality_flag"): [
            np.nan,
            "0",
            np.nan,
            "0",
            np.nan,
            "0",
            "0",
            "0",
            "0",
            "0",
            "2",
            "2",
            "2",
        ],
        ("observations-slp", "quality_flag"): [
            "0",
            "0",
            np.nan,
            "0",
            np.nan,
            "0",
            "0",
            "0",
            "0",
            "0",
            "2",
            "2",
            "2",
        ],
        ("observations-sst", "quality_flag"): [
            "0",
            "0",
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
        ],
        ("observations-wd", "quality_flag"): [
            "0",
            "0",
            np.nan,
            "0",
            np.nan,
            "0",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
            "1",
        ],
        ("observations-ws", "quality_flag"): [
            "0",
            "0",
            np.nan,
            "0",
            np.nan,
            "1",
            "0",
            "0",
            "1",
            "1",
            "1",
            "1",
            "1",
        ],
    },
    "level3": [
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
    ],
}

drops = {
    "level1a": [0, 5, 6, 7, 9, 10, 11],
    "level1c": [0, 3],
    "level1d": [1, 2, 4],
    "level1e": [2, 4],
    "level3": [2, 4],
}
