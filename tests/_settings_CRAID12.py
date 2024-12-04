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
    "level1b": table_names_next,
    "level1c": table_names_next,
    "level1d": table_names_next,
    "level1e": table_names_next,
    "level2": table_names_next,
}

pattern = {
    "level1a": "craid_????-??-??_subset.nc",
    "level1b": "header-craid_????-??-??_subset.psv",
    "level1c": "header-craid_????-??-??_subset.psv",
    "level1d": "header-craid_????-??-??_subset.psv",
    "level1e": "header-craid_????-??-??_subset.psv",
    "level2": "header-craid_????-??-??_subset.psv",
}

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
        ("header", "report_quality"): ["1", "0", "1", "0", "1", "0", "1", "0", "0", "0"]
    },
}

drops = {
    "level1e": [0, 2, 4, 6],
}
