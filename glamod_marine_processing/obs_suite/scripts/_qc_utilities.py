"""QC Utility functions for level1e script."""

from __future__ import annotations

import copy
import datetime
import logging
import operator
import os

import numpy as np
import pandas as pd
from _utilities import read_cdm_tables
from marine_qc import qc_grouped_reports, qc_individual_reports, qc_sequential_reports
from marine_qc.external_clim import Climatology
from marine_qc.multiple_row_checks import do_multiple_row_check

op_map = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "//": operator.floordiv,
    "%": operator.mod,
    "**": operator.pow,
}


def update_dtypes(data_df, table):
    """Update dtypes in DataFrame."""
    if table == "header":
        data_df["platform_type"] = data_df["platform_type"].astype(int)
        data_df["latitude"] = data_df["latitude"].astype(float)
        data_df["longitude"] = data_df["longitude"].astype(float)
        data_df["report_timestamp"] = pd.to_datetime(
            data_df["report_timestamp"],
            format="%Y-%m-%d %H:%M:%S",
            errors="coerce",
        )
        data_df["station_speed"] = data_df["station_speed"].astype(float)
        data_df["station_course"] = data_df["station_course"].astype(float)
        data_df["report_quality"] = data_df["report_quality"].astype(int)
        data_df["location_quality"] = data_df["location_quality"].astype(int)
        data_df["report_time_quality"] = data_df["report_time_quality"].astype(int)
    else:
        data_df["observation_value"] = data_df["observation_value"].astype(float)
        data_df["latitude"] = data_df["latitude"].astype(float)
        data_df["longitude"] = data_df["longitude"].astype(float)
        data_df["date_time"] = pd.to_datetime(
            data_df["date_time"],
            format="%Y-%m-%d %H:%M:%S",
            errors="coerce",
        )
        data_df["quality_flag"] = data_df["quality_flag"].astype(int)
    return data_df


def get_qc_columns(data_dict):
    """Copy data dictionary, convert values and get quality flags."""
    quality_flags = {}
    report_quality = pd.Series()
    location_quality = pd.Series()
    report_time_quality = pd.Series()
    history = pd.Series()
    data_dict_qc = {}

    for table, df in data_dict.items():
        update_dtypes(df, table)

        data_dict_qc[table] = df.copy()

        if table == "header":
            report_quality = df["report_quality"].copy()
            location_quality = df["location_quality"].copy()
            report_time_quality = df["report_time_quality"].copy()
            history = df["history"].copy()
        else:
            quality_flags[table] = df["quality_flag"].copy()

    return (
        data_dict_qc,
        report_quality,
        location_quality,
        report_time_quality,
        quality_flags,
        history,
    )


def get_single_qc_flag(df):
    """Get single QC flag from DataFrame containing multiple QC flags."""
    mask_0 = (df == 0).any(axis=1)
    mask_1 = (df == 1).any(axis=1)
    mask_2 = (df == 2).any(axis=1)
    mask_3 = (df == 3).any(axis=1)

    conditions = [mask_1, mask_0, mask_3, mask_2]
    choices = [1, 0, 3, 2]
    result = np.select(conditions, choices, default=2)
    return pd.Series(result, index=df.index, name="QC_FLAG")


def compare_quality_checks(df, location_quality, report_time_quality):
    """Compare entries with location_quality and report_time_quality."""
    df[location_quality == 2] = 1
    df[report_time_quality == 4] = 1
    df[report_time_quality == 5] = 1


def update_filenames(d, ext_path):
    """Ad external file path to file names."""
    if isinstance(d, dict):
        for k, v in d.items():
            if k == "file_name":
                d[k] = os.path.join(ext_path, v)
            elif isinstance(v, dict):
                update_filenames(v, ext_path)


def open_netcdffiles(d):
    """Open filenames as Climatology objects."""
    if isinstance(d, dict):
        for k, v in d.items():
            if k == "inputs":
                if not isinstance(v, dict):
                    continue
                d[k] = Climatology.open_netcdf_file(**v)
            elif isinstance(v, dict):
                open_netcdffiles(v)


def drop_invalid_indexes(df, df_ref, failed_qc):
    """Drop invalid indexes."""
    indexes_failed = df_ref[df_ref == failed_qc].index
    indexes_failed = indexes_failed.intersection(df.index)
    df.drop(index=indexes_failed, inplace=True)


