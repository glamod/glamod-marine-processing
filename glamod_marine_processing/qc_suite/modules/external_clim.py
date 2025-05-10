"""Module to read external climatology files."""

from __future__ import annotations

import cf_xarray  # noqa
import xarray as xr

from .time_control import day_in_year, which_pentad


def open_xrdataset(
    files,
    use_cftime=True,
    decode_cf=False,
    decode_times=False,
    parallel=False,
    data_vars="minimal",
    chunks={"time": 1},
    coords="minimal",
    compat="override",
    combine="by_coords",
    **kwargs,
):
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
    use_cftime: bool, optional
        See [decode_cf]_
    parallel: bool, optional
        See [open_mfdataset]_
    data_vars: {"minimal", "different", "all"} or list of str, optional
        See [open_mfdataset]
    chunks: int or dict, optional
        See [open_mfdataset]
    coords: {"minimal", "different", "all"} or list of str, optional
        See [open_mfdataset]
    compat: str (see `coords`), optional
        See [open_mfdataset]

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
    return xr.decode_cf(ds, use_cftime=use_cftime, decode_timedelta=False)


class Climatology:
    """Class for dealing with climatologies, reading, extracting values etc.
    Automatically detects if this is a single field, pentad or daily climatology
    """

    def __init__(self, data, obs_name, statistics):
        self.data = data
        self.time_axis = data.cf.axes["T"][0]
        self.lat_axis = data.cf.axes["Y"][0]
        self.lon_axis = data.cf.axes["X"][0]
        self.ntime = len(data[self.time_axis])
        assert self.ntime in [1, 73, 365], "weird shaped field"
        self.nlat = len(data[self.lat_axis])
        self.nlon = len(data[self.lon_axis])
        self.res = 180.0 / self.nlat
        self.obs_name = obs_name
        self.statistics = statistics

    @classmethod
    def open_netcdf_file(cls, file_name, clim_name, **kwargs):
        """Open filename with xarray."""
        ds = open_xrdataset(file_name)
        da = ds[clim_name]
        return cls(da, **kwargs)

    def get_value(
        self,
        lat: float | None = None,
        lon: float | None = None,
        month: int | None = None,
        day: int | None = None,
    ) -> float:
        """Get the value from the climatology at the give position and time.

        Parameters
        ----------
        lat: float or None
            Latitude of location to extract value from in degrees.
        lon: float or None
            Longitude of location to extract value from in degrees.
        month: int or None
            Month for which the value is required.
        day: int or None
            Day for which the value is required.

        Returns
        -------
        float
            Climatology value at specified location and time.

        Note
        ----
        Use only exact matches for selecting time and nearest valid index value for selecting location.
        """
        data = self.data.copy()
        if month is not None or day is not None:
            tindex = self.get_tindex(month, day)
            data = data.isel(**{self.time_axis: tindex})
        if lat is not None:
            data = data.sel(**{self.lat_axis: lat}, method="nearest")
        if lon is not None:
            data = data.sel(**{self.lon_axis: lon}, method="nearest")
        return data.values[0]

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
        elif self.ntime == 365:
            return day_in_year(month, day) - 1
