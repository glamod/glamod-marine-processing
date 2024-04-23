#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 14:27:16 2022

@author: sbiri
"""
import os
import pandas as pd
import cdm
import argparse
import sys

def main(argv):
    """
    replace quality flag in level2 data to bad (1) if UIDs exist in LZ file
    """

    print('########################')
    print('Running level2 UID check')
    print('########################')

    parser = argparse.ArgumentParser(description='Level2 check, main program')
    parser.add_argument('-l2path', type=str, help='path to level2 data')
    parser.add_argument('-lzpath', type=str, help='path to LZ data')
    parser.add_argument('-release', type=str, help='release')
    parser.add_argument('-update', type=str, help='update')
    parser.add_argument('-sid_dck', type=str, help='source ID and deckl')
    parser.add_argument('-year', type=str, help='year')
    parser.add_argument('-month', type=str, help='month')

    args = parser.parse_args()

    l2path = args.l2path
    lzpath = args.lzpath
    rls = args.release
    updt = args.update
    sid = args.sid_dck
    yr = args.year
    mo = args.month

    cdm_tables = cdm.lib.tables.tables_hdlr.load_tables()
    #obs_tables = [ x for x in cdm_tables.keys() if x != 'header' ]
    obs_tables = cdm_tables.keys()
    print(obs_tables)

    for i in obs_tables:
        print("Running process for sid "+sid+" table "+i+" date "+yr+"-"+mo)
        fn = os.path.join(l2path, sid, i+"-"+yr+"-"+mo+"-"+rls+"-"+updt+".psv")
        fn_f = os.path.join(lzpath, "lz_"+yr+"-"+mo+".psv")
        #print(fn)
        #print(fn_f)
        if os.path.exists(fn):
            df = pd.read_csv(fn, delimiter = '|', dtype = 'object',
                             quotechar=None, quoting=3)
            df1 = pd.read_csv(fn_f, delimiter = '|', dtype = 'object',
                              names=["UID"], quotechar=None, quoting=3)
            if df1.UID.isin(df.report_id).any().any():
                print(fn)
                if i=="header":
                    df['report_quality'].loc[df.report_id.isin(df1.UID)] = 1
                    print(df['report_quality'].loc[df.report_id.isin(df1.UID)])
                else:
                    df['quality_flag'].loc[df.report_id.isin(df1.UID)] = 1
                    #print(df['quality_flag'].loc[df.report_id.isin(df1.UID)])
                cdm_columns = cdm_tables.get(i).keys()
                df.to_csv(fn, index = False, sep = '|',
                          columns = cdm_columns, header = True, mode = "w",
                          na_rep = 'null')

    return

if __name__ == "__main__":
    main(sys.argv)
