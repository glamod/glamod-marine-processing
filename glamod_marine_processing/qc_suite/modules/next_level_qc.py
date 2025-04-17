"""Module containing main QC functions which could be applied on a DataBundle."""

from __future__ import annotations

from . import qc

# This should be the raw structure.
# In general, I think, we do not need to set qc flags, we just return them (no self.set_qc)
# I hop I did not forget anything.


def is_buoy(pt):
    """
    Identify whether report is from a moored or drifting buoy based
    on ICOADS platform type PT. Set additional flag to pick out drifters only
    """
    # Do we need this function?
    # Where/Why do we need "isbuoy" and "isdrifter"?
    # I think this function should return a boolean value, isn't it?
    # I think we should use the CDM platform table?
    # https://glamod.github.io/cdm-obs-documentation/tables/code_tables/platform_type/platform_type.html
    if pt in [6, 7]:
        self.set_qc("POS", "isbuoy", 1)
    else:
        self.set_qc("POS", "isbuoy", 0)

    if pt == 7:
        self.set_qc("POS", "isdrifter", 1)
    else:
        self.set_qc("POS", "isdrifter", 0)


def is_ship(pt):
    """
    Identify whether report is from a ship based
    on ICOADS platform type PT
    """
    # Do we need this function?
    # I think this function should return a boolean value, isn't it?
    # I think we should use the CDM platform table?
    # https://glamod.github.io/cdm-obs-documentation/tables/code_tables/platform_type/platform_type.html
    if pt in [0, 1, 2, 3, 4, 5, 10, 11, 12, 17]:
        self.set_qc("POS", "isship", 1)
    else:
        self.set_qc("POS", "isship", 0)


def is_deck_780():
    """Identify obs that are from ICOADS Deck 780 which consists of obs from WOD."""
    # Do we need this function?
    # Where/Why do we need "is780"?
    # I think this function should return a boolean value, isn't it?
    # We do not have this information explicitly in the CDM.
    if self.getvar("DCK") == 780:
        self.set_qc("POS", "is780", 1)
    else:
        self.set_qc("POS", "is780", 0)


def do_position_check(latitude, longitude):
    """Perform the positional QC check on the report."""
    # I think this function should return a boolean value, isn't it?
    # maybe return qc.position_check(latitude, longitude)
    self.set_qc("POS", "pos", qc.position_check(latitude, longitude))


def do_date_check(year, month, day):
    """Perform the date QC check on the report."""
    # Do we need this function?
    # I think this function should return a boolean value, isn't it?
    # maybe return qc.date_check(latitude, longitude)
    # This should already be done while mapping to the CDM.
    self.set_qc(
        "POS",
        "date",
        qc.date_check(year, month, day),
    )


def do_time_check(hour):
    """Perform the time QC check on the report."""
    # See do_date_check
    self.set_qc("POS", "time", qc.time_check(hour))


def do_blacklist():
    """Do basic blacklisting on the report."""
    # Why is this needed?
    self.set_qc(
        "POS",
        "blklst",
        qc.blacklist(
            self.getvar("ID"),
            self.getvar("DCK"),
            self.getvar("YR"),
            self.getvar("MO"),
            self.lat(),
            self.lon(),
            self.getvar("PT"),
        ),
    )


def do_day_check(time_since_sun_above_horizon):
    """Set the day/night flag on the report."""
    if (
        self.get_qc("POS", "pos") == 0
        and self.get_qc("POS", "date") == 0
        and self.get_qc("POS", "time") == 0
    ):
        self.set_qc(
            "POS",
            "day",
            qc.day_test(
                self.getvar("YR"),
                self.getvar("MO"),
                self.getvar("DY"),
                self.getvar("HR"),
                self.lat(),
                self.lon(),
                time_since_sun_above_horizon,
            ),
        )
    else:
        self.set_qc("POS", "day", 1)


def humidity_blacklist(self):
    """Flag certain sources as ineligible for humidity QC."""
    self.set_qc("DPT", "hum_blacklist", 0)
    if self.getvar("PT") in [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 15]:
        self.set_qc("DPT", "hum_blacklist", 0)
    else:
        self.set_qc("DPT", "hum_blacklist", 1)


