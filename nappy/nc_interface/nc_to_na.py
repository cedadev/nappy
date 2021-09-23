#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
nc_to_na.py
=============

Holds the class NCToNA (sub-classing XarrayToNA) that converts a NetCDF file to
one or more NASA Ames files.

"""

# Imports from python standard library
import sys
import logging

import xarray as xr
import numpy as np

# Import from nappy package
import nappy
from nappy.utils.common_utils import fuzzy_contains, get_rank_zero_array_value
import nappy.nc_interface.xarray_to_na

log = logging.getLogger(__name__)


class NCToNA(nappy.nc_interface.xarray_to_na.XarrayToNA):
    """
    Converts a NetCDF file to one or more NASA Ames files.
    """

    def __init__(self, nc_file, var_ids=None, na_items_to_override=None, 
            only_return_file_names=False, exclude_vars=None,
            requested_ffi=None,
            ):
        """
        Sets up instance variables.
        Typical usage is:
        >>>    import nappy.nc_interface.nc_to_na as nc_to_na
        >>>    c = nc_to_na.NCToNA("old_file.nc") 
        >>>    c.convert()
        >>>    c.writeNAFiles("new_file.na", delimiter=",") 

        OR:
        >>>    c = nc_to_na.NCToNA("old_file.nc") 
        >>>    file_names = c.constructNAFileNames() 
        """
        self.nc_file = nc_file

        # Now need to read Xarray file so parent class methods are compatible
        xr_variables, global_attributes = self._readXarrayFile(var_ids, exclude_vars)

        super().__init__(xr_variables, global_attributes=global_attributes, 
                         na_items_to_override=na_items_to_override, 
                         only_return_file_names=only_return_file_names,
                         requested_ffi=requested_ffi)
 

    def _readXarrayFile(self, var_ids=None, exclude_vars=None, exclude_bounds=True):
        """
        Reads the file and returns all the Xarray variables in a list as well
        as the global attributes: (xr_variable_list, global_atts_list)
        If var_ids is defined then only get those.
        If exclude_bounds is True: exclude "bounds" variables.
        """
        exclude_vars = exclude_vars or []

        ds = xr.open_dataset(self.nc_file, use_cftime=True, decode_timedelta=False)
        xr_variables = []

        # Make sure var_ids is a list
        if isinstance(var_ids, str):
            var_ids = [var_ids]

        # Identify bounds variables
        bounds_vars = {ds[var_id].attrs.get("bounds", None) for var_id in ds.variables}

        if None in bounds_vars:
            bounds_vars.remove(None)

        for var_id in ds.variables:
            if var_ids == None or var_id in var_ids:

                # Process required variables
                if not fuzzy_contains(var_id, exclude_vars):
                    if exclude_bounds and var_id in bounds_vars:
                        continue

                    da = ds[var_id]

                    # Check whether singleton variable, if so create variable                   
                    if hasattr(da, "shape") and da.shape == ():
                        # Test type of the data to convert  
                        data_value = get_rank_zero_array_value(da.values) 
                        da = xr.DataArray(np.array(data_value), name=da.name, attrs=da.attrs)

                    xr_variables.append(da)

        global_attrs = ds.attrs.items()
        return (xr_variables, global_attrs)