def get_combined_input_values(tables, names, data_dict):
    """Get combined input values."""
    inputs = {}
    for ivar, table in tables.items():
        data = data_dict[table]
        column = names[ivar]
        inputs[ivar] = data[column]

    series_list = list(inputs.values())
    common_indexes = set(series_list[0].index).intersection(
        *(s.index for s in series_list[1:])
    )
    common_indexes = list(common_indexes)
    for ivar, series in inputs.items():
        inputs[ivar] = inputs[ivar].loc[common_indexes]
    return inputs


def all_tables_available(tables, data_dict):
    """Check if all tables available in data_dict."""
    available = True
    for table in tables:
        if table not in data_dict.keys():
            available = False
            break
    return available


def run_qc_by_group(inputs, group_df, func, kwargs):
    """Run QC function grouped by primary_station_id."""
    failed_idxs = []
    sample_input = next(iter(inputs.values()))

    for ps_id, subset in group_df.groupby("primary_station_id"):
        idx = sample_input.index.intersection(subset.index)
        if idx.empty:
            continue

        subset_inputs = {k: v.loc[idx] for k, v in inputs.items()}
        qc_flags = func(**subset_inputs, **kwargs)

        failed = qc_flags[qc_flags == 1].index
        if not failed.empty:
            failed_idxs.extend(failed)

    return failed_idxs


class Parameters:
    """Get parameters from qc_dict."""

    def __init__(self, qc_dict, qc_module):
        self.func = getattr(qc_module, qc_dict["func"])
        self.names = qc_dict.get("names", {})
        self.kwargs = qc_dict.get("arguments", {})
        self.preproc = qc_dict.get("preproc", {})
        self.tables = qc_dict.get("tables", None)


def get_qc_function_and_inputs(qc_dict, data, table_name, qc_module):
    """Extract the function, inputs, and arguments from a QC config."""
    parameters = Parameters(qc_dict, qc_module)

    if isinstance(parameters.tables, list) and table_name not in parameters.tables:
        return None, None, None

    if table_name in parameters.preproc.keys():
        col = parameters.preproc[table_name]["column"]
        op_str = parameters.preproc[table_name]["operation"]
        op_symbol, operand = op_str.strip().split()
        operand = float(operand)
        data[col] = op_map[op_symbol](data[col], operand)

    inputs = {k: data[v] for k, v in parameters.names.items()}

    return parameters.func, inputs, parameters.kwargs


def add_buoy_data_and_get_ignore_indexes(
    data, params_buoy, obs_table, buoy_dataset, buoy_dck
):
    """Attempts to read buoy data and append it to the main data."""
    db_buoy = pd.DataFrame()
    if buoy_dataset != "None" and buoy_dck != "None":
        db_buoy = read_cdm_tables(params_buoy, obs_table)
        if not db_buoy.empty:
            data_buoy = db_buoy[obs_table].set_index("report_id", drop=False)
            update_dtypes(data_buoy, obs_table)
            data = pd.concat([data, data_buoy])
        else:
            logging.warning(
                f"Could not find any {obs_table} {buoy_dataset} data for {params_buoy.prev_fileID}: {params_buoy.prev_level_path}"
            )
    else:
        logging.warning(
            f"Buoy dataset or deck not specified for {obs_table} (dataset={buoy_dataset}, dck={buoy_dck})"
        )

    indexes_buoy = db_buoy.index if not db_buoy.empty else []
    ignore_indexes = data.index.get_indexer(indexes_buoy) if db_buoy.empty else None

    return data, ignore_indexes


def update_preproc_dict(preproc_dict, preproc_dict_ind, obs_table, ext_path):
    """Update preprocessing dictionary for a given obs_table."""
    preproc_obs = preproc_dict.get(obs_table, {}).copy()
    preproc_ind_obs = preproc_dict_ind.get(obs_table, {})

    for var_name, val in preproc_obs.items():
        if val == "__individual_reports__":
            preproc_obs[var_name] = preproc_ind_obs.get(var_name, {}).get("inputs")

    update_filenames(preproc_obs, ext_path)
    open_netcdffiles(preproc_obs)

    for var_name, val in preproc_obs.items():
        if isinstance(val, dict) and "inputs" in val:
            preproc_obs[var_name] = val["inputs"]

    return preproc_obs


