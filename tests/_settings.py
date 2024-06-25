from __future__ import annotations

import numpy as np

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

table_names_1b = [
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
}

level_input = {
    "level1a": "datasets",
    "level1b": "release_7.0",
    "level1c": "release_7.0",
    "level1d": "release_7.0",
    "level1e": "release_7.0",
    "level2": "release_7.0",
}

which_tables = {
    "level1a": table_names,
    "level1b": table_names_1b,
    "level1c": table_names_1b,
    "level1d": table_names_1b,
    "level1e": table_names_1b,
    "level2": table_names_1b,
}

pattern = {
    "level1a": "???-???_????-??-??_subset.imma",
    "level1b": "header-???-???_????-??-??_subset.psv",
    "level1c": "header-???-???_????-??-??_subset.psv",
    "level1d": "header-???-???_????-??-??_subset.psv",
    "level1e": "header-???-???_????-??-??_subset.psv",
    "level2": "header-???-???_????-??-??_subset.psv",
}

manipulation = {
    "level1c": {},
    "level1d": {
        ("header", "station_name"): [
            "null",
            "FF HELMER HANSEN",
            "WAVERIDER TFSTD",
            "null",
            "WAVERIDER TFDRN",
        ],
        ("header", "platform_sub_type"): ["null", "RV", "OT", "null", "OT"],
        ("header", "station_record_number"): ["1", "1", "0", "1", "0"],
        ("header", "report_duration"): ["11", "HLY", "11", "HLY", "11"],
        ("observations-at", "sensor_id"): ["null", "AT", np.nan, "null", np.nan],
        ("observations-dpt", "sensor_id"): [np.nan, "HUM", np.nan, "null", np.nan],
        ("observations-slp", "sensor_id"): ["null", "SLP", np.nan, "null", np.nan],
        ("observations-sst", "sensor_id"): ["null", "SST", np.nan, np.nan, np.nan],
        ("observations-wd", "sensor_id"): ["null", "WSPD", np.nan, "null", np.nan],
        ("observations-ws", "sensor_id"): ["null", "WSPD", np.nan, "null", np.nan],
        ("observations-at", "sensor_automation_status"): [
            "5",
            "3",
            np.nan,
            "5",
            np.nan,
        ],
        ("observations-dpt", "sensor_automation_status"): [
            np.nan,
            "3",
            np.nan,
            "5",
            np.nan,
        ],
        ("observations-slp", "sensor_automation_status"): [
            "5",
            "3",
            np.nan,
            "5",
            np.nan,
        ],
        ("observations-sst", "sensor_automation_status"): [
            "5",
            "3",
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
        ],
        ("observations-ws", "sensor_automation_status"): [
            "5",
            "3",
            np.nan,
            "5",
            np.nan,
        ],
    },
    "level1e": {
        ("header", "report_quality"): ["0", "0", "1", "0", "1"],
        ("observations-at", "quality_flag"): ["1", "1", np.nan, "0", np.nan],
        ("observations-dpt", "quality_flag"): [np.nan, "0", np.nan, "0", np.nan],
        ("observations-slp", "quality_flag"): ["0", "0", np.nan, "0", np.nan],
        ("observations-sst", "quality_flag"): ["0", "0", np.nan, np.nan, np.nan],
        ("observations-wd", "quality_flag"): ["0", "0", np.nan, "0", np.nan],
        ("observations-ws", "quality_flag"): ["0", "0", np.nan, "0", np.nan],
    },
}

drops = {"level1c": [0, 3]}
