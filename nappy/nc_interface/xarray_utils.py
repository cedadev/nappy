"""
xarray_utils.py
===============

A set of useful functions involving xarray objects.
"""

import re

import numpy as np
import xarray as xr
import cf_xarray  # noqa
import cftime



def getBestName(var):
    """
    Returns the most appropriate variable name for a NASA Ames header.
    """
    # Return itself if is string
    if isinstance(var, str):
        return var

    name = None
    att_order = ("long_name", "standard_name", "title", "name", "short_name", "id")

    # Deal with object that has attributes
    for att in att_order:
        if hasattr(var, att):   
            name = getattr(var, att)
            break

    # Deal with object that has dictionary lookup instead of attributes
    if hasattr(var, "get") and not name:
        for att in att_order:
            if att in var:   
                name = var[att]
                break

    # Raise an error if no name
    if not name:
        raise Exception("Cannot find a valid name for variable.")

    units = getattr(var, "units", "")

    # See if we can get the units from the encoding if not defined.
    # This is required for time.
    if not units:
        units = var.encoding.get("units", "")

    units = units.strip()

    if units:
        name = f"{name} ({units})"

        if name.count(f"({units})") > 1:
            name = name.replace(f"({units})", "")  # remove all (units) and start again
            name = f"{name}({units})"              # using the space inserted last time

    # Remove empty parentheses from end of name if there
    if name[-2:] == "()": 
        name = name[:-2]

    return name


def getMissingValue(var):
    """
    Returns the missing value or defaults to -1.e20
    """
    miss = None

    if hasattr(var, "encoding"):
        for key in ("_FillValue", "missing_value", "_fill_value"):
            if key in var.encoding: 
                miss = var.encoding[key]
                break

    if miss is None:
        miss = -1.e20

    return miss


def getAxisList(var):
    """
    Returns a list of coordinates from: var
    """ 
    return [var.coords[key] for key in var.dims]


def isUniformlySpaced(arr):
    """
    Returns True if array values are uniformaly spaced else returns False.
    """
    if is_time(arr):
        arr = datetimes_to_nums(arr)
    else:
        arr = np.array(arr)

    start = arr[0]
    end = arr[-1]
    length = len(arr)

    return all(np.linspace(start, end, length) == arr)


def isAxisRegularlySpacedSubsetOf(ax1, ax2):
    """
    Returns True if ax1 is same as ax2 except that it is only defined on a
    subset of regularly spaced values within ax2. Otherwise returns False.
    """
    return areAxesIdentical(ax1, ax2, is_subset=True, check_id=False)


def areAxesIdentical(ax1, ax2, is_subset=False, check_id=True):
    """
    Takes 2 axis (coord) objects returning True if they are essentially
    the same and False if not.
   
    If is_subset == True then return True if ax1 is same as ax2 except that it is
    only defined on a subset of regularly spaced values within ax2.
   
    If is_subset is used then return value is False or (len(ax2)/len(ax1)).
   
    If check_id == False then don't compare the ids of the axes.
    """
    for axtype in ("time", "level", "latitude", "longitude"):
        if axtype in ax1.cf and axtype in ax2.cf and ax1.cf[axtype].name != ax2.cf[axtype].name:
            return False

    # Check ids
    if check_id:
        if ax1.name != ax2.name: return False

    # Check units
    if getattr(ax1, 'units', None) != getattr(ax2, 'units', None):
        return False

    # Do different comparisons depending on 'is_subset' argument
    if is_subset == False:
        # Check lengths and values only
        if (len(ax1) != len(ax2)) or all(ax1.data != ax2.data):
            return False

    else:
        # Check whether values are a subset
        len1 = len(ax1)
        len2 = len(ax2)

        # Check length of 1 divides into length of 2
        if len2 % len1 != 0:
            return False

        # Now test if it is subset
        n = int(len2 / len1)

        for i in range(len(ax1)):
            ax2_value = ax2[n*i]
            test_value = ax1[i]

            if ax2_value != test_value:
                return False

        # If we got here then return len2 / len1
        return n

    # OK, I think they are the same axis!
    return True


def is_latitude(coord):
    """
    Determines if a coordinate is latitude.

    :param coord: coordinate of xarray dataset e.g. coord = ds.coords[coord_id]
    :return: (bool) True if the coordinate is latitude.
    """

    if "latitude" in coord.cf and coord.cf["latitude"].name == coord.name:
        return True

    if coord.attrs.get("standard_name", None) == "latitude":
        return True

    return False


