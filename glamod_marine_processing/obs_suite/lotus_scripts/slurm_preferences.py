"""SLURM preferences."""

level_source = {
    "level1a": "level0",
    "level1b": "level1a",
    "level1c": "level1b",
    "level1d": "level1c",
    "level1e": "level1d",
    "level2": "level1e",
    "level3": "level2",
}

source_pattern = {
    "level1a": {
        "ICOADS_R3.0.2T": "IMMA1_R3.0.?T*_????-??",
        "C-RAID_1.2": ["???????.nc", "??????.nc", "?????.nc", "????.nc"],
    },
    "level1b": "header-????-??-*.psv",
    "level1c": "header-????-??-*.psv",
    "level1d": "header-????-??-*.psv",
    "level1e": "header-????-??-*.psv",
    "level2": "header-????-??-*.psv",
    "level3": "header-????-??-*.psv",
}

one_task = ["level2"]

nodesi = {
    "level1d": 1,
    "level2": 1,
}

TaskPNi = {
    "level1d": 20,
}

ti = {"level1d": "02:00:00"}
