"""Module containing ICOADS-specific blacklisting functions."""

from __future__ import annotations

from .auxiliary import isvalid
from .qc import failed, passed


def do_blacklist(
    id: str,
    deck: int,
    year: int,
    month: int,
    latitude: float,
    longitude: float,
    platform_type: int,
) -> int:
    """
    Do basic blacklisting on the report. The blacklist is used to remove data that are known to be bad
    and shouldn't be passed to the QC.

    If the report is from Deck 732, compares the observations year and location to a table of pre-identified
    regions in which Deck 732 observations are known to be dubious - see Rayner et al. 2006 and Kennedy et al.
    2011b. Observations at 0 degrees latitude 0 degrees longitude are blacklisted as this is a common error.
    C-MAN stations with platform type 13 are blacklisted. SEAS data from deck 874 are unreliable (SSTs were
    often in excess of 50degC) and so the whole deck was removed from processing.

    Parameters
    ----------
    id : str
        ID of the report
    deck : int
        Deck of the report
    year : int
        Year of the report
    month : int
        Month of the report (1-12)
    latitude: float
        Latitude of the report
    longitude : float
        Longitude of the report
    platform_type : int
        Platform type of report

    Returns
    -------
    int
        1 if the report is blacklisted, 0 otherwise
    """
    # Fold longitudes into ICOADS range
    if longitude > 180.0:
        longitude -= 360

    if latitude == 0.0 and longitude == 0.0:
        return failed  # blacklist all obs at 0,0 as this is a common error.

    if isvalid(platform_type) and platform_type == 13:
        return failed  # C-MAN data - we do not want coastal stations

    if id == "SUPERIGORINA":
        return failed

    # these are the definitions of the regions which are blacklisted for Deck 732
    region = {
        1: [-175, 40, -170, 55],
        2: [-165, 40, -160, 60],
        3: [-145, 40, -140, 50],
        4: [-140, 30, -135, 40],
        5: [-140, 50, -130, 55],
        6: [-70, 35, -60, 40],
        7: [-50, 45, -40, 50],
        8: [5, 70, 10, 80],
        9: [0, -10, 10, 0],
        10: [-30, -25, -25, -20],
        11: [-60, -50, -55, -45],
        12: [75, -20, 80, -15],
        13: [50, -30, 60, -20],
        14: [30, -40, 40, -30],
        15: [20, 60, 25, 65],
        16: [0, -40, 10, -30],
        17: [-135, 30, -130, 40],
    }

    # this dictionary contains the regions that are to be excluded for this year
    year_to_regions = {
        1958: [1, 2, 3, 4, 5, 6, 14, 15],
        1959: [1, 2, 3, 4, 5, 6, 14, 15],
        1960: [1, 2, 3, 5, 6, 9, 14, 15],
        1961: [1, 2, 3, 5, 6, 14, 15, 16],
        1962: [1, 2, 3, 5, 12, 13, 14, 15, 16],
        1963: [1, 2, 3, 5, 6, 12, 13, 14, 15, 16],
        1964: [1, 2, 3, 5, 6, 12, 13, 14, 16],
        1965: [1, 2, 6, 10, 12, 13, 14, 15, 16],
        1966: [1, 2, 6, 9, 14, 15, 16],
        1967: [1, 2, 5, 6, 9, 14, 15],
        1968: [1, 2, 3, 5, 6, 9, 14, 15],
        1969: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15, 16],
        1970: [1, 2, 3, 4, 5, 6, 8, 9, 14, 15],
        1971: [1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 14, 16],
        1972: [4, 7, 8, 9, 10, 11, 13, 16, 17],
        1973: [4, 7, 8, 10, 11, 13, 16, 17],
        1974: [4, 7, 8, 10, 11, 16, 17],
    }

    if deck == 732:
        if year in year_to_regions:
            regions_to_check = year_to_regions[year]
            for regid in regions_to_check:
                thisreg = region[regid]
                if (
                    thisreg[0] <= longitude <= thisreg[2]
                    and thisreg[1] <= latitude <= thisreg[3]
                ):
                    return failed

    if deck == 874:
        return failed  # SEAS data gets blacklisted

    # For a short period, observations from drifting buoys with these IDs had very erroneous values in the
    # Tropical Pacific. These were identified offline and added to the blacklist
    if (
        (year == 2005 and month == 11)
        or (year == 2005 and month == 12)
        or (year == 2006 and month == 1)
    ):
        if id in [
            "53521    ",
            "53522    ",
            "53566    ",
            "53567    ",
            "53568    ",
            "53571    ",
            "53578    ",
            "53580    ",
            "53582    ",
            "53591    ",
            "53592    ",
            "53593    ",
            "53594    ",
            "53595    ",
            "53596    ",
            "53599    ",
            "53600    ",
            "53601    ",
            "53602    ",
            "53603    ",
            "53604    ",
            "53605    ",
            "53606    ",
            "53607    ",
            "53608    ",
            "53609    ",
            "53901    ",
            "53902    ",
        ]:
            return failed

    return passed


def do_humidity_blacklist(platform_type: int) -> int:
    """
    Flag certain sources as ineligible for humidity QC.

    Parameters
    ----------
    platform_type : int
        Platform type of report

    Returns
    -------
    int
        Return 1 if report is ineligible for humidity QC, otherwise 0.
    """
    if platform_type in [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 15]:
        return passed
    else:
        return failed


def do_mat_blacklist(
    platform_type: int,
    deck: int,
    latitude: float,
    longitude: float,
    year: int,
) -> int:
    """
    Flag certain decks, areas and other sources as ineligible for MAT QC.

    These exclusions are based on Kent et al. HadNMAT2 paper and include
    Deck 780 which is oceanographic data and the North Atlantic, Suez,
    Indian Ocean area in the 19th Century.

    Parameters
    ----------
    platform_type: int
        Platform type of report
    deck: int
        Deck number of report
    latitude: float
        Latitude of the report
    longitude: float
         Longitude of the report
    year: int
        Year of the report

    Returns
    -------
    int
        Returns 1 if report is ineligible for MAT QC, otherwise 0.

    References
    ----------
    https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/jgrd.50152
    """
    # Observations from ICOADS Deck 780 with platform type 5 (originating from
    # the World Ocean Database) [Boyer et al., 2009] were found to be erroneous (Z. Ji and S. Worley, personal
    # communication, 2011) and were excluded from HadNMAT2.
    if platform_type == 5 and deck == 780:
        return failed

    # North Atlantic, Suez and indian ocean to be excluded from MAT processing
    # See figure 8 from Kent et al.
    if (
        deck == 193
        and 1880 <= year <= 1892
        and (
            (-80.0 <= longitude <= 0.0 and 40.0 <= latitude <= 55.0)
            or (-10.0 <= longitude <= 30.0 and 35.0 <= latitude <= 45.0)
            or (15.0 <= longitude <= 45.0 and -10.0 <= latitude <= 40.0)
            or (15.0 <= longitude <= 95.0 and latitude >= -10.0 and latitude <= 15.0)
            or (95.0 <= longitude <= 105.0 and -10.0 <= latitude <= 5.0)
        )
    ):
        return failed

    return passed


def do_wind_blacklist(deck):
    """
    Flag certain sources as ineligible for wind QC. Based on Shawn Smith's list.

    Parameters
    ----------
    deck : int
        Deck of report

    Returns
    -------
    int
        Set to 1 if deck is in black list, 0 otherwise
    """
    if deck in [708, 780]:
        return failed

    return passed
