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
from marine_qc.auxiliary import isvalid
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


def get_combined_input_values(tables, names, data_dict, drop_idx=None):
    """Get combined input values."""
    inputs = {}
    for ivar, table in tables.items():
        data = data_dict[table]
        column = names[ivar]
        inputs[ivar] = data[column]
        if drop_idx is None:
            continue
        intersec = inputs[ivar].index.intersection(drop_idx)
        inputs[ivar] = inputs[ivar].drop(index=intersec)

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
    passed_idxs = []
    failed_idxs = []
    sample_input = next(iter(inputs.values()))

    for ps_id, subset in group_df.groupby("primary_station_id"):
        idx = sample_input.index.intersection(subset.index)
        if idx.empty:
            continue

        subset_inputs = {k: v.loc[idx] for k, v in inputs.items()}
        qc_flags = func(**subset_inputs, **kwargs)

        passed = qc_flags[qc_flags == 0].index
        failed = qc_flags[qc_flags == 1].index
        if not passed.empty:
            passed_idxs.extend(passed)
        if not failed.empty:
            failed_idxs.extend(failed)

    return passed_idxs, failed_idxs


class Parameters:
    """Get parameters from qc_dict."""

    def __init__(self, qc_dict, qc_module):
        self.func = getattr(qc_module, qc_dict["func"])
        self.names = copy.deepcopy(qc_dict.get("names", {}))
        self.kwargs = copy.deepcopy(qc_dict.get("arguments", {}))
        self.preproc = copy.deepcopy(qc_dict.get("preproc", {}))
        self.tables = copy.deepcopy(qc_dict.get("tables", None))
        self.get_flagged = copy.deepcopy(qc_dict.get("get_flagged", None))


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


def add_buoy_data_and_get_buoy_indexes(
    data, params_buoy, obs_table, buoy_dataset, buoy_dck
):
    """Attempts to read buoy data and append it to the main data."""
    data_buoy = pd.DataFrame()
    if buoy_dataset != "None" and buoy_dck != "None":
        db_buoy = read_cdm_tables(params_buoy, obs_table)
        if not db_buoy.empty:
            data_buoy = db_buoy[obs_table].set_index("report_id", drop=False)
            update_dtypes(data_buoy, obs_table)
            valid_indexes = (
                isvalid(data_buoy["observation_value"])
                & isvalid(data_buoy["latitude"])
                & isvalid(data_buoy["longitude"])
                & isvalid(data_buoy["date_time"])
                & (data_buoy["quality_flag"] == 0)
            )
            data_buoy = data_buoy[valid_indexes]
            data = pd.concat([data, data_buoy])
        else:
            logging.warning(
                f"Could not find any {obs_table} {buoy_dataset} data for {params_buoy.prev_fileID}: {params_buoy.prev_level_path}"
            )
    else:
        logging.warning(
            f"Buoy dataset or deck not specified for {obs_table} (dataset={buoy_dataset}, dck={buoy_dck})"
        )

    buoy_indexes = data_buoy.index if not data_buoy.empty else pd.Index([])
    return data, buoy_indexes  # ignore_indexes


def do_qc_individual_header(
    data,
    report_quality,
    location_quality,
    report_time_quality,
    params,
    ext_path,
    i=1,
    j=1,
):

    qc_dict = copy.deepcopy(params.qc_settings.get("individual_reports"))
    return_method = qc_dict["return_method"]

    # Header
    logging.info(f"{i}.{j}. Do individual header checks")
    qc_dict_header = copy.deepcopy(qc_dict.get("header", {}))

    # Position check
    logging.info(f"{i}.{j}.1. Do positional checks")

    # Deselect already failed location_qualities
    data_pos = data[location_quality.loc[data.index] != 2]
    idx_pos = data_pos.index

    # Do position check
    qc_dict_pos = copy.deepcopy(qc_dict_header.get("position_check", {}))
    pos_qc = do_multiple_row_check(
        data=data_pos,
        qc_dict=qc_dict_pos,
        return_method=return_method,
    )
    pos_qc = get_single_qc_flag(pos_qc)
    pos_qc = pos_qc.replace({1: 2, 2: 3})
    location_quality.loc[idx_pos] = pos_qc

    # Time check
    logging.info(f"{i}.{j}.2. Do time checks")

    # Deselect already failed report_time_qualities
    data_time = data[
        (report_time_quality.loc[data.index] != 4)
        & (report_time_quality.loc[data.index] != 5)
    ]

    # Do time check
    qc_dict_tme = copy.deepcopy(qc_dict_header.get("time_check", {}))
    time_qc = do_multiple_row_check(
        data=data_time,
        qc_dict=qc_dict_tme,
        return_method=return_method,
    )
    time_qc = get_single_qc_flag(time_qc)
    time_qc = time_qc.replace({1: 5, 2: 4, 3: 4})
    invalid_indexes = time_qc[time_qc != 0].index
    report_time_quality.loc[invalid_indexes] = time_qc[invalid_indexes]

    # Report quality
    logging.info(f"{i}.{j}.3. Set report quality")
    compare_quality_checks(report_quality, location_quality, report_time_quality)

    return report_quality, location_quality, report_time_quality