def do_qc_individual(
    data_dict_qc,
    report_quality,
    location_quality,
    report_time_quality,
    quality_flags,
    params,
    ext_path,
):
    """Individual QC."""

    def do_qc_individual_header():
        # 1.1. Header
        logging.info("1.1. Do header checks")
        qc_dict_header = qc_dict.get("header", {})
        data = data_dict_qc["header"]

        # 1.1.1. Position check
        logging.info("1.1.1. Do positional checks")

        # Deselect already failed location_qualities
        data_pos = data[location_quality.loc[data.index] != 2]
        idx_pos = data_pos.index

        # Do position check
        qc_dict_pos = qc_dict_header.get("position_check", {})
        pos_qc = do_multiple_row_check(
            data=data_pos,
            qc_dict=qc_dict_pos,
            return_method=return_method,
        )
        pos_qc = get_single_qc_flag(pos_qc)
        pos_qc = pos_qc.replace({1: 2, 2: 3})
        location_quality.loc[idx_pos] = pos_qc

        # 1.1.2. Time check
        logging.info("1.1.2. Do time checks")

        # Deselect already failed report_time_qualities
        data_time = data[
            (report_time_quality.loc[data.index] != 4)
            & (report_time_quality.loc[data.index] != 5)
        ]

        # Do time check
        qc_dict_tme = qc_dict_header.get("time_check", {})
        time_qc = do_multiple_row_check(
            data=data_time,
            qc_dict=qc_dict_tme,
            return_method=return_method,
        )
        time_qc = get_single_qc_flag(time_qc)
        time_qc = time_qc.replace({1: 5, 2: 4, 3: 4})
        invalid_indexes = time_qc[time_qc != 0].index
        report_time_quality.loc[invalid_indexes] = time_qc[invalid_indexes]

        # 1.1.3. Report quality
        logging.info("1.1.3. Set report quality")
        compare_quality_checks(report_quality, location_quality, report_time_quality)

        drop_invalid_indexes(data, report_quality, 1)

    def do_qc_individual_observations():
        # 1.2. Observations
        logging.info("1.2. Do observations checks")

        # 1.2.1. Do observation check
        i = 1
        for obs_table in data_dict_qc.keys():
            if obs_table == "header":
                continue
            logging.info(f"1.2.{i}. Do {obs_table} check")
            data = data_dict_qc[obs_table]
            quality_flag = quality_flags[obs_table]

            # Deselect already failed quality_flags
            drop_invalid_indexes(data, quality_flag, 1)

            # Deselect already failed report_qualities
            drop_invalid_indexes(data, report_quality, 1)

            # Deselect missing values
            qc_dict_miss = qc_dict.get("observations", {}).get("missing_values")
            miss_qc = do_multiple_row_check(
                data=data,
                qc_dict=qc_dict_miss,
                return_method=return_method,
            )
            miss_qc = get_single_qc_flag(miss_qc)
            quality_flag.loc[miss_qc[miss_qc == 1].index] = 3
            drop_invalid_indexes(data, quality_flag, 3)

            # Do QC
            preproc_dict = qc_dict.get("preprocessing", {}).get(obs_table, {})
            qc_dict_obs = qc_dict.get("observations", {}).get(obs_table, {})
            update_filenames(preproc_dict, ext_path)
            open_netcdffiles(preproc_dict)
            obs_qc = do_multiple_row_check(
                data=data,
                preproc_dict=preproc_dict,
                qc_dict=qc_dict_obs,
                return_method=return_method,
            )
            obs_qc = get_single_qc_flag(obs_qc)
            invalid_indexes = obs_qc[obs_qc != 0].index

            # Flag quality_flag
            quality_flag.loc[invalid_indexes] = obs_qc[invalid_indexes]
            compare_quality_checks(quality_flag, location_quality, report_time_quality)

            drop_invalid_indexes(data, quality_flag, 1)

            i += 1

    def do_qc_individual_combined():
        # 1.2.2. Do combined observation check
        qc_dict_comb = qc_dict.get("observations", {}).get("combined", {})
        i = 1
        for qc_name in qc_dict_comb.keys():
            parameters = Parameters(qc_dict_comb[qc_name], qc_individual_reports)

            obs_tables = set(parameters.tables.values())
            if all_tables_available(obs_tables, data_dict_qc) is False:
                continue

            logging.info(f"1.2.{i}. Do combined {qc_name} check")

            inputs = get_combined_input_values(
                parameters.tables, parameters.names, data_dict_qc
            )

            qc_flag = parameters.func(**inputs)
            idx_failed = qc_flag[qc_flag == 1].index
            for table in obs_tables:
                quality_flags[table].loc[idx_failed] = qc_flag.loc[idx_failed]
                drop_invalid_indexes(data_dict_qc[table], qc_flag, 1)

            i += 1

    # Get QC settings for individual reports
    logging.info("1. Do individual checks")
    qc_dict = params.qc_settings.get("individual_reports")
    return_method = qc_dict["return_method"]

    # Do header QC
    do_qc_individual_header()

    # Do observations QC
    do_qc_individual_observations()

    # Do combined QC
    do_qc_individual_combined()

    # Return updated quality flags
    return report_quality, location_quality, report_time_quality, quality_flags