def mat_blacklist(self):
    """
    Flag certain decks, areas and other sources as ineligible for MAT QC.
    These exclusions are based on Kent et al. HadNMAT2 paper and include
    Deck 780 which is oceanographic data and the North Atlantic, Suez,
    Indian Ocean area in the 19th Century.
    """
    # See Kent et al. HadNMAT2 QC section
    self.set_qc("AT", "mat_blacklist", 0)

    if self.getvar("PT") == 5 and self.getvar("DCK") == 780:
        self.set_qc("AT", "mat_blacklist", 1)

    # make sure lons are in range -180 to 180
    lon = self.lon()
    lat = self.lat()
    # North Atlantic, Suez and indian ocean to be excluded from MAT processing
    if (
        self.getvar("DCK") == 193
        and 1880 <= self.getvar("YR") <= 1892
        and (
            (-80.0 <= lon <= 0.0 and 40.0 <= lat <= 55.0)
            or (-10.0 <= lon <= 30.0 and 35.0 <= lat <= 45.0)
            or (15.0 <= lon <= 45.0 and -10.0 <= lat <= 40.0)
            or (15.0 <= lon <= 95.0 and lat >= -10.0 and lat <= 15.0)
            or (95.0 <= lon <= 105.0 and -10.0 <= lat <= 5.0)
        )
    ):
        self.set_qc("AT", "mat_blacklist", 1)


def wind_blacklist(self):
    """Flag certain sources as ineligible for wind QC. Based on Shawn Smith's list."""
    self.set_qc("W", "wind_blacklist", 0)

    if self.getvar("DCK") in [708, 780]:
        self.set_qc("W", "wind_blacklist", 1)

    pass


def do_base_mat_qc(at, parameters):
    """Run the base MAT QC checks, non-missing, climatology check and check for normal etc."""
    # I think this should return a boolean value, isn't it?
    assert "maximum_anomaly" in parameters

    self.set_qc("AT", "noval", qc.value_check(self.getvar("AT")))
    self.set_qc(
        "AT",
        "clim",
        qc.climatology_check(
            self.getvar("AT"), self.getnorm("AT"), parameters["maximum_anomaly"]
        ),
    )
    self.set_qc("AT", "nonorm", qc.no_normal_check(self.getnorm("AT")))
    self.set_qc(
        "AT",
        "hardlimit",
        qc.hard_limit(self.getvar("AT"), parameters["hard_limits"]),
    )


def do_base_dpt_qc(dpt, parameters):
    """
    Run the base DPT checks, non missing, modified climatology check, check for normal,
    supersaturation etc.
    """
    # I think this should return a boolean value, isn't it?
    self.set_qc(
        "DPT",
        "clim",
        qc.climatology_plus_stdev_check(
            self.getvar("DPT"),
            self.getnorm("DPT"),
            self.getnorm("DPT", "stdev"),
            parameters["minmax_standard_deviation"],
            parameters["maximum_standardised_anomaly"],
        ),
    )

    self.set_qc("DPT", "noval", qc.value_check(self.getvar("DPT")))
    self.set_qc("DPT", "nonorm", qc.no_normal_check(self.getnorm("DPT")))
    self.set_qc(
        "DPT", "ssat", qc.supersat_check(self.getvar("DPT"), self.getvar("AT2"))
    )


def do_base_slp_qc(self, parameters):
    """Run the base SLP QC checks, non-missing, climatology check and check for normal."""
    # I think this should return a boolean value, isn't it?
    assert "maximum_anomaly" in parameters
    self.set_qc("SLP", "noval", qc.value_check(self.getvar("SLP")))
    self.set_qc(
        "SLP",
        "clim",
        qc.climatology_plus_stdev_with_lowbar(
            self.getvar("SLP"),
            self.getnorm("SLP"),
            self.getnorm("SLP", "stdev"),
            parameters["maximum_standardised_anomaly"],
            parameters["lowbar"],
        ),
    )
    #        self.set_qc('SLP', 'clim', qc.climatology_check(self.getvar('SLP'), self.getnorm('SLP'),
    #                                                        parameters['maximum_anomaly']))
    self.set_qc("SLP", "nonorm", qc.no_normal_check(self.getnorm("SLP")))


def do_base_sst_qc(sst, parameters):
    """Run the base SST QC checks, non-missing, above freezing, climatology check and check for normal."""
    # I think this should return a boolean value, isn't it?
    assert "freezing_point" in parameters
    assert "freeze_check_n_sigma" in parameters
    assert "maximum_anomaly" in parameters

    self.set_qc("SST", "noval", qc.value_check(self.getvar("SST")))

    self.set_qc(
        "SST",
        "freez",
        qc.sst_freeze_check(
            self.getvar("SST"),
            0.0,
            parameters["freezing_point"],
            parameters["freeze_check_n_sigma"],
        ),
    )

    self.set_qc(
        "SST",
        "clim",
        qc.climatology_check(
            self.getvar("SST"), self.getnorm("SST"), parameters["maximum_anomaly"]
        ),
    )

    self.set_qc("SST", "nonorm", qc.no_normal_check(self.getnorm("SST")))
    self.set_qc(
        "SST",
        "hardlimit",
        qc.hard_limit(self.getvar("SST"), parameters["hard_limits"]),
    )


