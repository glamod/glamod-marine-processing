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


# Set process params-----------------------------------------------------------
LEVEL = 'level1d'
LEVEL_SOURCE = 'level1c'
SOURCE_PATTERN = 'header-????-??-*.psv'
PYSCRIPT = 'level1d.py'
USER = 'glamod'

NODES = 1
TaskPN = 20
ti = '02:00:00'
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
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

#------------------------------------------------------------------------------


logging.basicConfig(format='%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s',
                    level=logging.INFO,datefmt='%Y%m%d %H:%M:%S',filename=None)

# Get process coordinates and build paths -------------------------------------
script_config_file = sys.argv[1]

check_file_exit([script_config_file])
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
parser.add_argument('--remove_source')

args = parser.parse_args()
if args.failed_only:
    logging.warning('failed_only is currently deactivated, all data will be processed')
    #failed_only = True if args.failed_only== 'yes' else False
    failed_only = False
else:
    failed_only = False

if args.remove_source:
    logging.warning('remove_source has been discontinued, source data will not be removed')
    #remove_source = True if args.remove_source== 'yes' else False
    remove_source = False
else:
    remove_source = False

# Get lotus paths
lotus_dir = lotus_paths.lotus_scripts_directory
scripts_dir = lotus_paths.scripts_directory
data_dir = lotus_paths.data_directory
scratch_dir = lotus_paths.scratch_directory

# Build process specific paths
release_tag = '-'.join([release,update])
level_dir = os.path.join(data_dir,release,dataset,LEVEL)
level_source_dir = os.path.join(data_dir,release,dataset,LEVEL_SOURCE)
log_dir = os.path.join(level_dir,'log')

# Check paths
check_file_exit([release_periods_file,process_list_file])
check_dir_exit([level_dir,level_source_dir,log_dir])

# Get configuration -----------------------------------------------------------
with open(process_list_file,'r') as fO:
    process_list = fO.read().splitlines()

with open(release_periods_file,'r') as fO:
    release_periods = json.load(fO)
    
# Build array input files -----------------------------------------------------
logging.info('CONFIGURING JOBs...')

status = config_array.main(level_source_dir,SOURCE_PATTERN,log_dir,
                           script_config,release_periods,process_list,
                           failed_only = failed_only) 
if status != 0:
    logging.error('Creating array inputs')
    sys.exit(1)

# Build jobs ------------------------------------------------------------------    
py_path = os.path.join(scripts_dir,PYSCRIPT)
pycommand='python {0} {1} {2} {3} {4}'.format(py_path,data_dir,release,update,
                  dataset)

# Set default job params
mem = script_config['job_memo_mb']
t_hh = script_config['job_time_hr']
t_mm = script_config['job_time_min']
t = ':'.join([t_hh,t_mm,'00'])

logging.info('SUBMITTING ARRAYS...')

job_file = os.path.join(log_dir,'sid_combined.slurm')
taskfarm_file = os.path.join(log_dir,'sid_combined.tasks')

if os.path.exists(taskfarm_file):#its appanded in the following: start empty
    logging.info('Removing previous tasks file')
    os.remove(taskfarm_file)

if 1:
    for sid_dck in process_list:
        log_diri = os.path.join(log_dir,sid_dck)
        array_size = len(glob.glob(os.path.join(log_diri,'*.input')))
        if array_size == 0:
            logging.warning('{}: no jobs for partition'.format(sid_dck))
            continue
    
        #job_file = os.path.join(log_diri,sid_dck + '.slurm')
        #taskfarm_file = os.path.join(log_diri, sid_dck + '.tasks')

        #memi = script_config.get(sid_dck,{}).get('job_memo_mb')
        #memi = mem if not memi else memi
        #TaskPNi = min(int(190000./float(memi)), TaskPN)
        #nodesi = array_size // TaskPNi + (array_size % TaskPNi > 0)
        
        #t_hhi = script_config.get(sid_dck,{}).get('job_time_hr')
        #t_mmi = script_config.get(sid_dck,{}).get('job_time_min')
        #if t_hhi and t_mmi:
        #    ti = ':'.join([t_hhi,t_mmi,'00'])
        #else:
        #    ti = t
    
        with open(taskfarm_file, 'a') as fh:
            for i in range(array_size):
                if os.path.isfile('{0}/{1}.failure'.format(log_diri, i+1)):
                    os.remove('{0}/{1}.failure'.format(log_diri, i+1))
                fh.writelines('{0} {1}/{2}.input > {1}/{2}.out 2> {1}/{2}.out; if [ $? -eq 0 ]; then touch {1}/{2}.success; else touch {1}/{2}.failure; fi \n'.format(pycommand, log_diri, i+1))

with open(job_file,'w') as fh:
    fh.writelines('#!/bin/bash\n')
    fh.writelines('#SBATCH --job-name={}.job\n'.format(LEVEL))
    fh.writelines('#SBATCH --nodes={}\n'.format(NODES))
    fh.writelines('#SBATCH -A {}\n'.format(USER))
    fh.writelines('#SBATCH --output={}/%j.out\n'.format(log_dir))
    fh.writelines('#SBATCH --error={}/%j.err\n'.format(log_dir))
    fh.writelines('#SBATCH --time={}\n'.format(ti))
    fh.writelines('#SBATCH --open-mode=truncate\n')
    fh.writelines('module load taskfarm\n')
    fh.writelines('export TASKFARM_PPN={}\n'.format(TaskPN))
    fh.writelines('taskfarm {}\n'.format(taskfarm_file))

logging.info('{}: launching'.format(job_file)) 
process = "jid=$(sbatch {} | cut -f 4 -d' ') && echo $jid".format(job_file)
jid = launch_process(process)
