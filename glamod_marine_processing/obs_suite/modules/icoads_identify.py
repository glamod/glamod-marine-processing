"""Module containing main QC functions which could be applied on a DataBundle."""

from __future__ import annotations

from ._utilities import auto_cast


def is_in_valid_list(
    value: str | int | float, valid_list: str | int | float | list
) -> int:
    """Identify whether a value is in a valid_list.

    Parameters
    ----------
    value : str, int or float
        Value to test
    valid_list : str, int, float or list
         List of valid values

    Returns
    -------
    int
        Return 0 if value is in valid list and 1 otherwise
    """
    if not isinstance(valid_list, list):
        valid_list = [valid_list]
    if value in valid_list:
        return True
    return False


@auto_cast
def is_buoy(platform_type: int, valid_list: list | int = [6, 7]) -> int:
    """
    Identify whether report is from a moored or drifting buoy based on ICOADS platform type PT.

    Parameters
    ----------
    platform_type : int
        Platform type
    valid_list: list or int, default: [6, 7]
        List of valid platform types

    Returns
    -------
    int
        Return 0 if observation is from a drifting or moored buoy and 1 otherwise
    """
    return is_in_valid_list(platform_type, valid_list)


@auto_cast
def is_drifter(platform_type: int, valid_list: list | int = 7) -> int:
    """
    Identify whether report is from a drifting buoy based on ICOADS platform type PT.
    trackqc is only applied to drifting buoys. Used to filter drifting buoys.

    Parameters
    ----------
    platform_type : int
        Platform type
    valid_list: list or int, default: 7
        List of valid platform types

    Returns
    -------
    int
        Return 0 if observation is from a drifting buoy and 1 otherwise
    """
    return is_in_valid_list(platform_type, valid_list)


@auto_cast
def is_ship(
    platform_type: int, valid_list: list | int = [0, 1, 2, 3, 4, 5, 10, 11, 12, 17]
) -> int:
    """
    Identify whether report is from a ship based on ICOADS platform type PT.
    Marien Air Temperature QC only performed on reports from ships. Used to filter ships.

    Parameters
    ----------
    platform_type : int
        Platform type
    valid_list: list or str, default: [0, 1, 2, 3, 4, 5, 10, 11, 12, 17]
        List of valid platform types

    Returns
    -------
    int
        Return 0 if observation is from a ship and 1 otherwise
    """
    return is_in_valid_list(platform_type, valid_list)


@auto_cast
def is_deck(dck: int, valid_list: list | int = 780) -> int:
    """
    Identify obs that are from ICOADS Deck 780 which consists of obs from WOD.
    Observations from deck 780 are not used so they are not included in QC.

    Parameters
    ----------
    dck : int
        Deck of observation
    valid_list: list or int, default: 780
        List of valid deck numbers

    Returns
    -------
    int
        return 0 if observation is in deck 780 and 1 otherwise
    """
    return is_in_valid_list(dck, valid_list)


@auto_cast
def id_is_generic(inid: str, inyear: int) -> bool:
    """Test to see if an ID is one of the generic IDs.

    Certain callsigns are shared by large numbers of ships. e.g. SHIP, PLAT, 0120,
    MASK, MASKSTID. This simple routine has a list of known generic call signs.
    Some call signs are only generic between certain years.

    Parameters
    ----------
    inid : str
        ID from marine report
    inyear : int
        Year we are checking for

    Returns
    -------
    bool
        True if the ID is generic and False otherwise
    """
    generic_ids = [
        None,
        "",
        "1",
        "58",
        "RIGG",
        "SHIP",
        "ship",
        "PLAT",
        "0120",
        "0204",
        "0205",
        "0206",
        "0207",
        "0208",
        "0209",
        "MASKST",
        "MASKSTID",
        "MASK",
        "XXXX",
        "/////",
    ]

    if 1921 <= inyear <= 1941:
        generic_ids.append("2")
        generic_ids.append("00002")

    if 1930 <= inyear <= 1937:
        generic_ids.append("3")

    if 1934 <= inyear <= 1954:
        generic_ids.append("7")
        generic_ids.append("00007")

    result = False
    if inid.strip() in generic_ids:
        result = True
    return result
