"""Module containing base QC which call multiple QC functions and could be applied on a DataBundle."""

from __future__ import annotations

import pandas as pd

from .next_level_qc import (  # noqa
    do_anomaly_check,
    do_climatology_plus_stdev_check,
    do_date_check,
    do_day_check,
    do_hard_limit_check,
    do_missing_value_check,
    do_no_normal_check,
    do_position_check,
    do_sst_freeze_check,
    do_supersaturation_check,
    do_time_check,
    do_wind_consistency_check,
)
from .qc import failed


def do_multiple_row_qc(data: dict | pd.Series, qc_dict: dict = {}) -> int:
    """Basic roy-by-row QC.

    Parameters
    ----------
    data: dict or pd.Series
        Hashable input data.
    qc_dict: dict
        Nested dictionary. Keys represent QC function names.
        The values are dictionaries which contain the keys "names" (hashable input data names)
        and if necessary "arguments" (the corresponding keyword arguments).

    Returns
    -------
    int
        1 if QC fails, otherwise 0

    Example
    -------
    An example `qc_dict`:

    .. code-block:: python

        qc_dict = {
            "do_air_temperature_hard_limit_check": {
                "names": "ATEMP",
                "arguments": {"hard_limits": [193.15, 338.15]},
            }
        }


    Note
    ----
    This function loops over each key-value pair. If one QC function fails, this function returns 1 and breaks the looping.
    """

    def get_function(name):
        return globals().get(name)

    # Firstly, check if all functions are callable and all requested input variables are available!
    qc_inputs = {}
    for qc_function, qc_params in qc_dict.items():
        func = get_function(qc_function)
        if not callable(func):
            raise NameError(f"Function '{qc_function}' is not defined.")

        requests = []
        for name in qc_params["names"]:
            if name not in data:
                raise NameError(
                    f"Variable '{name}' is not available in input data: {data}."
                )
            requests.append(data[name])

        qc_inputs[qc_function] = {}
        qc_inputs[qc_function]["function"] = func
        qc_inputs[qc_function]["requests"] = requests
        qc_inputs[qc_function]["kwargs"] = qc_params["arguments"]

    for qc_function, qc_params in qc_inputs.items():
        qc_flag = qc_function(*qc_params["requests"], **qc_params["kwargs"])
        if qc_flag == failed:
            return qc_flag

    return qc_flag


# def do_base_mat_qc(at, parameters):
#     """Run the base MAT QC checks, non-missing, climatology check and check for normal etc."""
#     # I think this should return a boolean value, isn't it?
#     assert "maximum_anomaly" in parameters
#
#     self.set_qc("AT", "noval", qc.value_check(self.getvar("AT")))
#     self.set_qc(
#         "AT",
#         "clim",
#         qc.climatology_check(
#             self.getvar("AT"), self.getnorm("AT"), parameters["maximum_anomaly"]
#         ),
#     )
#     self.set_qc("AT", "nonorm", qc.no_normal_check(self.getnorm("AT")))
#     self.set_qc(
#         "AT",
#         "hardlimit",
#         qc.hard_limit(self.getvar("AT"), parameters["hard_limits"]),
#     )

# def do_base_dpt_qc(dpt, parameters):
#     """
#     Run the base DPT checks, non missing, modified climatology check, check for normal,
#     supersaturation etc.
#     """
#     # I think this should return a boolean value, isn't it?
#     self.set_qc(
#         "DPT",
#         "clim",
#         qc.climatology_plus_stdev_check(
#             self.getvar("DPT"),
#             self.getnorm("DPT"),
#             self.getnorm("DPT", "stdev"),
#             parameters["minmax_standard_deviation"],
#             parameters["maximum_standardised_anomaly"],
#         ),
#     )
#
#     self.set_qc("DPT", "noval", qc.value_check(self.getvar("DPT")))
#     self.set_qc("DPT", "nonorm", qc.no_normal_check(self.getnorm("DPT")))
#     self.set_qc(
#         "DPT", "ssat", qc.supersat_check(self.getvar("DPT"), self.getvar("AT2"))
#     )

# def do_base_sst_qc(sst, parameters):
#     """
#     Run the base SST QC checks, non-missing, above freezing, climatology check
#     and check for normal
#     """
#     # I think this should return a boolean value, isn't it?
#     assert "freezing_point" in parameters
#     assert "freeze_check_n_sigma" in parameters
#     assert "maximum_anomaly" in parameters
#
#     self.set_qc("SST", "noval", qc.value_check(self.getvar("SST")))
#
#     self.set_qc(
#         "SST",
#         "freez",
#         qc.sst_freeze_check(
#             self.getvar("SST"),
#             0.0,
#             parameters["freezing_point"],
#             parameters["freeze_check_n_sigma"],
#         ),
#     )
#
#     self.set_qc(
#         "SST",
#         "clim",
#         qc.climatology_check(
#             self.getvar("SST"), self.getnorm("SST"), parameters["maximum_anomaly"]
#         ),
#     )
#
#     self.set_qc("SST", "nonorm", qc.no_normal_check(self.getnorm("SST")))
#     self.set_qc(
#         "SST",
#         "hardlimit",
#         qc.hard_limit(self.getvar("SST"), parameters["hard_limits"]),
#     )

