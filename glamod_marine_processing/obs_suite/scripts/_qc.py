"""Quality control for observation suite."""

from __future__ import annotations

import logging


class QualityControl:
    """Class for quality control."""

    def __init__(self, wind_speed, wind_direction):
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction


def wind_qc(table_wd, table_ws):
    """Wind Quality Control function.

    Note:
    * northerlies given as 360°
    * calm winds given as 0°

    Flags:
    * negative wind speeds
    * wind speeds above 99.9 m/s
    * negative wind directions
    * wrapped directions (> 360°)
    * no wind speeds but wind directions
    * no wind directions but wind speeds
    """
    if len(table_wd) == 0:
        logging.warning(
            "No wind direction QC is possible since table is empty or non exisisting table."
        )
    else:
        value_wd = table_wd["observation_value"].astype(float)
        table_wd["quality_flag"] = table_wd["quality_flag"].mask(
            (value_wd < 0.0) | (value_wd > 360.0),
            "1",
        )
    if len(table_ws) == 0:
        logging.warning(
            "No wind speed QC is possible since table is empty or non exisisting table."
        )
    else:
        value_ws = table_ws["observation_value"].astype(float)
        table_ws["quality_flag"] = table_ws["quality_flag"].mask(
            (value_ws < 0.0) | (value_ws > 99.9),
            "1",
        )
    if len(table_wd) == 0 and len(table_ws) == 0:
        logging.warning(
            "No wind QC cross checks are possible since tables are empty or non exisisting table."
        )
    else:
        masked = (value_ws == 0.0) & (value_wd != 0)
        table_wd["quality_flag"] = table_wd["quality_flag"].mask(masked, "1")
        table_ws["quality_flag"] = table_ws["quality_flag"].mask(masked, "1")
        masked = (value_ws != 0.0) & (value_wd == 0)
        table_wd["quality_flag"] = table_wd["quality_flag"].mask(masked, "1")
        table_ws["quality_flag"] = table_ws["quality_flag"].mask(masked, "1")

    return QualityControl(table_ws, table_wd)
