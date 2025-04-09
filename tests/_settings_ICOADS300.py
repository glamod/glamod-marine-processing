from __future__ import annotations

data_model = "icoads"
release = "r300"
deck = "d706"
input_dir = f"{data_model}/{release}/{deck}"
cdm = f"icoads_{release}_{deck}_1919-03-01_subset"
suffix = "imma"
level0 = f"{input_dir}/input/{cdm}.{suffix}"

process_list = "084-706"
year_init = "1919"
year_end = "1920"

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
}

level_input = {
    "level1a": "datasets",
    "level1b": "release_8.0",
    "level1c": "release_8.0",
    "level1d": "release_8.0",
    "level1e": "release_8.0",
    "level2": "release_8.0",
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
    "level1a": "icoads_r???_d???_????-??-??_subset.imma",
    "level1b": "header-icoads_r???_d???_????-??-??_subset.psv",
    "level1c": "header-icoads_r???_d???_????-??-??_subset.psv",
    "level1d": "header-icoads_r???_d???_????-??-??_subset.psv",
    "level1e": "header-icoads_r???_d???_????-??-??_subset.psv",
    "level2": "header-icoads_r???_d???_????-??-??_subset.psv",
}