def do_qc_individual_observation(
    data,
    table,
    quality_flag,
    params,
    ext_path,
    i=1,
    j=1,
    k=1,
):
    logging.info(f"{i}.{j}.{k}. Do individual {table} check")
    qc_dict = copy.deepcopy(params.qc_settings.get("individual_reports"))
    return_method = qc_dict["return_method"]

    # Deselect missing values
    qc_dict_miss = copy.deepcopy(qc_dict.get("observations", {}).get("missing_values"))
    miss_qc = do_multiple_row_check(
        data=data,
        qc_dict=qc_dict_miss,
        return_method=return_method,
    )
    miss_qc = get_single_qc_flag(miss_qc)
    quality_flag.loc[miss_qc[miss_qc == 1].index] = 3
    drop_invalid_indexes(data, quality_flag, 3)

    # Do QC
    preproc_dict = copy.deepcopy(qc_dict.get("preprocessing", {}).get(table, {}))
    qc_dict_obs = copy.deepcopy(qc_dict.get("observations", {}).get(table, {}))
    update_filenames(preproc_dict, ext_path)
    open_netcdffiles(preproc_dict)
    obs_qc = do_multiple_row_check(
        data=data,
        preproc_dict=preproc_dict,
        qc_dict=qc_dict_obs,
        return_method=return_method,
    )
    obs_qc = get_single_qc_flag(obs_qc)

    # Flag quality_flag
    passed = obs_qc[obs_qc == 0].index
    failed = obs_qc[obs_qc == 1].index
    quality_flag.loc[passed] = 0
    quality_flag.loc[failed] = 1
    return quality_flag


def do_qc_individual_combined(
    data_dict_qc,
    quality_flags,
    params,
    ext_path,
    i=1,
    j=1,
    k=1,
):
    qc_dict = copy.deepcopy(params.qc_settings.get("individual_reports"))

    # Do combined observation check
    qc_dict_comb = copy.deepcopy(qc_dict.get("observations", {}).get("combined", {}))

    for qc_name in qc_dict_comb.keys():
        parameters = Parameters(qc_dict_comb[qc_name], qc_individual_reports)

        obs_tables = set(parameters.tables.values())
        if all_tables_available(obs_tables, data_dict_qc) is False:
            continue

        logging.info(f"{i}.{j}.{k}. Do individual combined {qc_name} check")

        inputs = get_combined_input_values(
            parameters.tables, parameters.names, data_dict_qc
        )

        qc_flag = parameters.func(**inputs)
        idx_passed = qc_flag[qc_flag == 0].index
        idx_failed = qc_flag[qc_flag == 1].index

        if parameters.get_flagged is not None:
            obs_tables = parameters.get_flagged
        for table in obs_tables:
            quality_flags[table].loc[idx_passed] = 0
            quality_flags[table].loc[idx_failed] = 1
            drop_invalid_indexes(data_dict_qc[table], qc_flag, 1)

        k += 1

    return quality_flags


