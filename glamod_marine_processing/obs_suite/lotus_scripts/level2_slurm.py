#!/usr/bin/env python3
"""
Created on Wed Jul 22 09:09:41 2020

@author: iregou
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys

import lotus_paths

# Set process params-----------------------------------------------------------
LEVEL = "level2"
PYSCRIPT = "level2.py"
CONFIG_FILE = "level2.json"
LIST_FILE = "source_deck_list.txt"

JOB_TIME = "00:10:00"
JOB_MEMO = 500
NODES = 1
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
def check_file_exit(files):
    """Check whether file exists."""
    if not isinstance(files, list):
        files = [files]
    for filei in files:
        if not os.path.isfile(filei):
            logging.error(f"File {filei} does not exist. Exiting")
            sys.exit(1)
    return


def check_dir_exit(dirs):
    """Check whether directory exists."""
    dirs = [dirs] if not isinstance(dirs, list) else dirs
    for diri in dirs:
        if not os.path.isdir(diri):
            logging.error(f"Directory {diri} does not exist. Exiting")
            sys.exit(1)
    return


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


# ------------------------------------------------------------------------------


logging.basicConfig(
    format="%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s",
    level=logging.INFO,
    datefmt="%Y%m%d %H:%M:%S",
    filename=None,
)

# Get process coordinates and build paths -------------------------------------
release = sys.argv[1]
update = sys.argv[2]
dataset = sys.argv[3]
# config_path = sys.argv[4]
# process_list_file = sys.argv[5]

# Get lotus paths
lotus_dir = lotus_paths.lotus_scripts_directory
scripts_dir = lotus_paths.scripts_directory
data_dir = lotus_paths.data_directory
scratch_dir = lotus_paths.scratch_directory
config_path = lotus_paths.config_directory

# Build process specific paths
release_tag = "-".join([release, update])
script_config_file = os.path.join(config_path, release_tag, dataset, CONFIG_FILE)
process_list_file = os.path.join(config_path, release_tag, dataset, LIST_FILE)

level_dir = os.path.join(data_dir, release, dataset, LEVEL)
log_dir = os.path.join(level_dir, "log")

# Check paths
check_file_exit([script_config_file, process_list_file])
check_dir_exit([level_dir, log_dir])

# Get configuration -----------------------------------------------------------
with open(process_list_file) as fO:
    process_list = fO.read().splitlines()

# Build jobs ------------------------------------------------------------------
py_path = os.path.join(scripts_dir, PYSCRIPT)
pycommand = "python {} {} {} {} {} {}".format(
    py_path, data_dir, release, update, dataset, script_config_file
)


logging.info("SUBMITTING JOBS...")

job_file = os.path.join(log_dir, "level2.slurm")
task_file = os.path.join(log_dir, "level2.tasks")


with open(task_file, "w") as fn:
    for sid_dck in process_list:
        if os.path.isfile(
            os.path.join(log_dir, f"{sid_dck}-{release}-{update}.failed")
        ):
            print(f"Deleting {job_id}.failure file for a fresh start")
            os.remove(os.path.join(log_dir, f"{sid_dck}-{release}-{update}.failed"))
        fn.writelines(
            "{0} {2} > {1}/{2}.out 2> {1}/{2}.out; if [ $? -eq 0 ]; "
            "then touch {1}/{2}-{3}-{4}.success; else touch {1}/{2}-{3}-{4}.failed; fi \n".format(
                pycommand, log_dir, sid_dck, release, update
            )
        )

with open(job_file, "w") as fh:
    fh.writelines("#!/bin/bash\n")
    fh.writelines("#SBATCH --job-name={}.job\n".format("glamod_level2"))
    fh.writelines(f"#SBATCH --output={log_dir}/%a.out\n")
    fh.writelines(f"#SBATCH --error={log_dir}/%a.err\n")
    fh.writelines(f"#SBATCH --time={JOB_TIME}\n")
    # fh.writelines('#SBATCH --mem={}\n'.format(JOB_MEMO))
    fh.writelines(f"#SBATCH --nodes={NODES}\n")
    fh.writelines("#SBATCH -A glamod\n")
    fh.writelines("#SBATCH --open-mode=truncate\n")
    # fh.writelines('{0} {1}/$SLURM_ARRAY_TASK_ID.input\n'.format(pycommand,log_diri))
    fh.writelines("module load taskfarm\n")
    fh.writelines(f"taskfarm {task_file}\n")


logging.info("{}: launching job".format("level2"))
process = f"jid=$(sbatch {job_file} | cut -f 4 -d' ') && echo $jid"
jid = launch_process(process)
