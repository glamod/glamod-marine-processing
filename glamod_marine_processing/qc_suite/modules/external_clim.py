"""Module to read external climatology files."""

from __future__ import annotations

import inspect
import warnings
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Literal

import cf_xarray  # noqa
import numpy as np
import xarray as xr
from numpy import ndarray
from xclim.core.units import convert_units_to

from .time_control import day_in_year, split_date, which_pentad


def inspect_climatology(*climatology_keys: str) -> Callable:
    """Create a decorator to inspect input sequences and convert them to numpy arrays.

    Parameters
    ----------
    climatology: float or Climatology
        Climatology value
        This could be a float value or Climatology object.

    Returns
    -------
    Callable
        The decorator function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)

            for clim_key in climatology_keys:
                if clim_key not in bound_args.arguments:
                    raise TypeError(
                        f"Missing expected argument '{clim_key}' in function '{func.__name__}'."
                        "The decorator requires this argument to be present."
                    )

                climatology = bound_args.arguments[clim_key]
                if isinstance(climatology, Climatology):
                    if "kwargs" not in bound_args.arguments:
                        warnings.warn(
                            f"'kwargs' not found in bound arguments for function '{func.__name__}'. "
                            "Climatology.get_value(**kwargs) may fail."
                        )
                        func_kwargs = {}
                    else:
                        func_kwargs = bound_args.arguments["kwargs"]
                    get_value_sig = inspect.signature(climatology.get_value)
                    required_keys = {
                        name
                        for name, param in get_value_sig.parameters.items()
                        if param.default is param.empty
                        and param.kind
                        in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY)
                    }
                    missing_in_kwargs = required_keys - func_kwargs.keys()
                    if missing_in_kwargs:
                        warnings.warn(
                            f"The following required arguments for '{type(clim_key).__name__}.get_value' are missing from **kwargs "
                            f"in function '{func.__name__}': {missing_in_kwargs}. "
                            f"Ensure all required arguments are passed via **kwargs."
                        )
                    try:
                        climatology = climatology.get_value(**func_kwargs)
                    except ValueError:
                        climatology = np.nan
                    except TypeError:
                        climatology = np.nan

                bound_args.arguments[clim_key] = climatology

            return func(*bound_args.args, **bound_args.kwargs)

        return wrapper

    return decorator


def open_xrdataset(
    files: str | list,
    use_cftime: bool = True,
    decode_cf: bool = False,
    decode_times: bool = False,
    parallel: bool = False,
    data_vars: Literal["all", "minimal", "different"] = "minimal",
    chunks: int | dict | Literal["auto", "default"] | None = "default",
    coords: Literal["all", "minimal", "different"] | None = "minimal",
    compat: Literal[
        "identical", "equals", "broadcast_equals", "no_conflicts", "override", "minimal"
    ] = "override",
    combine: Literal["by_coords", "nested"] | None = "by_coords",
    **kwargs,
) -> xr.Dataset:
    """Optimized function for opening large cf datasets.

    based on [open_xrdataset]_.
    decode_timedelta=False is added to leave variables and
    coordinates with time units in
    {"days", "hours", "minutes", "seconds", "milliseconds", "microseconds"}
    encoded as numbers.

    Parameters
    ----------
    files: str or list
        See [open_mfdataset]_
    use_cftime: bool, default: True
        See [decode_cf]_
    decode_cf: bool, default: True
        See [decode_cf]_
    decode_times: bool, default: False
        See [decode_cf]_
    parallel: bool, default: False
        See [open_mfdataset]_
    data_vars: {"minimal", "different", "all"} or list of str, default: "minimal"
        See [open_mfdataset]
    chunks: int, dict, "auto" or None, optional, default: "default"
        If chunks is "default", set chunks to {"time": 1}
        See [open_mfdataset]
    coords: {"minimal", "different", "all"} or list of str, optional, default: "minimal"
        See [open_mfdataset]
    compat: {"identical", "equals", "broadcast_equals", "no_conflicts", "override", "minimal"}, default: "override"
        See [open_mfdataset]
    combine: {"by_coords", "nested"}, optional, default: "by_coords"
        See [open_mfdataset]_

    Returns
    -------
    xarray.Dataset

    References
    ----------
    .. [open_xrdataset] https://github.com/pydata/xarray/issues/1385#issuecomment-561920115
    .. [open_mfdataset] https://docs.xarray.dev/en/stable/generated/xarray.open_mfdataset.html
    .. [decode_cf] https://docs.xarray.dev/en/stable/generated/xarray.decode_cf.html

    """

    def drop_all_coords(ds):
        return ds.reset_coords(drop=True)

    if chunks == "default":
        chunks = {"time": 1}

    ds = xr.open_mfdataset(
        files,
        parallel=parallel,
        decode_times=decode_times,
        combine=combine,
        preprocess=drop_all_coords,
        decode_cf=decode_cf,
        chunks=chunks,
        data_vars=data_vars,
        coords=coords,
        compat=compat,
        **kwargs,
    )
    time_coder = xr.coders.CFDatetimeCoder(use_cftime=use_cftime)
    return xr.decode_cf(ds, decode_times=time_coder, decode_timedelta=False)


class Climatology:
    """Class for dealing with climatologies, reading, extracting values etc.
    Automatically detects if this is a single field, pentad or daily climatology.

    Parameters
    ----------
    data: xr.DataArray
        Climatology data
    time_axis: str, optional
        Name of time axis.
        Set if time axis in `data` is not CF compatible.
    lat_axis: str, optional
        Name of latitude axis.
        Set if latitude axis in `data` is not CF compatible.
    lon_axis: str, optional
        Name of longitude axis.
        Set if longitude axis in `data` is not CF compatible.
    source_units: str, optional
        Name of units in `data`.
        Set if units are not defined in `data`.
    target_units: str, optional
        Name of target units to which units must conform.
    valid_ntime: int or list, default: [1, 73, 365]
        Number of valid time steps:
        1: single field climatology
        73: pentad climatology
        365: daily climatology
    """

    def __init__(
        self,
        data: xr.DataArray,
        time_axis: str | None = None,
        lat_axis: str | None = None,
        lon_axis: str | None = None,
        source_units: str | None = None,
        target_units: str | None = None,
        valid_ntime: int | list = [1, 73, 365],
    ):
        self.data = data
        self.convert_units_to(target_units, source_units=source_units)
        if time_axis is None:
            self.time_axis = data.cf.coordinates["time"][0]
        else:
            self.time_axis = time_axis
        if lat_axis is None:
            self.lat_axis = data.cf.coordinates["latitude"][0]
        else:
            self.lat_axis = lat_axis
        if lon_axis is None:
            self.lon_axis = data.cf.coordinates["longitude"][0]
        else:
            self.lon_axis = lon_axis
        if not isinstance(valid_ntime, list):
            valid_ntime = [valid_ntime]
        self.ntime = len(data[self.time_axis])
        assert self.ntime in valid_ntime, "weird shaped field"

    @classmethod
    def open_netcdf_file(cls, file_name, clim_name, **kwargs) -> Climatology:
        """Open filename with xarray."""
        ds = open_xrdataset(file_name)
        da = ds[clim_name]
        return cls(da, **kwargs)

    def convert_units_to(self, target_units, source_units=None) -> None:
        """Convert units to user-specific units.

        Parameters
        ----------
        target_units: str
            Target units to which units must conform.
        source_units, str, optional
            Source units if not specified in :py:class:`Climatology`.

        Note
        ----
        For more information see: :py:func:`xclim.core.units.convert_units_to`
        """
        if target_units is None:
            return
        if source_units is not None:
            self.data.attrs["units"] = source_units
        self.data = convert_units_to(self.data, target_units)

    def get_value(
        self,
        lat: float | None = None,
        lon: float | None = None,
        date: datetime | None = None,
        month: int | None = None,
        day: int | None = None,
    ) -> ndarray:
        """Get the value from a climatology at the give position and time.

        Parameters
        ----------
        lat: float, optional
            Latitude of location to extract value from in degrees.
        lon: float, optional
            Longitude of location to extract value from in degrees.
        date: datetime-like, optional
            Date for which the value is required.
        month: int, optional
            Month for which the value is required.
        day: int, optional
            Day for which the value is required.

        Returns
        -------
        ndarray
            Climatology value at specified location and time.

        Note
        ----
        Use only exact matches for selecting time and nearest valid index value for selecting location.
        """
        data = self.data.copy()
        if isinstance(date, datetime):
            date_ = split_date(date)
            if date_ is None:
                return
            month = date_["month"]
            day = date_["day"]
        if month is not None or day is not None:
            tindex = self.get_tindex(month, day)
            data = data.isel(**{self.time_axis: tindex})
        if lat is not None:
            data = data.sel(**{self.lat_axis: lat}, method="nearest")
        if lon is not None:
            data = data.sel(**{self.lon_axis: lon}, method="nearest")
        return data.values

    def get_tindex(self, month: int, day: int) -> int:
        """Get the time index of the input month and day.

        Parameters
        ----------
        month: int
            Month for which the time index is required.
        day: int
            Day for which the time index is required.

        Returns
        -------
        int
            Time index for specified month and day.
        """
        if self.ntime == 1:
            return 0
        elif self.ntime == 73:
            return which_pentad(month, day) - 1
        return day_in_year(month, day) - 1


@inspect_climatology("climatology")
def get_climatological_value(climatology: Climatology, **kwargs) -> ndarray:
    """Get the value from a climatology.

    Parameters
    ----------
    climatology: Climatology
        Climatology class
    kwargs: dict
        Pass keyword-arguments to :py:class:~Climatology.get_value`

    Returns
    -------
    ndarray
            Climatology value at specified location and time.
    """
    return climatology