def do_qc_sequential_header(
    data,
    report_quality,
    location_quality,
    idx_gnrc,
    params,
    i=1,
    j=1,
):
    # Header
    logging.info(f"{i}.{j}. Do sequential header checks")
    qc_dict = copy.deepcopy(
        params.qc_settings.get("sequential_reports", {}).get("header", {})
    )
    data = data.copy()

    # Deselect rows containing generic ids
    invalid_indexes = idx_gnrc.intersection(data.index)
    data.drop(index=invalid_indexes, inplace=True)

    k = 1
    for qc_name in qc_dict.keys():
        # Deselect already failed report_qualities
        drop_invalid_indexes(data, report_quality, 1)

        # Get parameters
        func, inputs, kwargs = get_qc_function_and_inputs(
            qc_dict[qc_name], data, "header", qc_sequential_reports
        )
        if func is None:
            continue

        logging.info(f"{i}.{j}.{k}. Do sequential {qc_name} check.")

        # Do QC
        indexes_passed, indexes_failed = run_qc_by_group(inputs, data, func, kwargs)

        location_quality.loc[indexes_passed] = 0
        location_quality.loc[indexes_failed] = 2
        report_quality.loc[indexes_failed] = 1

        k += 1

    return report_quality, location_quality


def do_qc_sequential_observation(
    data,
    table,
    quality_flag,
    idx_gnrc,
    data_group,
    params,
    i=1,
    j=1,
    k=1,
):
    """Sequential QC."""
    # Do observation track check
    qc_dict = copy.deepcopy(
        params.qc_settings.get("sequential_reports", {}).get("observations", {})
    )

    logging.info(f"{i}.{j}.{k}. Do sequential {table} checks")
    data = data.copy()

    # Deselect rows containing generic ids
    idx_gnrc_obs = idx_gnrc.intersection(data.index)
    data = data.drop(index=idx_gnrc_obs)

    l = 1  # noqa: E741
    for qc_name in qc_dict.keys():
        # Deselect already failed report_qualities
        drop_invalid_indexes(data, quality_flag, 1)

        # Get parameter
        func, inputs, kwargs = get_qc_function_and_inputs(
            qc_dict[qc_name], data, table, qc_sequential_reports
        )
        if func is None:
            continue

        logging.info(f"{i}.{j}.{k}.{l}. Do {qc_name} check")

        # Do QC
        indexes_passed, indexes_failed = run_qc_by_group(
            inputs, data_group, func, kwargs
        )

        quality_flag.loc[indexes_passed] = 0
        quality_flag.loc[indexes_failed] = 1

        l += 1  # noqa: E741

    return quality_flag


def do_qc_sequential_combined(
    data_dict_qc,
    quality_flags,
    idx_gnrc,
    params,
    i=1,
    j=1,
    k=1,
):
    """Sequential QC."""
    # Do combined observations track check
    qc_dict = copy.deepcopy(
        params.qc_settings.get("sequential_reports", {}).get("combined", {})
    )

    for qc_name in qc_dict.keys():
        # Get parameters
        parameters = Parameters(qc_dict[qc_name], qc_sequential_reports)

        obs_tables = set(parameters.tables.values())
        if all_tables_available(obs_tables, data_dict_qc) is False:
            continue

        logging.info(f"{i}.{j}.{k}. Do sequential combined {qc_name} check")
        inputs = get_combined_input_values(
            parameters.tables,
            parameters.names,
            data_dict_qc,
            drop_idx=idx_gnrc,
        )

        indexes_passed, indexes_failed = run_qc_by_group(
            inputs, data_dict_qc["header"], parameters.func, parameters.kwargs
        )
        if parameters.get_flagged is not None:
            obs_tables = parameters.get_flagged
        for table in obs_tables:
            quality_flags[table].loc[indexes_passed] = 0
            quality_flags[table].loc[indexes_failed] = 1
            drop_invalid_indexes(data_dict_qc[table], quality_flags[table], 1)

        k += 1

    return quality_flags


