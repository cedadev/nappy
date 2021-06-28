#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
xarray_objs_to_na_file.py
=========================

Holds the class XarrayObjectsToNAFile (sub-classing NCToNA) that converts a 
Xarray objects (variables and global atts) to one or more NASA Ames files.

"""

# Imports from python standard library
import sys
import logging

# Import from nappy package
import nappy
import nappy.utils
import nappy.nc_interface.nc_to_na


# Define global variables
DEBUG = nappy.utils.getDebug()
default_delimiter = nappy.utils.getDefault("default_delimiter")
default_float_format = nappy.utils.getDefault("default_float_format")

# Define logger
log = logging.getLogger(__name__)


class XarrayObjectsToNAFile(nappy.nc_interface.nc_to_na.NCToNA):
    """
    Converts a set of Xarray Objects to one or more NASA Ames files.
    """

    def __init__(self, xr_variables, global_attributes=None, na_items_to_override=None,
                 only_return_file_names=False,
                 requested_ffi=None,
                 ):
        """
        Sets up instance variables.
        Typical usage is:
        >>>    import nappy.nc_interface.xr_objs_to_na_file as na_maker
        >>>    c = na_maker.XarrayObjectsToNAFile(existing_var_list)
        >>>    c.convert()
        >>>    c.writeNAFiles("new_file.na", delimiter=",")
        """
        self.xr_variables = xr_variables
        self.global_attributes = global_attributes or []
        self.na_items_to_override = na_items_to_override or {}
        self.only_return_file_names = only_return_file_names
        self.requested_ffi = requested_ffi

        self.converted = False
        self.output_message = []

