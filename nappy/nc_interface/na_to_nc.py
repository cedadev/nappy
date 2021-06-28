#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
na_to_nc.py
===========

Contains the NAToNC class for converting a NASA Ames file to a NetCDF file.

"""

# Imports from python standard library
import logging
from collections.abc import Sequence

# Third-party imports
import xarray as xr
import numpy as np

# Import from nappy package
import nappy.nc_interface.na_to_xarray

log = logging.getLogger(__name__)


class NAToNC(nappy.nc_interface.na_to_xarray.NADictToXarrayObjects):
    """
    Converts a NASA Ames file to a NetCDF file.
    """
    
    def __init__(self, na_file, variables=None, aux_variables=None,
                 global_attributes=None,
                 time_units=None, time_warning=True, 
                 rename_variables=None):
        """
        Sets up instance variables. Note that the argument 'na_file' has a relaxes definition
        and can be either a NASA Ames file object or the name of a NASA AMES file.
        Typical usage is:
        >>>    import nappy.nc_interface.na_to_nc as na_to_nc
        >>>    c = na_to_nc.NAToNC("old_file.na") 
        >>>    c.convert()
        >>>    c.writeNCFile("new_file.nc")         
        """
        if global_attributes is None:
            global_attributes = []

        if not rename_variables:
            rename_variables = {}

        # First open na_file if it is a file rather than an na_file object
        na_file_obj = na_file
        if type(na_file_obj) == type("string"):
            na_file_obj = nappy.openNAFile(na_file_obj)

        nappy.nc_interface.na_to_xarray.NADictToXarrayObjects.__init__(self, na_file_obj, variables=variables, 
                 aux_variables=aux_variables,
                 global_attributes=global_attributes,
                 time_units=time_units, time_warning=time_warning, 
                 rename_variables=rename_variables)


    def fix_ints(self, dct, key):
        """
        Convert integer values in a dict to numpy.int32s - so they just show up as integers in ncdump
        (rather than 2LL (e.g. long longs)).

        Fixes the those dictionary items: either integers or a sequence of integers, then converts and
        returns them.
        """
        def to_np_int(_value):
            return np.int32(_value)

        value = dct.get(key)

        if isinstance(value, Sequence) and all([isinstance(v, int) for v in value]):
            dct[key] = [to_np_int(v) for v in value]
        elif isinstance(value, int):
            dct[key] = to_np_int(value)

    def fix_attrs(self, obj):
        """
        Check each attr of the object, and fix integer/integer-sequence values.
        """
        for key in obj.attrs:
            self.fix_ints(obj.attrs, key)

    def writeNCFile(self, file_name, mode="w"):
        """
        Writes the NASA Ames content that has been converted into Xarray objects to a
        NetCDF file of name 'file_name'. Note that mode can be set to append so you 
        can add the data to an existing file.
        """
        if not self.converted:
            self.convert()

        # Build an Xarray Dataset and then write it to NetCDF
        combined_var_list = self.xr_variables + self.xr_aux_variables

        # Fix integers in attributes
        [self.fix_attrs(v) for v in combined_var_list]

        # Create the Datset
        variables = {da.name: da for da in combined_var_list}
        ds = xr.Dataset(variables, attrs=dict(self.global_attributes))
        self.fix_attrs(ds)

        # Write to NetCDF
        ds.to_netcdf(file_name)

        log.info(f"NetCDF file '{file_name}' written successfully.")
        return True
