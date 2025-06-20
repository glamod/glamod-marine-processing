"""Module containing base QC which call multiple QC functions and could be applied on a DataBundle."""

from __future__ import annotations

import inspect
from typing import Literal

import pandas as pd

from .auxiliary import failed, passed, untested
from .external_clim import get_climatological_value  # noqa
from .next_level_qc import (  # noqa
    do_climatology_check,
    do_date_check,
    do_day_check,
    do_hard_limit_check,
    do_missing_value_check,
    do_missing_value_clim_check,
    do_position_check,
    do_sst_freeze_check,
    do_supersaturation_check,
    do_time_check,
    do_wind_consistency_check,
)


def _get_function(name):
    func = globals().get(name)
    if not callable(func):
        raise NameError(f"Function '{name}' is not defined.")
    return func


def _is_func_param(func, param):
    sig = inspect.signature(func)
    if "kwargs" in sig.parameters:
        return True
    return param in sig.parameters


def _get_requests_from_params(params, func, data):
    requests = {}
    if params is None:
        return requests
    for param, cname in params.items():
        if not _is_func_param(func, param):
            raise ValueError(
                f"Parameter '{param}' is not a valid parameter of function '{func.__name__}'"
            )
        if cname not in data:
            raise NameError(
                f"Variable '{cname}' is not available in input data: {data}."
            )
        requests[param] = data[cname]
    return requests


def do_multiple_row_check(
    data: dict | pd.Series,
    qc_dict: dict | None = None,
    preproc_dict: dict | None = None,
    return_method: Literal["all", "passed", "failed"] = "all",
) -> pd.Series:
    """Basic row-by-row QC by using multiple QC functions.

    Parameters
    ----------
    data : dict or pd.Series
        Hashable input data.
    qc_dict : dict, optional
        Nested QC dictionary.
        Keys represent arbitrary names of the check.
        The values are dictionaries which contain the keys "func" (name of the QC function),
        "names" (input data names as keyword arguments, that will be retrieved from `data`) and,
        if necessary, "arguments" (the corresponding keyword arguments).
        For more information see Examples.
    preproc_dict : dict, optional
        Nested pre-processing dictionary.
        Keys represent variable names that can be used by `qc_dict`.
        The values are dictionaries which contain the keys "func" (name of the pre-processing function),
        "names" (input data names as keyword arguments, that will be retrieved from `data`), and "inputs"
        (list of input-given variables).
        For more information see Examples.
    return_method: {"all", "passed", "failed"}, default: "all"
        If "all", return QC dictionary containing all requested QC check flags.
        If "passed": return QC dictionary containing all requested QC check flags until the first check passes.
        Other QC checks are flagged as unstested (3).
        If "failed": return QC dictionary containing all requested QC check flags until the first check fails.
        Other QC checks are flagged as unstested (3).

    Returns
    -------
    pd.Series
        Columns represent arbitrary names of the check (taken from `qc_dict.keys()`).
        Values representing corresponding QC flags.
        For information to QC flags see QC functions.

    Raises
    ------
    NameError
        If a function listed in `qc_dict` or `preproc_dict` is not defined.
        If columns listed in `qc_dict` or `preproc_dict` are not available in `data`.
    ValueError
        If `return_method` is not one of ["all", "passed", "failed"]
        If variable names listed in `qc_dict` or `preproc_dict` are not valid parameters of the QC function.

    Notes
    -----
    If a variable is pre-processed using `preproc_dict`, mark the variable name as "__preprocessed__" in `qc_dict`.
    E.g. `"climatology": "__preprocessed__"`.

    For more information, see Examples.

    Examples
    --------
    An example `qc_dict` for a hard limit test:

    .. code-block:: python

        qc_dict = {
            "hard_limits_check": {
                "func": "do_air_temperature_hard_limit_check",
                "names": "ATEMP",
                "arguments": {"hard_limits": [193.15, 338.15]},
            }
        }

    An example `qc_dict` for a climatology test. Variable "climatology" was previously defined:

    .. code-block:: python

        qc_dict = {
            "climatology_check": {
                "func": "do_climatology_check",
                "names": {
                    "value": "observation_value",
                    "lat": "latitude",
                    "lon": "longitude",
                    "date": "date_time",
                },
                "arguments": {
                    "climatology": climatology,
                    "maximum_anomaly": 10.0,  # K
                },
            },
        }

    An example `preproc_dict` for extracting a climatological value:

    .. code-block:: python

        preproc_dict = {
            "func": "get_climatological_value",
            "names": {
                "lat": "latitude",
                "lon": "longitude",
                "date": "date_time",
            },
            "inputs": climatology,
        }

    Make use of both dictionaries:

    .. code-block:: python

        preproc_dict = {
            "func": "get_climatological_value",
            "names": {
                "lat": "latitude",
                "lon": "longitude",
                "date": "date_time",
            },
            "inputs": climatology,
        }

        qc_dict = {
            "climatology_check": {
                "func": "do_climatology_check",
                "names": {
                    "value": "observation_value",
                },
                "arguments": {
                    "climatology": "__preprocessed__",
                    "maximum_anomaly": 10.0,  # K
                },
            },
        }

    """
    if return_method not in ["all", "passed", "failed"]:
        raise ValueError(
            f"'return_method' has to be one of ['all', 'passed', 'failed']: {return_method}"
        )

    if qc_dict is None:
        qc_dict = {}

    if preproc_dict is None:
        preproc_dict = {}

    # Firstly, check if all functions are callable and all requested input variables are available!
    preprocessed = {}
    for var_name, preproc_params in preproc_dict.items():
        func_name = preproc_params.get("func")
        func = _get_function(func_name)

        requests = _get_requests_from_params(preproc_params.get("names"), func, data)

        inputs = preproc_params.get("inputs")
        if not isinstance(inputs, list):
            inputs = [inputs]

        preprocessed[var_name] = func(*inputs, **requests)

    qc_inputs = {}
    for qc_name, qc_params in qc_dict.items():
        func_name = qc_params.get("func")
        func = _get_function(func_name)
        requests = _get_requests_from_params(qc_params.get("names"), func, data)

        qc_inputs[qc_name] = {}
        qc_inputs[qc_name]["function"] = func
        qc_inputs[qc_name]["requests"] = requests
        qc_inputs[qc_name]["kwargs"] = {}
        if "arguments" in qc_params.keys():
            arguments = {}
            for k, v in qc_params["arguments"].items():
                if v == "__preprocessed__":
                    v = preprocessed[k]
                arguments[k] = v
            qc_inputs[qc_name]["kwargs"] = arguments

    results = pd.Series()
    finished = False
    for qc_name, qc_params in qc_inputs.items():
        if finished is True:
            results[qc_name] = untested
            continue
        results[qc_name] = qc_params["function"](
            **qc_params["requests"], **qc_params["kwargs"]
        )
        if (results[qc_name] == failed and return_method == "failed") or (
            results[qc_name] == passed and return_method == "passed"
        ):
            finished = True
    return results