def do_base_wind_qc(ws, parameters):
    """Run the base Wind speed QC checks."""
    self.set_qc("W", "noval", qc.value_check(self.getvar("W")))
    self.set_qc(
        "W", "hardlimit", qc.hard_limit(self.getvar("W"), parameters["hard_limits"])
    )
    self.set_qc(
        "W",
        "consistency",
        qc.wind_consistency(
            self.getvar("W"), self.getvar("D"), parameters["variable_limit"]
        ),
    )


def do_kate_mat_qc(at, parameters):
    """
    Kate's modified MAT checks, non missing, modified climatology check, check for normal etc.
    Has a mix of AT and AT2 because we want to keep two sets of climatologies and checks for humidity
    """
    # I think this should return a boolean value, isn't it?
    # What is AT and AT2?
    self.set_qc(
        "AT2",
        "clim",
        qc.climatology_plus_stdev_check(
            self.getvar("AT2"),
            self.getnorm("AT2"),
            self.getnorm("AT2", "stdev"),
            parameters["minmax_standard_deviation"],
            parameters["maximum_standardised_anomaly"],
        ),
    )

    self.set_qc("AT2", "noval", qc.value_check(self.getvar("AT2")))
    self.set_qc("AT2", "nonorm", qc.no_normal_check(self.getnorm("AT2")))
    self.set_qc(
        "AT2",
        "hardlimit",
        qc.hard_limit(self.getvar("AT"), parameters["hard_limits"]),
    )


def perform_base_qc(pt, latitude, longitude, timestamp, parameters):
    """Run all the base QC checks on the header file (CDM)."""
    # If one of those checks is missing we break. Is this reasonable to you?

    # self.do_fix_missing_hour()  # this should already be fixed while mapping to the CDM

    if is_buoy(pt):
        return "2"  # not checked, since we have no QC for buoys?

    if not is_ship(pt):
        return "2"  # not checked, since we have a QC for ships only?

    if is_deck_780():
        return "?"  # I have no idea what do do here

    # Should we filter buoy, ship, deck_780 before this routine?
    # I think this is too ICOADS-specific, isn't it?

    if not do_position_check(latitude, longitude):
        return "1"  # failed

    if not do_date_check(year=timestamp.year, month=timestamp.month, day=timestamp.day):
        return "1"  # failed

    if not do_time_check(timestamp.hour):
        return "1"  # failed

    do_blacklist()  # I have no idea what do do here

    is_day = do_day_check(
        parameters["base"]["time_since_sun_above_horizon"]
    )  # do we need this variable afterwards ?


def perform_obs_qc(
    at=None, dpt=None, slp=None, sst=None, wbt=None, wd=None, ws=None, parameters={}
):
    """Run all the base QC checks on the obsevation files (CDM)."""
    humidity_blacklist()
    mat_blacklist()
    wind_blacklist()

    # Should we do those blacklisting before this routine?
    # Maybe as extra parameters of this function: do_humidity_qc, do_mat_qc, do_wind_qc?

    if at is not None:
        return do_base_mat_qc(at, parameters)
        # How should we implement this: self.do_kate_mat_qc(parameters["AT"]) ??

    if dpt is not None:
        return do_base_dpt_qc(dpt, parameters)

    if slp is not None:
        return do_base_slp_qc(slp, parameters)

    if sst is not None:
        return do_base_sst_qc(sst, parameters)

    if wbt is not None:
        return "3"  # not checked

    if wd is not None:
        return "3"  # not checked

    if ws is not None:  # I think "W" is "WS" in the CDM.
        return do_base_wind_qc(ws, parameters)

    # special check for silly values in all humidity-related variables
    # and set DPT hardlimit flag if necessary
    # How to implement this?
    self.set_qc("DPT", "hardlimit", 0)
    for var in ["AT", "DPT", "SHU", "RH"]:
        if qc.hard_limit(self.getvar(var), parameters[var]["hard_limits"]) == 1:
            self.set_qc("DPT", "hardlimit", 1)
