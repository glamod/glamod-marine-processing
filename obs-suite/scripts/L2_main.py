#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 14:24:10 2019

Script to generate the C3S CDM Marine level2 data: final release data after visual
inspection of data.

The processing unit is the source-deck.

Outputs data to /<data_path>/<release>/<source>/level2/<sid-dck>/table[i]-fileID.psv
Outputs data to /<data_path>/<release>/<source>/level2/excluded/<sid-dck>/table[i]-fileID.psv

where fileID is yyyy-mm-release_tag-update_tag

Before processing starts:
    - checks the existence of all io subdirectories in level1e|2 -> exits if fails
    - checks the existence of the level2 selection file (level2_list) and that
    sid-dck is registered within -> exits if fails
    - checks that a sid-dck to be included has at least an observation table
    registered to be included  -> exits if fails
    - removes level2 products on input file resulting from previous runs
    
If at any point during copying an exception is raised, cleans all sid-dck level2
before exiting.

Inargs:
------
data_path: data release parent path (i.e./gws/nopw/c3s311_lot2/data/marine)
sid_dck: source-deck partition (sss-ddd)
release: release identifier
update: release update identifier
source: source dataset identifier

Uses level2_list:
----------------
json file as created by L2_list_create.py, with:

{
    'params_exclude':[],
    'ss1-dd1':{'exclude':True|False,'params_exclude':[]},
    ....
    'ssN-ddN':{'exclude':True|False,'params_exclude':[]}
}


!!!!:
----
If not all the observation tables from a sid-dck are included in level2 from level1e,
then the header table needs to be check as some reports may stay orphan and
should not progress to level2.

Once the above is implemented, for consistency, in the excluded directory a header table
should reflect all the reports from all the excluded observation tables....

Me explico?
.....

@author: iregon
"""
import sys
import os
import json
import datetime
import cdm
import glob
import logging
from subprocess import call
from imp import reload
reload(logging)  # This is to override potential previous config of logging

# FUNCTIONS -------------------------------------------------------------------
class script_setup:
    def __init__(self, inargs):
        self.data_path = inargs[1]
        self.sid_dck = inargs[2]
        self.dck = self.sid_dck.split("-")[1]
        self.release = inargs[3]
        self.update = inargs[4]
        self.source = inargs[5]

# This is for json to handle dates
date_handler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, (datetime.datetime, datetime.date))
    else None
)

def clean_level():
    level_prods = glob.glob(os.path.join(level_path,'*.psv'))
    level_reports = glob.glob(os.path.join(level_reports_path, '*.json'))
    level_excluded = glob.glob(os.path.join(level_excluded_path,'*.psv'))
    for filename in level_prods + level_reports + level_excluded:
        try:
            logging.info('Removing previous file: {}'.format(filename))
            os.remove(filename)
        except:
            pass

# MAIN ------------------------------------------------------------------------

# Process input and set up some things and make sure we can do something-------
logging.basicConfig(format='%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s',
                    level=logging.INFO,datefmt='%Y%m%d %H:%M:%S',filename=None)
if len(sys.argv)>1:
    logging.info('Reading command line arguments')
    args = sys.argv
else:
    logging.error('Need arguments to run!')
    sys.exit(1)

params = script_setup(args)
    
filename_field_sep = '-' 
level = 'level2'
level_prev = 'level1e'
header = True 
wmode = 'w'
    
release_path = os.path.join(params.data_path,params.release,params.source)
release_id = filename_field_sep.join([params.release,params.update ]) 

prev_level_path = os.path.join(release_path,level_prev,params.sid_dck)  
level_path = os.path.join(release_path,level,params.sid_dck)
level_excluded_path = os.path.join(release_path,level,'excluded',params.sid_dck)
level_reports_path = os.path.join(release_path,level,'reports',params.sid_dck)

data_paths = [prev_level_path, level_path, level_excluded_path]
if any([ not os.path.isdir(x) for x in data_paths ]):
    logging.error('Could not find data paths: {}'.format(','.join([ x for x in data_paths if not os.path.isdir(x)])))
    sys.exit(1)

level2_list = os.path.join(release_path,'level2',filename_field_sep.join([params.release,params.update,'selection.json']))

if not os.path.isfile(level2_list):
    logging.error('Level2 selection file {} not found'.format(level2_list))
    sys.exit(1)

 
# Clean previous L2 products and side files -----------------------------------
clean_level()

# DO THE DATA SELECTION -------------------------------------------------------
# -----------------------------------------------------------------------------
cdm_tables = cdm.lib.tables.tables_hdlr.load_tables()
obs_tables = [ x for x in cdm_tables if x != 'header' ]
with open(level2_list,'r') as fileObj:
    include_list = json.load(fileObj)

if not include_list.get(params.sid_dck):
    logging.error('sid-dck {0} not registered in level2 list {1}'.format(params.sid_dck,level2_list))
    sys.exit(1)     
       
exclude_sid_dck = include_list.get(params.sid_dck,{}).get('exclude')  
  
exclude_param_global_list = include_list.get('params_exclude')
exclude_param_sid_dck_list = include_list.get(params.sid_dck,{}).get('params_exclude')
   
exclude_param_list = list(set(exclude_param_global_list + exclude_param_sid_dck_list))
include_param_list = [ x for x in obs_tables if x not in exclude_param_list ]

# Check that inclusion list makes sense
if not exclude_sid_dck and len(include_param_list) == 0:
    logging.error('sid-dck {} is to be included, but include parameter list is empty'.format(params.sid_dck))
    sys.exit(1)    

try:  
    include_param_list.append('header')
    if exclude_sid_dck:
        logging.info('Full dataset {} excluded from level2'.format(params.sid_dck))
        for table in cdm_tables:
            files = os.path.join(prev_level_path,table + '*.psv')
            call(' '.join(['cp',files,level_excluded_path]),shell=True)
    else:
        for table in exclude_param_list:
            logging.info('{} excluded from level2'.format(table))
            files = os.path.join(prev_level_path,table + '*.psv')
            call(' '.join(['cp',files,level_excluded_path]),shell=True)
        for table in include_param_list:
            logging.info('{} included in level2'.format(table))
            files = os.path.join(prev_level_path,table + '*.psv')
            call(' '.join(['cp',files,level_path]),shell=True)
    logging.info('Level2 data succesfully created')
except Exception:
    logging.error('Error creating level2 data',exc_info = True)
    logging.info('Level2 data {} removed'.format(params.sid_dck))
    clean_level()
    sys.exit(1)

