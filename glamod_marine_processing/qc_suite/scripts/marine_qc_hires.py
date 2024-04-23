#!/usr/local/sci/bin/python2.7
"""
marine_qc_hires.py invoked by typing::

  python2.7 marine_qc_hires.py -config configuration.txt -year1 1850 -year2 1855 -month1 1 -month2 12

This quality controls the data for the chosen years using the high 
resolution SST climatology. The location of the data base, the locations 
of the climatology files are to be specified in the configuration files.

"""

import gzip
import qc
from IMMA1 import IMMA
import Extended_IMMA_sb as ex
import Climatology as clim
import BackgroundField as bf
import argparse
import configparser as ConfigParser
import json
import sys
from noc_auxiliary import *
from datetime import datetime
import pandas as pd
from pathlib import Path
import logging


def main(argv):
    """
    This program reads in data from ICOADS.2.5.1 and applies quality control processes to it, flagging data as 
    good or bad according to a set of different criteria.

    The first step of the process is to read in various SST and MAT climatologies from file. These are 1degree latitude 
    by 1 degree longitude by 73 pentad fields in NetCDF format.
    
    The program then loops over all specified years and months reads in the data needed to QC that month and then 
    does the QC. There are three stages in the QC
    
    basic QC - this proceeds one observation at a time. Checks are relatively simple and detect gross errors
    
    track check - this works on Voyages consisting of all the observations from a single ship (or at least a single ID) 
    and identifies observations which make for an implausible ship track
    
    buddy check - this works on Decks which are large collections of observations and compares observations to their
    neighbours
    """

    logging.info('########################')
    logging.info('Running make_and_full_qc')
    logging.info('########################')

    parser = argparse.ArgumentParser(description='Marine QC system, main program')
    parser.add_argument('-config', type=str, default='configuration.txt', help='name of config file')
    parser.add_argument('-tracking', action='store_true', help='perform tracking QC')
    parser.add_argument('-jobs', type=str, default='jobs.json', help='name of job file')
    parser.add_argument('-job_index', type=int, default=0, help='job index')
    
    args = parser.parse_args()


    inputfile = args.config
    jobfile   = args.jobs
    jobindex  = args.job_index - 1
    tracking = args.tracking    
    
    with open( jobfile ) as fp:
        jobs = json.load( fp )    
    
    year1 = jobs['jobs'][jobindex]['year1']
    year2 = jobs['jobs'][jobindex]['year2']
    month1 = jobs['jobs'][jobindex]['month1']
    month2 = jobs['jobs'][jobindex]['month2']
    input_schema = jobs['schema']
    code_tables  = jobs['code_tables']
    
    verbose = True # need set to read as arg in future


    logging.info('Input file is {}'.format(inputfile))
    logging.info('Running from {} {} to {} {}'.format(month1, year1, month2, year2))
    logging.info('')

    config = ConfigParser.ConfigParser()
    config.read(inputfile)
    icoads_dir = config.get('Directories', 'ICOADS_dir')
    out_dir = config.get('Directories', 'out_dir')
    bad_id_file = config.get('Files', 'IDs_to_exclude')
    version = config.get('Icoads', 'icoads_version')

    logging.info('ICOADS directory = {}'.format(icoads_dir))
    logging.info('ICOADS version = {}'.format(version))
    logging.info('Output to {}'.format(out_dir))
    logging.info('List of bad IDs = {}'.format(bad_id_file))
    logging.info('Parameter file = {}'.format(config.get('Files', 'parameter_file')))
    logging.info('')

    ids_to_exclude = bf.process_bad_id_file(bad_id_file)

    # read in climatology files
    sst_pentad_stdev = clim.Climatology.from_filename(config.get('Climatologies', 'Old_SST_stdev_climatology'), 'sst')

    sst_stdev_1 = clim.Climatology.from_filename(config.get('Climatologies', 'SST_buddy_one_box_to_buddy_avg'), 'sst')
    sst_stdev_2 = clim.Climatology.from_filename(config.get('Climatologies', 'SST_buddy_one_ob_to_box_avg'), 'sst')
    sst_stdev_3 = clim.Climatology.from_filename(config.get('Climatologies', 'SST_buddy_avg_sampling'), 'sst')

    with open(config.get('Files', 'parameter_file'), 'r') as f:
        parameters = json.load(f)

    # read in high resolution SST climatology file
    for entry in parameters['hires_climatologies']:
        if entry[0] == 'SST' and entry[1] == 'mean':
            sst_climatology_file = entry[2]
            logging.info("hires sst climatology file {}".format(sst_climatology_file))

    climlib = ex.ClimatologyLibrary()
    climlib.add_field('SST', 'mean', clim.Climatology.from_filename(sst_climatology_file, 'temperature'))

    for year, month in qc.year_month_gen(year1, month1, year2, month2):

        logging.info("{} {}".format(year, month))

        last_year, last_month = qc.last_month_was(year, month)
        next_year, next_month = qc.next_month_is(year, month)

        reps = ex.Deck()
        count = 0

        for readyear, readmonth in qc.year_month_gen(last_year, last_month, next_year, next_month):

            logging.info("{} {}".format(readyear, readmonth))

            #icoads_dir = '/gws/nopw/j04/c3s311a_lot2/data/level0/marine/sub_daily_data/IMMA1_R3.0.0T-QC/'
            filename = icoads_dir + '{:4d}-{:02d}.psv'.format(readyear, readmonth)
            # YR|MO|DY|HR|LAT|LON|DS|VS|ID|AT|SST|DPT|DCK|SLP|SID|PT|UID|W|D|IRF|bad_data|outfile
            imma_obj = pd.read_csv(filename, sep='|', header=None,
                                   names=['YR', 'MO', 'DY', 'HR', 'LAT', 'LON', 'DS', 'VS', 'ID', 'AT', 'SST', 'DPT',
                                          'DCK', 'SLP', 'SID', 'PT', 'UID', 'W', 'D', 'IRF', 'bad_data', 'outfile'], low_memory = False)

            imma_obj['ID'].replace(' ','',inplace=True)        
            imma_obj = imma_obj.sort_values(['YR','MO','DY','HR','ID'], axis = 0, ascending = True )
            imma_obj = imma_obj.reset_index(drop=True)

            data_index = imma_obj.index


            rec = IMMA()

            for idx in data_index :
                # set missing values to None
                for k,v in imma_obj.loc[ idx, ].to_dict().items() :
                    rec.data[k] = to_none( v )

                readob = True
                if (not (rec.data['ID'] in ids_to_exclude) and
                        readob and
                        rec.data['YR'] == readyear and
                        rec.data['MO'] == readmonth and
                        rec.data['DY'] is not None): # dyb - new line / check

                    rep = ex.MarineReportQC(rec)
                    del rec

                rep_clim = climlib.get_field('SST', 'mean').get_value(rep.lat(), rep.lon(), rep.getvar('MO'),
                                                                  rep.getvar('DY'))
                rep.add_climate_variable('SST', rep_clim)

                rep.perform_base_sst_qc(parameters)
                rep.set_qc('POS', 'month_match', qc.month_match(year, month, rep.getvar('YR'), rep.getvar('MO')))

                reps.append(rep)
                count += 1

                rec = IMMA()                

            #icoads_file.close()

        logging.info("Read {} ICOADS records".format(count))

        # filter the obs into passes and fails of basic positional QC
        filt = ex.QC_filter()
        filt.add_qc_filter('POS', 'date', 0)
        filt.add_qc_filter('POS', 'time', 0)
        filt.add_qc_filter('POS', 'pos', 0)
        filt.add_qc_filter('POS', 'blklst', 0)

        reps.add_filter(filt)

        # track check the passes one ship at a time
        count_ships = 0
        for one_ship in reps.get_one_platform_at_a_time():
            one_ship.sort() # corrections applied can move reports between months, corrections currently applied after reading IMMA
            one_ship.track_check(parameters['track_check'])
            one_ship.find_repeated_values(parameters['find_repeated_values'], intype='SST')
            count_ships += 1

        logging.info("Track checked {} ships".format(count_ships))

        # SST buddy check
        filt = ex.QC_filter()
        filt.add_qc_filter('POS', 'is780', 0)
        filt.add_qc_filter('POS', 'date', 0)
        filt.add_qc_filter('POS', 'time', 0)
        filt.add_qc_filter('POS', 'pos', 0)
        filt.add_qc_filter('POS', 'blklst', 0)
        filt.add_qc_filter('POS', 'trk', 0)
        filt.add_qc_filter('SST', 'noval', 0)
        filt.add_qc_filter('SST', 'freez', 0)
        filt.add_qc_filter('SST', 'clim', 0)
        filt.add_qc_filter('SST', 'nonorm', 0)

        reps.add_filter(filt)

        reps.bayesian_buddy_check('SST', sst_stdev_1, sst_stdev_2, sst_stdev_3, parameters)
        reps.mds_buddy_check('SST', sst_pentad_stdev, parameters['mds_buddy_check'])

        extdir = bf.safe_make_dir(out_dir, year, month)

        varnames_to_print = {
            'SST': ['bud', 'clim', 'nonorm', 'freez', 'noval', 'nbud', 'bbud', 'rep', 'spike', 'hardlimit']}

        reps.write_qc('hires_' + parameters['runid'], extdir, year, month, varnames_to_print)

        if tracking:
            # set QC for output by ID - buoys only and passes base SST QC
            filt = ex.QC_filter()
            filt.add_qc_filter('POS', 'month_match', 1)
            filt.add_qc_filter('POS', 'isdrifter', 1)

            reps.add_filter(filt)

            idfile = open(extdir + '/ID_file.txt', 'w')
            for one_ship in reps.get_one_platform_at_a_time():

                if len(one_ship) > 0:
                    thisid = one_ship.getrep(0).getvar('ID')
                    if thisid is not None:
                        idfile.write(thisid + ',' + ex.safe_filename(thisid) + '\n')
                        one_ship.write_qc('hires_' + parameters['runid'], extdir, year, month, varnames_to_print)
            idfile.close()

        del reps


if __name__ == '__main__':
    main(sys.argv[1:])