def do_qc_sequential(
    data_dict_qc,
    report_quality,
    location_quality,
    quality_flags,
    idx_gnrc,
    params,
):
    """Sequential QC."""

    def do_qc_sequential_header():
        # 2.1. Header
        logging.info("2.1. Do header checks")
        qc_dict = params.qc_settings.get("sequential_reports", {}).get("header", {})
        data = data_dict_qc["header"].copy()

        # Deselect rows containing generic ids
        data.drop(index=idx_gnrc, inplace=True)

        i = 1
        for qc_name in qc_dict.keys():
            logging.info(f"2.1.{i}. Do {qc_name} check.")

            # Deselect already failed report_qualities
            drop_invalid_indexes(data, report_quality, 1)

            # Get parameters
            func, inputs, kwargs = get_qc_function_and_inputs(
                qc_dict[qc_name], data, "header", qc_sequential_reports
            )
            if func is None:
                continue

            # Do QC
            indexes_failed = run_qc_by_group(inputs, data, func, kwargs)

            location_quality.loc[indexes_failed] = 2
            report_quality.loc[indexes_failed] = 1

            i += 1

        drop_invalid_indexes(data_dict_qc["header"], report_quality, 1)

    def do_qc_sequential_observations():
        # 2.2. Observations
        logging.info("2.2. Do observation checks")

        # 2.2.1. Do observation track check
        qc_dict = params.qc_settings.get("sequential_reports", {}).get(
            "observations", {}
        )
        i = 1
        for obs_table in data_dict_qc.keys():
            if obs_table == "header":
                continue

            logging.info(f"2.2.{i}. Do {obs_table} checks")
            quality_flag = quality_flags[obs_table]
            data = data_dict_qc[obs_table].copy()

            # Deselect rows containing generic ids
            idx_gnrc_obs = idx_gnrc.intersection(quality_flag.index)
            data = data.drop(index=idx_gnrc_obs)

            j = 1
            for qc_name in qc_dict.keys():
                logging.info(f"2.2.{i}.{j}. Do {qc_name} check")

                # Deselect already failed report_qualities
                drop_invalid_indexes(data, quality_flag, 1)

                # Get parameter
                func, inputs, kwargs = get_qc_function_and_inputs(
                    qc_dict[qc_name], data, obs_table, qc_sequential_reports
                )
                if func is None:
                    return

                # Do QC
                indexes_failed = run_qc_by_group(
                    inputs, data_dict_qc["header"], func, kwargs
                )

                quality_flag.loc[indexes_failed] = 1

                j += 1

            drop_invalid_indexes(data_dict_qc[obs_table], quality_flag, 1)

            i += 1

    def do_qc_sequential_combined():
        # 2.2.2. Do combined observations track check
        qc_dict = params.qc_settings.get("sequential_reports", {}).get("combined", {})

        i = 1
        for qc_name in qc_dict.keys():
            # Get parameters
            parameters = Parameters(qc_dict[qc_name], qc_sequential_reports)

            obs_tables = set(parameters.tables.values())
            if all_tables_available(obs_tables, data_dict_qc) is False:
                continue

            logging.info(f"2.2.{i}. Do {qc_name} check")
            inputs = get_combined_input_values(
                parameters.tables, parameters.names, data_dict_qc
            )

            indexes_failed = run_qc_by_group(
                inputs, data_dict_qc["header"], parameters.func, parameters.kwargs
            )

            for table in obs_tables:
                quality_flags[table].loc[indexes_failed] = 1
                drop_invalid_indexes(data_dict_qc[table], quality_flags[table], 1)

            i += 1

    logging.info("2. Do sequential checks")
    do_qc_sequential_header()

    do_qc_sequential_observations()

    do_qc_sequential_combined()

    return report_quality, location_quality, quality_flags