def is_longitude(coord):
    """
    Determines if a coordinate is longitude.

    :param coord: coordinate of xarray dataset e.g. coord = ds.coords[coord_id]
    :return: (bool) True if the coordinate is longitude.
    """
    if "longitude" in coord.cf and coord.cf["longitude"].name == coord.name:
        return True

    if coord.attrs.get("standard_name", None) == "longitude":
        return True

    return False


def is_level(coord):
    """
    Determines if a coordinate is level.

    :param coord: coordinate of xarray dataset e.g. coord = ds.coords[coord_id]
    :return: (bool) True if the coordinate is level.
    """
    if "vertical" in coord.cf and coord.cf["vertical"].name == coord.name:
        return True

    if hasattr(coord, "positive"):
        if coord.attrs.get("positive", None) == "up" or "down":
            return True

    if hasattr(coord, "axis"):
        if coord.attrs.get("axis", None) == "Z":
            return True

    return False


def is_time(coord, test_by_values=False):
    """
    Determines if a coordinate is time.

    :param coord: coordinate of xarray dataset e.g. coord = ds.coords[coord_id]
    :test_by_values: boolean to decide whether to identify by checking first value type
    :return: (bool) True if the coordinate is time.
    """
    if "time" in coord.cf and coord.cf["time"].name == coord.name:
        return True

    if np.issubdtype(coord.dtype, np.datetime64):
        return True

    if isinstance(np.atleast_1d(coord.values)[0], cftime.datetime):
        return True

    if hasattr(coord, "axis"):
        if coord.axis == "T":
            return True

    if coord.attrs.get("standard_name", None) == "time":
        return True

    if test_by_values and len(coord) > 0:
        # Test the first value to see if it is a datetime object
        values = resolve_array(coord.data)

        if isinstance(values.flat[0], cftime.datetime):
            return True

    return False


def get_coord_by_index(da, indx):
    """
    Take an Xarray DataArray, return a coordinate by its index in the
    order of the data structure. E.g. if var is defined on: ('time', 'lat'),
    indx=0 will return the coordinate labelled as 'time'.
    """
    coord_name = da.dims[indx]
    return da.coords[coord_name]


def get_dim_names_for_variables(variables):
    """
    Analyses variables to gather a list of dimension (coordinate)
    names. These are returned as a set of dimension names.
    """
    return {dim for v in variables for dim in v.dims}


def create_data_array(arr, name, coords, attrs, fill_value):
    """
    Create an Xarray DataArray and assign properties as required.
    """
    da = xr.DataArray(arr, name=name, coords=coords, attrs=attrs)
    da.encoding["_FillValue"] = fill_value
    return da


def datetimes_to_nums(da):
    units = da.time.encoding['units']
    calendar = da.time.encoding.get('calendar', 'standard')
    arr = cftime.date2num(da.data, units, calendar=calendar)
    return arr


def get_interval(da, indx1, indx2, handle_datetimes=True):
    if not isinstance(da, xr.DataArray):
        arr = da
    elif is_time(da) and handle_datetimes:
        arr = datetimes_to_nums(da)
    else:
        arr = da.data

    return arr[indx2] - arr[indx1]


def getArrayAsList(da, missing_value=None, handle_datetimes=True):
    """
    Takes a DataArray ``da``.
    If the array is masked then replace masked values with 
    ``missing_value``.
    If ``handle_datetimes`` is True, then ensure that the units and
    calendar are used to convert datetimes to sensible values.
    """
    if is_time(da, test_by_values=True) and handle_datetimes:
        arr = datetimes_to_nums(da)

    elif missing_value is not None:
        arr = resolve_array(da.data)
        found_nans = np.isnan(arr).any()

        if found_nans:
            arr = da.fillna(missing_value).data
        else:
            arr = da.data

    else:
        arr = da.data

    arr = resolve_array(arr)

    return arr.tolist()


def resolve_array(arr):
    """
    Takes an array that may be a numpy/masked or Dask array.
    If it is a Dask array then `compute` it to convert to values.
    """
    if hasattr(arr, "compute"):
        arr = arr.compute()

    return arr
