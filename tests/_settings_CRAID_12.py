from __future__ import annotations

data_model = "craid"
deck = "1260810"
input_dir = data_model
cdm = f"{data_model}_2004-12-20_subset"
suffix = "nc"
level0 = f"{data_model}/input/{cdm}.{suffix}"
process_list = "1260810"
year_init = "2000"
year_end = "2010"
release = "release_8.0"

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
    "observations-slp",
    "observations-sst",
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
    "level3": "observations-slp",
}

pattern = {
    "level1a": "craid_????-??-??_subset.nc",
    "level1b": "header-craid_????-??-??_subset.psv",
    "level1c": "header-craid_????-??-??_subset.psv",
    "level1d": "header-craid_????-??-??_subset.psv",
    "level1e": "header-craid_????-??-??_subset.psv",
    "level2": "header-craid_????-??-??_subset.psv",
    "level3": "header-craid_????-??-??_subset.psv",
}

pattern_out = {"level3": "insitu-surface-marine_2004-12.psv"}

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
            "0",
            "0",
        ]
    },
    "level1e": {
        ("header", "report_quality"): [
            "1",
            "0",
            "1",
            "0",
            "1",
            "0",
            "1",
            "0",
            "0",
            "0",
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
        ("observations-slp", "observation_height_above_station_surface"),
        ("observations-slp", "z_coordinate"),
        ("header", "report_timestamp"),
        ("header", "report_meaning_of_timestamp"),
        ("header", "report_duration"),
        ("observations-slp", "observed_variable"),
        ("observations-slp", "units"),
        ("observations-slp", "observation_value"),
        ("observations-slp", "quality_flag"),
        ("header", "source_id"),
        ("observations-slp", "data_policy_licence"),
        ("header", "platform_type"),
        ("header", "report_type"),
        ("observations-slp", "value_significance"),
    ],
}

drops = {
    "level1b": [0, 2, 4, 6],
    "level1e": [0, 2, 4, 6],
    "level3": [0, 2, 4, 6],
}

reindex = ["level1b"]
