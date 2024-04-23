#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 09:09:41 2020

@author: iregou
"""

import sys
import os
import json
import argparse
import logging
import glob
import subprocess

import lotus_paths
import config_array


#%% Set process params-----------------------------------------------------------
LEVEL = 'level1a'
LEVEL_SOURCE = 'level0'
SOURCE_PATTERN = 'IMMA1_R3.0.?T*_????-??' # '????-??.imma'
PYSCRIPT = 'level1a.py'
USER = 'glamod'
#NODES = 1
#this scripts determines how many nodes it is requesting based on the size of the job, can be set to fixed value in line 157
#------------------------------------------------------------------------------

#%%------------------------------------------------------------------------------
def check_file_exit(files):
    files = [files] if not isinstance(files,list) else files
    for filei in files:
        if not os.path.isfile(filei):
            logging.error('File {} does not exist. Exiting'.format(filei))
            sys.exit(1)
    return

def check_dir_exit(dirs):
    dirs = [dirs] if not isinstance(dirs,list) else dirs
    for diri in dirs:
        if not os.path.isdir(diri):
            logging.error('Directory {} does not exist. Exiting'.format(diri))
            sys.exit(1)
    return

def launch_process(process):
    proc = subprocess.Popen([process],shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    jid_by, err = proc.communicate()
    if len(err)>0:
        logging.error('Error launching process. Exiting')
        logging.info('Error is: {}'.format(err))
        sys.exit(1)
    jid = jid_by.decode('UTF-8').rstrip()

    return jid.split(' ')[-1]

#%%------------------------------------------------------------------------------


logging.basicConfig(format='%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s',
                    level=logging.INFO,datefmt='%Y%m%d %H:%M:%S',filename=None)

# Get process coordinates and build paths -------------------------------------
script_config_file = sys.argv[1]

check_file_exit([script_config_file])
print(script_config_file)
with open(script_config_file,'r') as fO:
    script_config = json.load(fO)

release = script_config['release']
update = script_config['update']
dataset = script_config['dataset']
process_list_file = script_config['process_list_file']
release_periods_file = script_config['release_periods_file']

parser = argparse.ArgumentParser()
parser.add_argument('positional', metavar='N', type=str, nargs='+')
parser.add_argument('--failed_only')

args = parser.parse_args()
if args.failed_only:
    failed_only = True if args.failed_only== 'yes' else False
    logging.warning('failed_only is currently deactivated, all data will be processed')
    #this is because of changes to the failed/success indicator used. config_array.main expects the 
    #log files to be renamed to name.ok in case of success, instead of .success file created
    failed_only = False
else:
    failed_only = False

# Get lotus paths
lotus_dir = lotus_paths.lotus_scripts_directory
scripts_dir = lotus_paths.scripts_directory
data_dir = lotus_paths.data_directory
scratch_dir = lotus_paths.scratch_directory

# Build process specific paths
release_tag = '-'.join([release,update])
print(release_periods_file)
level_dir = os.path.join(data_dir,release,dataset,LEVEL)
print(level_dir)
level_source_dir = os.path.join(data_dir,'datasets',dataset,LEVEL_SOURCE)
log_dir = os.path.join(level_dir, 'log')

# Check paths
check_file_exit([release_periods_file,process_list_file])
check_dir_exit([level_dir,level_source_dir,log_dir])

# Get further configuration -----------------------------------------------------------
with open(process_list_file,'r') as fO:
    process_list = fO.read().splitlines()

with open(release_periods_file,'r') as fO:
    release_periods = json.load(fO)

# Build array input files -----------------------------------------------------
logging.info('CONFIGURING JOB ARRAYS...')

status = config_array.main(level_source_dir, SOURCE_PATTERN, log_dir,
                           script_config, release_periods, process_list,
                           failed_only = failed_only)
if status != 0:
    logging.error('Creating array inputs')
    sys.exit(1)

print(status)

# Build jobs ------------------------------------------------------------------
py_path = os.path.join(scripts_dir,PYSCRIPT)
#py_clean_path = os.path.join(lotus_dir,PYCLEAN)
pycommand='python3 {0} {1} {2} {3} {4}'.format(py_path, data_dir, release,
                                                update, dataset)

# Set default job params
mem = script_config['job_memo_mb']
t_hh = script_config['job_time_hr']
t_mm = script_config['job_time_min']
t = ':'.join([t_hh, t_mm, '00'])

logging.info('SUBMITTING ARRAYS...')

for sid_dck in process_list:
    log_diri = os.path.join(log_dir, sid_dck)
    array_size = len(glob.glob(os.path.join(log_diri, '*.input')))
    if array_size == 0:
        logging.warning('{}: no jobs for partition'.format(sid_dck))
        continue

    job_file = os.path.join(log_diri, sid_dck + '.slurm')
    taskfarm_file = os.path.join(log_diri, sid_dck + '.tasks')
    memi = script_config.get(sid_dck,{}).get('job_memo_mb')
    memi = mem if not memi else memi
    TaskPNi = min(int(190000./float(memi)), 40)
    nodesi = array_size // TaskPNi + (array_size % TaskPNi > 0)
    #nodesi = 1
    t_hhi = script_config.get(sid_dck,{}).get('job_time_hr')
    t_mmi = script_config.get(sid_dck,{}).get('job_time_min')
    if t_hhi and t_mmi:
        ti = ':'.join([t_hhi,t_mmi,'00'])
    else:
        ti = t
    with open(taskfarm_file, 'w') as fh:
        for i in range(array_size):
            if os.path.isfile('{0}/{1}.failure'.format(log_diri, i+1)):
                os.remove('{0}/{1}.failure'.format(log_diri, i+1))
            fh.writelines('{0} {1}/{2}.input > {1}/{2}.out 2> {1}/{2}.out; if [ $? -eq 0 ]; then touch {1}/{2}.success; else touch {1}/{2}.failure; fi  \n'.format(pycommand, log_diri, i+1))

    with open(job_file,'w') as fh:
        fh.writelines('#!/bin/bash\n')
        fh.writelines('#SBATCH --job-name={}.job\n'.format(sid_dck))
        fh.writelines('#SBATCH --output={}/%a.out\n'.format(log_diri))
        fh.writelines('#SBATCH --error={}/%a.err\n'.format(log_diri))
        fh.writelines('#SBATCH --time={}\n'.format(ti))
        fh.writelines('#SBATCH --nodes={}\n'.format(nodesi))#request more nodes (or time) if array_size>num of jobs we can run at a time
        fh.writelines('#SBATCH --open-mode=truncate\n')
        fh.writelines('#SBATCH -A {}\n'.format(USER))
        fh.writelines('module load taskfarm\n')
        fh.writelines('export TASKFARM_PPN={}\n'.format(TaskPNi))
        fh.writelines('taskfarm {}\n'.format(taskfarm_file))

    logging.info('{}: launching array'.format(sid_dck))
    process = "jid=$(sbatch {} | cut -f 4 -d' ') && echo $jid".format(job_file)
    logging.info('process launching: {}'.format(process))
    jid = launch_process(process)
