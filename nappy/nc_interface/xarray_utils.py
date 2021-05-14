"""
xarray_utils.py
===============

A set of useful functions involving xarray objects.
"""

import re

import numpy as np
import xarray as xr


def getBestName(var):
    """
    Returns the most appropriate variable name for a NASA Ames header.
    """
    name = None
    att_order = ("long_name", "standard_name", "title", "name", "shortname", "id")

    # Deal with object that has attributes
    for att in att_order:
        if hasattr(var, att):   
            name = getattr(var, att)
            break

    # Deal with object that has dictionary lookup instead of attributes
    if hasattr(var, "get") and name is None:
        for att in att_order:
            if att in var:   
                name = var[att]
                break

    # Raise an error if no name
    if name == None:
        raise Exception("Cannot find a valid name for variable.")

    if hasattr(var, "units") and not re.match(r"^\s+$", var.units):

        units = var.units.strip()
        name = f"{name} ({units})"

        if name.count(f"({units})") > 1:
            name = name.replace(f"({units})", "")  # remove all (units) and start again
            name = f"{name}({units})"              # using the space inserted last time

    # Remove empty parantheses from end of name if there
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


def isUniformlySpaced(array):
    """
    Returns True if array values are uniformaly spaced else returns False.
    """
    arr = np.array(array)

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
    Takes 2 CDMS axis objects returning True if they are essentially
    the same and False if not.
   
    If is_subset == True then return True if ax1 is same as ax2 except that it is
    only defined on a subset of regularly spaced values within ax2.
   
    If is_subset is used then return value is False or (len(ax2)/len(ax1)).
   
    If check_id == False then don't compare the ids of the axes.
    """
    for axtype in ("time", "level", "latitude", "longitude"):
        if cdms.axisMatches(ax1, axtype) == 1 and not (cdms.axisMatches(ax2, axtype) == 1):
            return False

    # Check ids
    if check_id:
        if ax1.id != ax2.id: return False

    # Check units
    if hasattr(ax1, 'units') and hasattr(ax2, 'units'):
        if ax1.units != ax2.units: 
            return False

    # Do different comparisons depending on 'is_subset' argument
    if is_subset == False:
        # Check lengths and values
        if (len(ax1) != len(ax2)) or \
           (ax1.getData()[:].tolist() != ax2.getData()[:].tolist()): 
            return False

    elif is_subset == True:
        # Check whether values are a subset
        len1 = len(ax1)
        len2 = len(ax2)

        # Check length of 1 divides into length of 2
        if len2 % len1 != 0:
            return False

        # Now test if it is subset
        n = len2 / len1

        for i in range(len(ax1)):
            ax2_value = ax2[n * i]
            test_value = ax1[i]
            if ax2_value != test_value:
                return False

        # If we got here then return len2/len1
        return n

    # OK, I think they are the same axis!
    return True