def do_qc_grouped(data_dict_qc, quality_flags, params, ext_path):
    """Grouped QC."""
    # 3. Buddy check
    logging.info("3. Do buddy checks")
    qc_dict = params.qc_settings.get("grouped_reports")

    # 3.1. Do observation buddy check
    preproc_dict = qc_dict.get("preprocessing", {})
    qc_dict_obs = qc_dict.get("observations")

    qc_dict_ind = params.qc_settings.get("individual_reports")
    preproc_dict_ind = qc_dict_ind.get("preprocessing", {})

    # Copy params for external buoy data
    params_buoy = copy.deepcopy(params)
    buoy_dataset = qc_dict.get("buoy_dataset", "None")
    buoy_dck = qc_dict.get("buoy_dck", "None")

    params_buoy.prev_level_path = params_buoy.prev_level_path.replace(
        params.dataset, buoy_dataset
    )
    params_buoy.prev_level_path = params_buoy.prev_level_path.replace(
        params.sid_dck, buoy_dck
    )

    i = 1
    for obs_table in data_dict_qc:
        if obs_table == "header":
            continue
        logging.info(f"3.{i}. Do {obs_table} checks")
        quality_flag = quality_flags[obs_table]
        data = data_dict_qc[obs_table].copy()

        # Add buoy data
        data, ignore_indexes = add_buoy_data_and_get_ignore_indexes(
            data, params_buoy, obs_table, buoy_dataset, buoy_dck
        )

        # Pre-processing
        preproc_dict_obs = update_preproc_dict(
            preproc_dict, preproc_dict_ind, obs_table, ext_path
        )

        j = 1

        # Get table-specific arguments
        qc_dict_obs_sp = qc_dict.get(obs_table, {})

        for qc_name in qc_dict_obs.keys():
            if obs_table not in qc_dict_obs[qc_name]["tables"]:
                continue

            logging.info(f"3.{i}.{j}. Do {qc_name} check")

            # Deselect already failed quality flags
            drop_invalid_indexes(data, quality_flag, 1)

            # Get parameters
            func, inputs, kwargs = get_qc_function_and_inputs(
                qc_dict_obs[qc_name], data, obs_table, qc_grouped_reports
            )
            if func is None:
                continue

            for var_name, value in kwargs.items():
                if isinstance(value, str) and value == "__preprocessed__":
                    kwargs[var_name] = preproc_dict_obs[var_name]

            kwargs["ignore_indexes"] = ignore_indexes
            for arg_name, arg_value in qc_dict_obs_sp.get(qc_name, {}).items():
                kwargs[arg_name] = arg_value

            qc_flag = func(**inputs, **kwargs)
            idx_failed = qc_flag[qc_flag == 1].index
            quality_flag.loc[idx_failed] = 1

            drop_invalid_indexes(data, quality_flag, 1)

            j += 1

        drop_invalid_indexes(data_dict_qc[obs_table], quality_flag, 1)

        i += 1

    return quality_flags


def do_qc(
    data_dict_qc,
    report_quality,
    location_quality,
    report_time_quality,
    quality_flags,
    history,
    params,
    ext_path,
):
    """QC."""
    # Set observation quality_flag on blacklist and deselect them
    try:
        history_tstmp = datetime.datetime.now(datetime.UTC).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    except AttributeError:  # for python < 3.11
        history_tstmp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    history_add = f";{history_tstmp}. {params.history_explain}"
    idx_blck = report_quality[report_quality == 6].index
    for table in data_dict_qc.keys():
        if table == "header":
            data_dict_qc[table].drop(index=idx_blck, inplace=True)
            idx_not_blck = data_dict_qc[table].index
            history.loc[idx_not_blck] = history.loc[idx_not_blck].apply(
                lambda x: x + history_add
            )
            continue

        idx_blck_obs = idx_blck.intersection(quality_flags[table].index)
        quality_flags[table].loc[idx_blck_obs] = 6
        data_dict_qc[table].drop(index=idx_blck_obs, inplace=True)

    # Set indexes of generic ID reports
    idx_gnrc = report_quality[report_quality == 88].index

    # Do the quality control
    report_quality, location_quality, report_time_quality, quality_flags = (
        do_qc_individual(
            data_dict_qc=data_dict_qc,
            report_quality=report_quality,
            location_quality=location_quality,
            report_time_quality=report_time_quality,
            quality_flags=quality_flags,
            params=params,
            ext_path=ext_path,
        )
    )

    report_quality, location_quality, quality_flags = do_qc_sequential(
        data_dict_qc=data_dict_qc,
        report_quality=report_quality,
        location_quality=location_quality,
        quality_flags=quality_flags,
        idx_gnrc=idx_gnrc,
        params=params,
    )

    quality_flags = do_qc_grouped(
        data_dict_qc=data_dict_qc,
        quality_flags=quality_flags,
        params=params,
        ext_path=ext_path,
    )

    return report_quality, location_quality, report_time_quality, quality_flags, history
