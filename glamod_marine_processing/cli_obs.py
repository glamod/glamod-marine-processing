"""
===========================================
Observational Command Line Interface module
===========================================
"""

from __future__ import annotations

import datetime
import os
import shutil
from types import SimpleNamespace

import click

from .cli import CONTEXT_SETTINGS, Cli, add_options
from .utilities import add_to_config, load_json, save_json


@click.command(context_settings=CONTEXT_SETTINGS)
@add_options()
def obs_cli(
    machine,
    level,
    level_source,
    level_destination,
    release,
    release_source,
    release_destination,
    update,
    dataset,
    dataset_source,
    dataset_destination,
    cdm_tables,
    process_list,
    year_init,
    year_end,
    source_pattern,
    prev_file_id,
    data_directory,
    work_directory,
    noc_version,
    noc_path,
    pub47_path,
    config_file,
    submit_jobs,
    run_jobs,
    parallel_jobs,
    parallel_tasks,
    nohup,
    n_max_jobs,
    overwrite,
):
    """Entry point for the obs_suite command line interface."""
    config = Cli(
        machine=machine,
        level=level,
        level_source=level_source,
        level_destination=level_destination,
        release=release,
        release_source=release_source,
        release_destination=release_destination,
        update=update,
        dataset=dataset,
        dataset_source=dataset_source,
        dataset_destination=dataset_destination,
        cdm_tables=cdm_tables,
        data_directory=data_directory,
        work_directory=work_directory,
        config_file=config_file,
        suite="obs_suite",
        deck_list=process_list,
        overwrite=overwrite,
    ).initialize()

    p = SimpleNamespace(**config["paths"])
    slurm_script = "level_slurm.py"
    slurm_script_ = f"{level}_slurm.py"
    slurm_script_tmp = os.path.join(p.lotus_scripts_directory, slurm_script)
    slurm_script_new = os.path.join(p.release_directory, slurm_script_)
    shutil.copyfile(slurm_script_tmp, slurm_script_new)

    level_config_file = f"{level}.json"
    level_config_file = os.path.join(p.config_files_path, level_config_file)

    config = add_to_config(
        config,
        slurm_script=slurm_script_new,
        level_config_file=level_config_file,
        machine=machine,
        key="scripts",
    )

    config = add_to_config(
        config,
        noc_version=noc_version,
        noc_path=noc_path,
        pub47_path=pub47_path,
        key="corrections_mod",
    )

    level_config = load_json(level_config_file)
    level_config["submit_jobs"] = submit_jobs
    level_config["run_jobs"] = run_jobs
    level_config["parallel_jobs"] = parallel_jobs
    level_config["parallel_tasks"] = parallel_tasks
    level_config["n_max_jobs"] = n_max_jobs
    level_config["nohup"] = nohup
    level_config["level"] = level
    level_config["overwrite"] = overwrite
    if isinstance(process_list, str):
        process_list = [process_list]
    level_config["process_list"] = process_list
    level_config["year_init"] = year_init
    level_config["year_end"] = year_end
    if source_pattern:
        level_config["source_pattern"] = source_pattern
    if prev_file_id:
        if prev_file_id[0] != "*":
            prev_file_id = f"*{prev_file_id}"
        if prev_file_id[-1] != "*":
            prev_file_id = f"{prev_file_id}*"
        level_config["prev_fileID"] = prev_file_id

    for key, value in config.items():
        level_config[key] = value

    current_time = datetime.datetime.now()
    current_time = current_time.strftime("%Y%m%dT%H%M%S")

    new_config = f"{level}_{current_time}.json"
    new_config = os.path.join(p.release_directory, new_config)
    save_json(level_config, new_config)
    os.system(f"python {slurm_script_new} {new_config}")