"""do base wind qc replaced by preceding three functions"""
# def do_base_wind_qc(ws, parameters):
#     """Run the base Wind speed QC checks."""
#     self.set_qc("W", "noval", qc.value_check(self.getvar("W")))
#     self.set_qc(
#         "W", "hardlimit", qc.hard_limit(self.getvar("W"), parameters["hard_limits"])
#     )
#     self.set_qc(
#         "W",
#         "consistency",
#         qc.wind_consistency(
#             self.getvar("W"), self.getvar("D"), parameters["variable_limit"]
#         ),
#     )


"""Only one QC check from do_kate_mat_qc was unique to the function so I added it to air temperature checks above"""


# def do_kate_mat_qc(at, parameters):
#     """
#     Kate's modified MAT checks, non missing, modified climatology check, check for normal etc.
#     Has a mix of AT and AT2 because we want to keep two sets of climatologies and checks for humidity
#     """
#     # I think this should return a boolean value, isn't it?
#     # What is AT and AT2?
#     self.set_qc(
#         "AT2",
#         "clim",
#         qc.climatology_plus_stdev_check(
#             self.getvar("AT2"),
#             self.getnorm("AT2"),
#             self.getnorm("AT2", "stdev"),
#             parameters["minmax_standard_deviation"],
#             parameters["maximum_standardised_anomaly"],
#         ),
#     )
#
#     self.set_qc("AT2", "noval", qc.value_check(self.getvar("AT2")))
#     self.set_qc("AT2", "nonorm", qc.no_normal_check(self.getnorm("AT2")))
#     self.set_qc(
#         "AT2",
#         "hardlimit",
#         qc.hard_limit(self.getvar("AT"), parameters["hard_limits"]),
#     )


# def perform_base_qc(pt, latitude, longitude, timestamp, parameters):
#     """
#     Run all the base QC checks on the header file (CDM).
#     """
#     # If one of those checks is missing we break. Is this reasonable to you?
#
#     # self.do_fix_missing_hour()  # this should already be fixed while mapping to the CDM
#
#     if is_buoy(pt):
#         return "2"  # not checked, since we have no QC for buoys?
#
#     if not is_ship(pt):
#         return "2"  # not checked, since we have a QC for ships only?
#
#     if is_deck_780():
#         return "?"  # I have no idea what do do here
#
#     # Should we filter buoy, ship, deck_780 before this routine?
#     # I think this is too ICOADS-specific, isn't it?
#
#     if not do_position_check(latitude, longitude):
#         return "1"  # failed
#
#     if not do_date_check(year=timestamp.year, month=timestamp.month, day=timestamp.day):
#         return "1"  # failed
#
#     if not do_time_check(timestamp.hour):
#         return "1"  # failed
#
#     do_blacklist()  # I have no idea what do do here
#
#     is_day = do_day_check(
#         parameters["base"]["time_since_sun_above_horizon"]
#     )  # maybe we need this variable afterwards
#
#
# def perform_obs_qc(
#     at=None, dpt=None, slp=None, sst=None, wbt=None, wd=None, ws=None, parameters={}
# ):
#     """Run all the base QC checks on the obsevation files (CDM)."""
#
#     humidity_blacklist()
#     mat_blacklist()
#     wind_blacklist()
#
#     # Should we do those blacklisting before this routine?
#     # Maybe as extra parameters of this function: do_humidity_qc, do_mat_qc, do_wind_qc?
#
#     if at is not None:
#         return do_base_mat_qc(at, parameters)
#         # How should we implement this: self.do_kate_mat_qc(parameters["AT"]) ??
#
#     if dpt is not None:
#         return do_base_dpt_qc(dpt, parameters)
#
#     if slp is not None:
#         return do_base_slp_qc(slp, parameters)
#
#     if sst is not None:
#         return do_base_sst_qc(sst, parameters)
#
#     if ws is not None:  # I think "W" is "WS" in the CDM.
#         return do_base_wind_qc(ws, parameters)
#
#     # special check for silly values in all humidity-related variables
#     # and set DPT hardlimit flag if necessary
#     # How to implement this?
#     self.set_qc("DPT", "hardlimit", 0)
#     for var in ["AT", "DPT", "SHU", "RH"]:
#         if qc.hard_limit(self.getvar(var), parameters[var]["hard_limits"]) == 1:
#             self.set_qc("DPT", "hardlimit", 1)


# def do_base_qc_header(
#     list_of_parameters_we_need, do_first_step=False, do_last_step=False
# ):
#     """Basic row QC for header file.
#
#     Since we have only one QC flag in the header file:
#
#     report_quality
#     https://glamod.github.io/cdm-obs-documentation/tables/code_tables/quality_flag/quality_flag.html
#
#     we return "1" (failed) if one test fails.
#     """
#     if do_first_step is True:
#         flag = first_function(some_of_the_list_of_parameters_we_need)
#
#     if flag == "1":
#         return flag
#
#     if do_last_step is True:
#         flag = last_function(some_of_the_list_of_parameters_we_need)
#
#     return flag
#
#
# def do_base_qc_at(list_of_parameters_we_need, do_first_step=False, do_last_step=False):
#     """Basic row QC for observation file.
#
#     See do_base_qc_header
#
#     We copy and adjust thgis function for each observation value (sst, slp, wbt, wd, ws)
#     """
#     return
