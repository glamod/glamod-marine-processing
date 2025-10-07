"""
Created on Wed Jul 22 09:09:41 2020

@author: iregou
"""

from __future__ import annotations

import glob
import logging
import os
import re
import subprocess
import sys
from copy import deepcopy

from glamod_marine_processing.obs_suite.lotus_scripts import slurm_preferences
from glamod_marine_processing.utilities import load_json, mkdir, read_txt, save_json


# %%------------------------------------------------------------------------------
def check_file_exist(files):
    """Check whether file exists."""
    files = [files] if not isinstance(files, list) else files
    for filei in files:
        if not os.path.isfile(filei):
            logging.error(f"File {filei} does not exist. Exiting")
            sys.exit(1)


def check_dir_exit(dirs):
    """Check whether directory exists."""
    dirs = [dirs] if not isinstance(dirs, list) else dirs
    for diri in dirs:
        if not os.path.isdir(diri):
            logging.error(f"Directory {diri} does not exist. Exiting")
            sys.exit(1)


def launch_process(process):
    """Launch process."""
    proc = subprocess.Popen(
        [process], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    jid_by, err = proc.communicate()
    if len(err) > 0:
        logging.error("Error launching process. Exiting")
        logging.info(f"Error is: {err}")
        sys.exit(1)
    jid = jid_by.decode("UTF-8").rstrip()

    return jid.split(" ")[-1]


def source_dataset(level, release):
    """Get source dataset."""
    if level == "level1a":
        return "datasets"
    return release


def get_yyyymm(filename):
    """Extract date from filename."""
    DATE_REGEX = r"([1-2]{1}[0-9]{3}\-(0[1-9]{1}|1[0-2]{1}))"
    yyyy_mm = re.search(DATE_REGEX, os.path.basename(filename))
    if not (yyyy_mm):
        logging.warning(f"Could not extract date from filename {filename}")
        return (None, None)
    return yyyy_mm.group().split("-")


def is_in_range(yyyy, mm, year_init, year_end):
    """Check whether date is in time period range."""
    add = False
    if not all((yyyy, mm)):
        add = True
    elif int(yyyy) >= year_init and int(yyyy) <= year_end:
        add = True
    elif (int(yyyy) == year_init - 1 and int(mm) == 12) or (
        int(yyyy) == year_end + 1 and int(mm) == 1
    ):
        add = True
    return add


def get_pattern(yyyy, mm, sid_dck):
    """Get SIDDCK_YEAR-MONTH pattern."""
    date = []
    if yyyy is not None:
        date += [yyyy]
    if mm is not None:
        date += [mm]
    date = "-".join(date)
    if len(date) > 0:
        date = f"_{date}"
    return f"{sid_dck}{date}"


def get_year(periods, sid_dck, yr_str):
    """Get period year."""
    if sid_dck in periods.keys():
        return periods[sid_dck].get(yr_str)
    return periods.get(yr_str)


# %%------------------------------------------------------------------------------


logging.basicConfig(
    format="%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s",
    level=logging.INFO,
    datefmt="%Y%m%d %H:%M:%S",
    filename=None,
)

# Get process coordinates and build paths -------------------------------------
script_config_file = sys.argv[1]
check_file_exist([script_config_file])
script_config = load_json(script_config_file)

release = script_config["abbreviations"]["release"]
update = script_config["abbreviations"]["update"]
dataset = script_config["abbreviations"]["dataset"]
config_files_path = script_config["paths"]["config_files_path"]
release_periods_file = script_config["release_periods_file"]
release_periods_file = os.path.join(config_files_path, release_periods_file)

release_source = script_config["release_source"]
release_dest = script_config["release_destination"]

dataset_source = script_config["dataset_source"]
dataset_dest = script_config["dataset_destination"]

level = script_config["level"]
level_source = script_config["level_source"]
level_dest = script_config["level_destination"]
if not level_source:
    level_source = slurm_preferences.level_source[level]

if "source_pattern" in script_config.keys():
    source_pattern = script_config["source_pattern"]
else:
    source_pattern = slurm_preferences.source_pattern[level]

if isinstance(source_pattern, dict):
    source_pattern = source_pattern[dataset]

if not isinstance(source_pattern, list):
    source_pattern = [source_pattern]

PYSCRIPT = f"{level}.py"
MACHINE = script_config["scripts"]["machine"].lower()
overwrite = script_config["overwrite"]

# Get lotus paths
lotus_dir = script_config["paths"]["lotus_scripts_directory"]
scripts_dir = script_config["paths"]["scripts_directory"]
data_dir = script_config["paths"]["data_directory"]
scratch_dir = script_config["paths"]["scratch_directory"]

# Build process specific paths
level_dir = os.path.join(data_dir, release_dest, dataset_dest, level_dest)
release_source = source_dataset(level, release_source)
level_source_dir = os.path.join(data_dir, release_source, dataset_source, level_source)
log_dir = os.path.join(level_dir, "log")
script_config["paths"]["destination_directory"] = level_dir
script_config["paths"]["source_directory"] = level_source_dir

# Get further configuration -----------------------------------------------------------
if script_config["process_list"]:
    process_list = script_config["process_list"]
else:
    process_list_file = script_config["process_list_file"]
    process_list_file = os.path.join(config_files_path, process_list_file)
    check_file_exist([process_list_file])
    process_list = read_txt(process_list_file)

logging.info(f"Periods file used: {release_periods_file}")
logging.info(f"Process deck list: {process_list}")
check_file_exist([release_periods_file])
release_periods = load_json(release_periods_file)

if script_config["year_init"]:
    release_periods["year_init"] = script_config["year_init"]
if script_config["year_end"]:
    release_periods["year_end"] = script_config["year_end"]

# Optionally, add CMD add file
add_file = os.path.join(config_files_path, f"{level}_cmd_add.json")
if os.path.isfile(add_file):
    script_config["cmd_add_file"] = add_file

# Build jobs ------------------------------------------------------------------
py_path = os.path.join(scripts_dir, PYSCRIPT)
pycommand = f"python {py_path}"

# Set default job params
mem = script_config["job_memo_mb"]
t_hh = script_config["job_time_hr"]
t_mm = script_config["job_time_min"]
t = ":".join([t_hh, t_mm, "00"])

logging.info("SUBMITTING ARRAYS...")
if script_config["parallel_jobs"] is True:
    taskfarm_files = os.path.join(log_dir, "taskfarm.tasks")
    with open(taskfarm_files, "w") as f:
        pass

for sid_dck in process_list:

    logging.info(f"Creating scripts for {sid_dck}")
    log_diri = os.path.join(log_dir, sid_dck)

    sid_dck_log_dir = os.path.join(log_dir, sid_dck)
    mkdir(sid_dck_log_dir)
    file_ = os.path.join(sid_dck_log_dir, sid_dck)
    if script_config["parallel_jobs"] is True:
        taskfarm_file = taskfarm_files
        mode = "a"
    else:
        taskfarm_file = f"{file_}.tasks"
        mode = "w"

    # check is separate configuration for this source / deck
    config = deepcopy(script_config)
    config_sid_dck = config.get(sid_dck)
    if config_sid_dck is not None:
        for k, v in config_sid_dck.items():
            config[k] = v

    year_init = int(get_year(release_periods, sid_dck, "year_init"))
    year_end = int(get_year(release_periods, sid_dck, "year_end"))
    source_files = []
    for pattern in source_pattern:
        sfiles = glob.glob(os.path.join(level_source_dir, sid_dck, pattern))
        if len(sfiles) == 0:
            continue
        if level in slurm_preferences.one_task:
            source_files = [sfiles[0]]
            break
        source_files.extend(sfiles)

    array_size = len(source_files)
    if array_size == 0:
        logging.info("No tasks to be calculated")
        continue

    if level in slurm_preferences.TaskPNi.keys():
        TaskPNi = slurm_preferences.TaskPNi[level]
    else:
        memi = script_config.get(sid_dck, {}).get("job_memo_mb")
        memi = mem if not memi else memi
        TaskPNi = min(int(190000.0 / float(memi)), 40)

    if level in slurm_preferences.nodesi.keys():
        nodesi = slurm_preferences.nodesi[level]
    else:
        nodesi = array_size // TaskPNi + (array_size % TaskPNi > 0)

    if level in slurm_preferences.ti.keys():
        ti = slurm_preferences.ti[level]
    else:
        t_hhi = script_config.get(sid_dck, {}).get("job_time_hr")
        t_mmi = script_config.get(sid_dck, {}).get("job_time_min")
        if t_hhi and t_mmi:
            ti = ":".join([t_hhi, t_mmi, "00"])
        else:
            ti = t

    with open(taskfarm_file, mode) as fh:
        for source_file in source_files:
            yyyy, mm = get_yyyymm(source_file)
            add = is_in_range(yyyy, mm, year_init, year_end)

            if add is False:
                logging.warning(f"{yyyy} out of range: {year_init} to {year_end}.")
                continue

            pattern = get_pattern(yyyy, mm, sid_dck)

            config_file_ = os.path.join(sid_dck_log_dir, f"{pattern}.input")
            success_file_ = os.path.join(sid_dck_log_dir, f"{pattern}.success")
            failed_file_ = os.path.join(sid_dck_log_dir, f"{pattern}.failure")

            if overwrite is not True and os.path.isfile(success_file_):
                logging.info(
                    f"Task {pattern} was already successful. Skip calculating again."
                )
                continue

            """Update configuration script."""
            script_config.update({"sid_dck": sid_dck})
            script_config.update({"yyyy": yyyy})
            script_config.update({"mm": mm})
            script_config.update({"filename": source_file})

            if os.path.isfile(failed_file_):
                logging.info(f"Task {pattern} failed. Try calculating again.")
                os.remove(failed_file_)

            if os.path.isfile(success_file_):
                logging.info(
                    f"Task {pattern} was already successful. However, calculate task again since option 'overwrite' was chosen."
                )
                os.remove(success_file_)

            fh.writelines(
                "{0} {1}/{2}.input > {1}/{2}.out 2> {1}/{2}.out; if [ $? -eq 0 ]; "
                "then touch {1}/{2}.success; else touch {1}/{2}.failure; fi  \n".format(
                    pycommand, log_diri, pattern
                )
            )
            save_json(script_config, config_file_)

    logging.info(f"{sid_dck}: launching array")
    logging.info(f"Script {taskfarm_file} was created.")
    if script_config["submit_jobs"] is True:
        job_file = f"{file_}.slurm"
        header = read_txt(
            os.path.join(lotus_dir, "header", f"slurm_header_{MACHINE}.txt")
        )
        with open(job_file, "w") as fh:
            for line in header:
                line = eval(line)  # noqa: S307
                line = f"{line}\n"
                fh.writelines(line)
        process = f"jid=$(sbatch {job_file} | cut -f 4 -d' ') && echo $jid"
        logging.info(f"process launching: {process}")
        jid = launch_process(process)
        continue

    subprocess.call(["/bin/chmod", "u+x", taskfarm_file], shell=False)
    if script_config["parallel_tasks"] is True:
        logging.info("Run tasks per job interactively in parallel.")
        cmd = [
            "/bin/parallel",
            "--jobs",
            script_config["n_max_jobs"],
            "::::",
            taskfarm_file,
        ]
        if script_config["nohup"] is True:
            nohup_out = os.path.join(sid_dck_log_dir, f"nohup_{pattern}.out")
            nohup_err = os.path.join(sid_dck_log_dir, f"nohup_{pattern}.err")
            nohup_pid = os.path.join(sid_dck_log_dir, f"nohup_{pattern}.pid")
            cdm = ["nohup"] + cmd
            with open(nohup_out, "w") as out, open(nohup_err, "w") as err:
                proc = subprocess.Popen(
                    cmd,
                    stdout=out,
                    stderr=err,
                    preexec_fn=os.setpgrp,
                )

            with open(nohup_pid, "w") as pidf:
                pidf.write(str(proc.pid))

        continue

    if script_config["run_jobs"] is True:
        logging.info("Run jobs interactively.")
        subprocess.call(["/bin/sh", taskfarm_file], shell=False)
        logging.info(f"Check whether jobs was successful: {log_diri}")

if script_config["parallel_jobs"] is True:
    subprocess.call(["/bin/chmod", "u+x", taskfarm_files], shell=False)
    logging.info("Run jobs interactively in parallel.")
    cmd = [
        "/bin/parallel",
        "--jobs",
        script_config["n_max_jobs"],
        "::::",
        taskfarm_files,
    ]
    if script_config["nohup"] is True:
        nohup_out = os.path.join(sid_dck_log_dir, f"nohup_{pattern}.out")
        nohup_err = os.path.join(sid_dck_log_dir, f"nohup_{pattern}.err")
        nohup_pid = os.path.join(sid_dck_log_dir, f"nohup_{pattern}.pid")
        cdm = ["nohup"] + cmd
        with open(nohup_out, "w") as out, open(nohup_err, "w") as err:
            proc = subprocess.Popen(
                cmd,
                stdout=out,
                stderr=err,
                preexec_fn=os.setpgrp,
            )
        with open(nohup_pid, "w") as pidf:
            pidf.write(str(proc.pid))