def do_qc_grouped_observation(
    data, table, quality_flag, params, ext_path, i=1, j=1, k=1
):
    """Grouped QC."""
    logging.info(f"{i}.{j}.{k}. Do grouped {table} checks")

    # Buddy check
    qc_dict = copy.deepcopy(params.qc_settings.get("grouped_reports"))

    # Do observation buddy check
    preproc_dict = copy.deepcopy(qc_dict.get("preprocessing", {}))
    qc_dict_obs = copy.deepcopy(qc_dict.get("observations"))

    qc_dict_ind = copy.deepcopy(params.qc_settings.get("individual_reports"))
    preproc_dict_ind = qc_dict_ind.get("preprocessing", {})

    # Copy params for external buoy data
    params_buoy = copy.deepcopy(params)
    buoy_dataset = copy.deepcopy(qc_dict.get("buoy_dataset", "None"))
    buoy_dck = copy.deepcopy(qc_dict.get("buoy_dck", "None"))

    params_buoy.prev_level_path = params_buoy.prev_level_path.replace(
        params.dataset, buoy_dataset
    )
    params_buoy.prev_level_path = params_buoy.prev_level_path.replace(
        params.sid_dck, buoy_dck
    )

    data = data.copy()

    # Add buoy data
    data, buoy_indexes = add_buoy_data_and_get_buoy_indexes(
        data, params_buoy, table, buoy_dataset, buoy_dck
    )

    # Pre-processing
    preproc_dict_obs = copy.deepcopy(preproc_dict.get(table, {}))
    preproc_dict_ind_obs = copy.deepcopy(preproc_dict_ind.get(table, {}))

    for var_name, val in preproc_dict_obs.items():
        if val == "__individual_reports__":
            preproc_dict_obs[var_name] = {
                "inputs": copy.deepcopy(
                    preproc_dict_ind_obs.get(var_name, {}).get("inputs")
                )
            }

    update_filenames(preproc_dict_obs, ext_path)
    open_netcdffiles(preproc_dict_obs)

    for var_name, val in preproc_dict_obs.items():
        if isinstance(val, dict) and "inputs" in val:
            preproc_dict_obs[var_name] = val["inputs"]

    l = 1  # noqa: E741

    # Get table-specific arguments
    qc_dict_obs_sp = copy.deepcopy(qc_dict.get(table, {}))

    for qc_name in qc_dict_obs.keys():
        if table not in qc_dict_obs[qc_name]["tables"]:
            continue

        logging.info(f"{i}.{j}.{k}.{l}. Do {qc_name} check")

        # Deselect already failed quality flags
        drop_invalid_indexes(data, quality_flag, 1)

        # Get parameters
        func, inputs, kwargs = get_qc_function_and_inputs(
            qc_dict_obs[qc_name], data, table, qc_grouped_reports
        )
        if func is None:
            continue

        for var_name, value in kwargs.items():
            if isinstance(value, str) and value == "__preprocessed__":
                kwargs[var_name] = preproc_dict_obs[var_name]

        kwargs["ignore_indexes"] = data.index.get_indexer(buoy_indexes)
        for arg_name, arg_value in qc_dict_obs_sp.get(qc_name, {}).items():
            kwargs[arg_name] = arg_value

        qc_flag = func(**inputs, **kwargs)
        idx_passed = qc_flag[qc_flag == 0].index
        idx_failed = qc_flag[qc_flag == 1].index
        quality_flag.loc[idx_passed] = 0
        quality_flag.loc[idx_failed] = 1

        drop_invalid_indexes(data, quality_flag, 1)

        l += 1  # noqa: E741

    return quality_flag


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
    # Update history
    try:
        history_tstmp = datetime.datetime.now(datetime.UTC).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    except AttributeError:  # for python < 3.11
        history_tstmp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    history_add = f";{history_tstmp}. {params.history_explain}"

    # Define indexes for both blacklist and generic IDs
    idx_blck = report_quality[report_quality == 6].index
    idx_gnrc = report_quality[report_quality == 88].index
    idx_fld = report_quality[report_quality == 1].index

    # DO QC
    i = 1
    obs_tables = [table for table in data_dict_qc.keys() if table != "header"]

    # Header
    logging.info(f"{i}. Do header checks")

    # Remove already failed report_qualities
    data_dict_qc["header"].drop(index=idx_fld, inplace=True)

    # Remove reports on blacklist and update history
    data_dict_qc["header"].drop(index=idx_blck, inplace=True)
    idx_not_blck = data_dict_qc["header"].index
    history.loc[idx_not_blck] = history.loc[idx_not_blck].apply(
        lambda x: x + history_add
    )

    # Set report_qualities for generic IDs to passed
    report_quality.loc[idx_gnrc] = 0

    # Do individual header QC
    print("Before QC")
    print("report_quality: ", report_quality.value_counts().to_dict())
    print("location_quality: ", location_quality.value_counts().to_dict())
    print("report_time_quality: ", report_time_quality.value_counts().to_dict())
    for table in obs_tables:
        print(table, ": ", quality_flags[table].value_counts().to_dict())

    j = 1
    report_quality, location_quality, report_time_quality = do_qc_individual_header(
        data_dict_qc["header"],
        report_quality,
        location_quality,
        report_time_quality,
        params,
        ext_path,
        i=i,
        j=j,
    )
    print("After individual header QC")
    print("report_quality: ", report_quality.value_counts().to_dict())
    print("location_quality: ", location_quality.value_counts().to_dict())
    print("report_time_quality: ", report_time_quality.value_counts().to_dict())

    # Remove already failed report_qualities
    drop_invalid_indexes(data_dict_qc["header"], report_quality, 1)

    # Do sequential header QC
    j = 2
    report_quality, location_quality = do_qc_sequential_header(
        data_dict_qc["header"],
        report_quality,
        location_quality,
        idx_gnrc,
        params,
        i=i,
        j=j,
    )
    print("After sequential header QC")
    print("report_quality: ", report_quality.value_counts().to_dict())
    print("location_quality: ", location_quality.value_counts().to_dict())
    print("report_time_quality: ", report_time_quality.value_counts().to_dict())

    # Remove already failed report_qualities
    drop_invalid_indexes(data_dict_qc["header"], report_quality, 1)

    # Observations
    i += 1
    logging.info(f"{i}. Do observation checks")

    # Do individual observations checks
    j = 1
    k = 1
    logging.info(f"{i}.{j}. Do individual observations checks")

    for table in obs_tables:
        # Remove already failed quality_flags
        idx_fld_obs = quality_flags[table][quality_flags[table] == 1].index
        data_dict_qc[table].drop(index=idx_fld_obs, inplace=True)

        # Remove observations on blacklist
        idx_blck_obs = idx_blck.intersection(quality_flags[table].index)
        quality_flags[table].loc[idx_blck_obs] = 6
        idx_blck_obs = quality_flags[table][quality_flags[table] == 6].index
        data_dict_qc[table].drop(index=idx_blck_obs, inplace=True)

        # Remove already failed report_qualities
        drop_invalid_indexes(data_dict_qc[table], report_quality, 1)

        # Do individual QC
        quality_flags[table] = do_qc_individual_observation(
            data_dict_qc[table],
            table,
            quality_flags[table],
            params,
            ext_path,
            i=i,
            j=j,
            k=k,
        )

        # Remove already failed quality_flags
        drop_invalid_indexes(data_dict_qc[table], quality_flags[table], 1)

        k += 1
        print(f"After individual {table} QC")
        print(table, ": ", quality_flags[table].value_counts().to_dict())

    quality_flags = do_qc_individual_combined(
        data_dict_qc,
        quality_flags,
        params,
        ext_path,
        i=i,
        j=j,
        k=k,
    )
    print("After combined individual QC")
    for table in obs_tables:
        print(table, ": ", quality_flags[table].value_counts().to_dict())

    # Do sequential observations checks
    j += 1
    k = 1
    logging.info(f"{i}.{j}. Do sequential observations checks")

    for table in obs_tables:

        quality_flags[table] = do_qc_sequential_observation(
            data_dict_qc[table],
            table,
            quality_flags[table],
            idx_gnrc,
            data_dict_qc["header"],
            params,
            i=i,
            j=j,
            k=k,
        )

        # Remove already failed quality_flags
        drop_invalid_indexes(data_dict_qc[table], quality_flags[table], 1)

        k += 1
        print(f"After sequential {table} QC")
        print(table, ": ", quality_flags[table].value_counts().to_dict())

    quality_flags = do_qc_sequential_combined(
        data_dict_qc,
        quality_flags,
        idx_gnrc,
        params,
        i=i,
        j=j,
        k=k,
    )
    for table in obs_tables:
        print(table, ": ", quality_flags[table].value_counts().to_dict())
    # Do grouped observations checks
    j += 1
    k = 1
    logging.info(f"{i}.{j}. Do grouped observations checks")

    for table in obs_tables:

        quality_flags[table] = do_qc_grouped_observation(
            data_dict_qc[table],
            table,
            quality_flags[table],
            params,
            ext_path,
            i=i,
            j=j,
            k=k,
        )

        # Remove already failed quality_flags
        drop_invalid_indexes(data_dict_qc[table], quality_flags[table], 1)

        k += 1
        print(f"After individual {table} QC")
        print(table, ": ", quality_flags[table].value_counts().to_dict())

    return report_quality, location_quality, report_time_quality, quality_flags, history
