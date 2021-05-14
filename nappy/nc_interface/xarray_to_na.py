#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
xarray_to_na.py
===============

Holds the class XarrayToNA that converts a set of Xarray variables (DataArrays) and global attributes.

"""

# Imports from python standard library
import sys
import logging

import xarray as xr
import numpy as np

# Import from nappy package
import nappy
from nappy.na_error import na_error
import nappy.utils
import nappy.utils.common_utils

import .xarray_utils

import nappy.na_file.na_core
import .na_content_collector


# Define global variables
var_limit = 5000 # surely never going to get this many vars in a file!

DEBUG = nappy.utils.getDebug() 

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class XarrayToNA:
    """
    Converts Xarray objects to NASA Ames file dictionaries.
    """

    def __init__(self, xr_variables, global_attributes=[], na_items_to_override={}, 
                 only_return_file_names=False, requested_ffi=None,
                 ):
        """
        Sets up instance variables.      
        """
        self.xr_variables = xr_variables
        self.global_attributes = global_attributes
        self.na_items_to_override = na_items_to_override
        self.only_return_file_names = only_return_file_names
        self.requested_ffi = requested_ffi

        self.converted = False
        self.output_message = []
    
    def convert(self):
        """
        Reads the Xarray objects and convert to a set of dictionaries that
        provide the structure for a NA File object.
        Returns [(na_dict, var_ids), (na_dict, var_ids), ....]
        All these na_dict dictionaries can be readily written to a NA File object.

        Note that NASA Ames is not as flexible as NetCDF so you cannot just send any 
        set of variables to write to a NASA Ames file. Essentially there is one
        multi-dimensional structure and all variables must be defined against it.

        Otherwise variables must be auxiliary variables within that structure (i.e. only
        defined once per the least changing dimension.
        """
        if self.converted:
            return self.na_dict_list
        
        # Convert any singleton variables to Xarray variables
        variables = self._convertSingletonVars(self.xr_variables)

        # Re-order variables if they have the attribute "nasa_ames_var_number" which means they came from a NASA Ames file originally
        variables = self._reorderVars(variables)

        # Make first call to collector class that creates NA dict from Xarray variables and global atts list 
        collector = nappy.nc_interface.na_content_collector.NAContentCollector(variables, 
                                        self.global_attributes, requested_ffi=self.requested_ffi,
                                        )
        collector.collectNAContent()

        # Return if no files returned
        if not collector.found_na:
            msg = "\nNo files created after variables parsed."
            if DEBUG: log.debug(msg)
            self.output_message.append(msg)
            return

        # NOTE: collector has attributes: na_dict, var_ids, unused_vars

        # Set up a list to collect multiple calls to content collector
        na_dict_list = []
        na_dict_list.append((collector.na_dict, collector.var_ids))

        # If there are variables that were not captured (i.e. unused) by NAContentCollector then loop through these
        # in attempt to convert all to a set of na_dicts
        log.debug("\nUnused_vars: %s" % collector.unused_vars)
        while len(collector.unused_vars) > 0:
            collector = nappy.nc_interface.na_content_collector.NAContentCollector(collector.unused_vars, 
                                        self.global_attributes, requested_ffi=self.requested_ffi,
                                        )
            collector.collectNAContent()           
            self.output_message += collector.output_message

            # Append to list if more variables were captured
            if collector.found_na:
                na_dict_list.append((collector.na_dict, collector.var_ids))

        self.na_dict_list = na_dict_list
        self.converted = True

        return self.na_dict_list

    def _convertSingletonVars(self, variables):
        """
        Loops through variables to convert singleton variables (i.e. Masked Arrays/Numeric Arrays) 
        to proper Xarray variables. Then code won't break when asking for rank attribute later.
        Returns a list of Xarray variable objects
        """
        vars = []

        for variable in variables:
            var_obj = variable

            # If singleton variable then convert into proper Xarray variables so code doesn't break later
            if not hasattr(var_obj, "rank") or var_obj.rank() == 0:
              
                var_metadata = var_obj.attributes       
                var_obj = xr.DataArray(np.array(var_obj), 
                                   id = xarray_utils.getBestName(var_metadata).replace(" ", "_"), 
                                   attributes=var_metadata)
                var_obj.value = float(var_obj._data)
                
            vars.append(var_obj)

        return vars

    def _reorderVars(self, variables):
        """
        Returns a reordered list of variables. Any that have the attribute 
        "nasa_ames_var_number" get ordered first in the list (according to numbering).
        """
        # Set up a long list (longer than number of vars)
        if len(variables) > var_limit:
            raise Exception("Can only handle converting less than " + var_limit + " variables in any batch.")

        # Collect up those that are ordered and unordered
        ordered_vars = [None] * var_limit
        unordered_vars = []

        for var in variables:
            var_metadata = var.attributes
            if hasattr(var_metadata, "nasa_ames_var_number"):
                num = var_metadata.nasa_ames_var_number
                ordered_vars[num] = var
            else:
                unordered_vars.append(var)
    
        vars = []

        # Clear any None values in ordered_vars and place in final vars list
        for var in ordered_vars + unordered_vars:
            # Test for Real var types
            if type(var) != type(None): 
                vars.append(var)
	     
        return vars

