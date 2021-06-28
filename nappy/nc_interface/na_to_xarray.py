#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
na_to_xarray.py
===============

Container module for class NADictToXarrayObjects that is sub-classed
by NAToNC classes.

"""

# Imports from python standard library
import sys
import re
import time
import logging

# Third-party libraries
import numpy as np
import xarray as xr

# Import from nappy package
import nappy.utils
import nappy.utils.common_utils

from . import xarray_utils


config_dict = nappy.utils.getConfigDict()
na_to_nc_map = config_dict["na_to_nc_map"]
header_partitions = config_dict["header_partitions"]
hp = header_partitions


# Define global variables
safe_nc_id = re.compile(r"[\/\s\[\(\)\]\=\+\-\?\#\~\@\&\$\%\!\*\{\}\^]+")
time_units_pattn = re.compile(r"\w+\s+since\s+\d{1,4}-\d{1,2}-\d{1,2}(\s+\d+:\d+:\d+)?")
max_id_length = 64
special_comment_known_strings = (hp["sc_start"], hp["sc_end"], hp["addl_vatts"],
                                  hp["addl_globals"], "\n")

normal_comment_known_strings = (hp["nc_start"], hp["nc_end"], hp["data_next"], 
                      hp["addl_vatts"], hp["addl_globals"], "\n")

time_units_warning_message = """\nWARNING: Could not recognise time units. For true NetCDF compability
please insert the correct time unit string below in the format:
    
    <units> since <YYYY>-<MM>-<DD> <hh>-<mm>-<ss>
    
Where:
    <units> is a known time interval such as years, months, days, etc.
    <YYYY> is the year, <MM> is the month, <DD> is the day,
    <hh> is the hour, <mm> is minutes, <ss> is seconds.
"""

DEBUG = nappy.utils.getDebug() 

log = logging.getLogger(__name__)


class NADictToXarrayObjects:
    """
    Converts a NA File instance to a tuple of Xarray objects.
    """
    
    def __init__(self, na_file_obj, variables="all", aux_variables="all",
                 global_attributes=None,
                 time_units=None, time_warning=True, 
                 rename_variables=None):
        """
        Sets up instance variables.
        """
        if global_attributes is None:
            global_attributes = []

        if rename_variables is None:
            rename_variables = {}

        self.na_file_obj = na_file_obj       
        self.variables = variables
        self.aux_variables = aux_variables
        self.global_attributes = global_attributes
        self.time_units = time_units
        self.time_warning = time_warning
        self.rename_variables = {key.lower(): value for key, value in rename_variables.items()}

        # Check if we have capability to convert this FFI
        if self.na_file_obj.FFI in (2110, 2160, 2310): 
            raise Exception(("Cannot convert NASA Ames File Format Index (FFI) " + 
                             self.na_file_obj.FFI + 
                             " to Xarray objects. No mapping implemented yet."))

        self.output_message = []  # for output displaying message
        self.converted = False

    def convert(self):
        """
        Reads the NASA Ames file object and converts to Xarray objects.
        Returns (variable_list, aux_variable_list, global_attributes_list).
        All these can be readily written to a Xarray File object.
        """
        if self.converted:
            log.info("Already converted to Xarray objects so not re-doing.")
            return (self.xr_variables, self.xr_aux_variables, self.global_attributes)

        self.na_file_obj.readData()

        # Convert global attribute
        self._mapNACommentsToGlobalAttributes()

        # Convert axes
        if not hasattr(self, 'xr_axes'):
            self._convertXarrayAxes()

        # Convert main variables
        if not hasattr(self, 'xr_variables'):
            self._convertXarrayVariables()

        # Then do auxiliary variables
        if hasattr(self.na_file_obj, "NAUXV") \
             and (type(self.na_file_obj.NAUXV) == type(1) and self.na_file_obj.NAUXV > 0):   # Are there any auxiliary variables?
            if not hasattr(self, 'xr_aux_variables'):  
                self._convertXarrayAuxVariables()
        else:
            self.xr_aux_variables = []
            
        self.converted = True
        return (self.xr_variables, self.xr_aux_variables, self.global_attributes)

    def _mapNACommentsToGlobalAttributes(self):
        """
        Maps the NASA Ames comments section to global attributes and append them to the 
        self.global_attributes list.
        """
        glob_atts = dict(self.global_attributes)
        
        for key in na_to_nc_map.keys():

            if type(key) == type((1,2)):

                if key == ("SCOM", "NCOM"):
                    # Map special and normal comments into the global comments section
                    comment_line = ""

                    # Add Special comments first
                    if self.na_file_obj.NSCOML > 0:
                        comment_line += (hp["sc_start"] + "\n")

                        for i in self.na_file_obj.SCOM: 
                
                            if i.strip() not in special_comment_known_strings:
                                comment_line += ("\n" + i)
                            
                        comment_line += ("\n" + hp["sc_end"] + "\n")

                    # Now add normal comments
                    if self.na_file_obj.NNCOML > 0:
                        comment_line += (hp["nc_start"] + "\n")

                        for i in self.na_file_obj.NCOM: 
                            if i.strip() not in normal_comment_known_strings:
                                comment_line += ("\n" + i)

                        comment_line += ("\n" + hp["nc_end"])

                    # Tidy comment line then write to global atts dict
                    comment_line = comment_line.replace("\n\n", "\n")

                    glob_atts["comment"] = comment_line

                elif key == ("ONAME", "ORG"):
                    # Map the two organisation NA files to the institution field in Xarray (NetCDF)
                    institution = "%s (ONAME from NASA Ames file); %s (ORG from NASA Ames file)." % \
                                         (self.na_file_obj.ONAME, self.na_file_obj.ORG)
                    glob_atts["institution"] = institution

                else:
                    # Any other strange tuple just gets merged into a string
                    item = (getattr(self.na_file_obj, key[0])) + "\n" + (getattr(self.na_file_obj, key[1]))
                    glob_atts[na_to_nc_map[key]] = item

            elif key == "RDATE":

                # RDATE = Revision date - update this and put in history global attribute
                date_parts = getattr(self.na_file_obj, "RDATE")
                date_string = "%.4d-%.2d-%.2d" % tuple(date_parts)

                hist = date_string + " - NASA Ames File created/revised.\n"
                time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

                version = nappy.utils.getVersion()
                hist = "%s\n%s - Converted to Xarray (NetCDF) format using nappy-%s." % (hist, time_string, version)

                log.debug("No history mapping from na so added it here from global attributes.")
                glob_atts["history"] = hist           

            else:
                # Anything else just needs to be stored as a global attribute
                glob_atts[na_to_nc_map[key]] = getattr(self.na_file_obj, key)

        # Now remake global atts list
        new_atts = []

        for key, value in self.global_attributes:
            new_atts.append( (key, glob_atts[key]) )

        used_keys = [i[0] for i in new_atts]

        for key in glob_atts.keys():
            if key not in used_keys:
                new_atts.append( (key, glob_atts[key]) )

        self.global_attributes = new_atts[:]

    def _convertXarrayVariables(self):
        """
        Creates Xarray variable list for writing out.
        """
        self.xr_variables = []

        if self.variables in (None, "all"):    
            for var_number in range(self.na_file_obj.NV):
                self.xr_variables.append(self._convertNAToXarrayVariable(var_number))

        else:
            # If integers or numbers: then use as indices for selecting variables
            if isinstance(self.variables[0], int) or re.match(r"\d+", str(self.variables[0])):

                for var_number in self.variables:
                    vn = int(var_number)
                    self.xr_variables.append(self._convertNAToXarrayVariable(vn))

            # If string: then use as variable names
            elif isinstance(self.variables[0], str):

                for var_name in self.variables:

                    if var_name in self.na_file_obj.VNAME:
                        var_number = self.na_file_obj.VNAME.index(var_name)
                        self.xr_variables.append(self._convertNAToXarrayVariable(var_number))
                    else:
                        raise Exception(f"Variable name not known: {var_name}")

    def _convertNAToXarrayVariable(self, var_number, attributes=None):
        """
        Creates a single Xarray variable from the variable number provided in the list.
        """
        if attributes == None:
            attributes = {}

        (var_name, units, miss, scal) = self.na_file_obj.getVariable(var_number)

        msg = "\nAdding variable: %s" % self.na_file_obj.VNAME[var_number]
        log.debug(msg)
        self.output_message.append(msg)

        array = np.array(self.na_file_obj.V[var_number])

        if miss:
            array = np.ma.masked_array(array, fill_value=miss)

        array = array * scal

        # Set up axes
        if not hasattr(self, 'xr_axes'):
            self._convertXarrayAxes()

        # Set up variable
        var = xarray_utils.create_data_array(array, name=var_name, coords=self.xr_axes, 
                                  fill_value=miss, attrs=attributes)

        # Sort units etc
        if units:   
            var.attrs["units"] =units
    
        if len(var_name) < max_id_length:
            var_name = safe_nc_id.sub("_", var_name).lower()
        else:
            var_name = "naVariable_%s" % (var_number)

        # Check if mapping provided for renaming this variable
        if var_name.lower() in self.rename_variables.keys():
            var_name = self.rename_variables[var_name.lower()]

        var.attrs["long_name"] = var.attrs["title"] = var_name
        var.name = nappy.utils.common_utils.safe_name(var_name)

        # Add a NASA Ames variable number (for mapping correctly back to NASA Ames)
        var.attrs["nasa_ames_var_number"] = var_number
        return var

    def _convertXarrayAuxVariables(self):
        """
        Creates a Xarray variable from an auxiliary variable
        """
        self.xr_aux_variables = []

        if self.aux_variables in (None, "all"):

            for avar_number in range(self.na_file_obj.NAUXV):
                self.xr_aux_variables.append(self._convertNAAuxToXarrayVariable(avar_number))

        else:
            if type(self.aux_variables[0]) == type(1): # They are integers = indices

                for avar_number in self.aux_variables:
                    self.xr_aux_variables.append(self._convertNAAuxToXarrayVariable(avar_number))   

            elif type(self.aux_variables[0]) == type("string"): # They are strings

                for avar_name in self.aux_variables:

                    if avar_name in self.na_file_obj.ANAME:
                        avar_number = self.na_file_obj.ANAME.index(avar_name)
                        self.xr_aux_variables.append(self._convertNAAuxToXarrayVariable(avar_number)) 
            else:
                raise Exception("Auxiliary variable name not known: " + avar_name)        

    def _convertNAAuxToXarrayVariable(self, avar_number, attributes=None):
        """
        Converts an auxiliary variable to a Xarray variable.
        """
        attributes = attributes or {}
             
        (var_name, units, miss, scal) = self.na_file_obj.getAuxVariable(avar_number)

        array = np.array(self.na_file_obj.A[avar_number])
        if miss:
            array = np.ma.masked_array(array, fill_value=miss)

        array = array * scal

        msg="\nAdding auxiliary variable: %s" % self.na_file_obj.ANAME[avar_number]
        log.debug(msg)
        self.output_message.append(msg)

        # Set up axes
        if not hasattr(self, 'xr_axes'):
            self._convertXarrayAxes()

        # Set up variable
        var = xarray_utils.create_data_array(array, name=var_name, coords=self.xr_axes[:1], 
                                  fill_value=miss, attrs=attributes)

        # Sort units etc
        if units:   
            var.attrs["units"] = units

        if len(var_name) < max_id_length:
            var_name = safe_nc_id.sub("_", var_name).lower()
        else:
            var_name = f"naAuxVariable_{avar_number}"

        # Check if mapping provided for renaming this variable
        if var_name in self.rename_variables.keys():
            var_name = self.rename_variables[var_name]

        var.attrs["long_name"] = var.attrs["title"] = var_name
        var.name = nappy.utils.common_utils.safe_name(var_name)

        # Add a NASA Ames auxiliary variable number (for mapping correctly back to NASA Ames)
        var.attrs["nasa_ames_aux_var_number"] = avar_number
        return var        

    def _convertXarrayAxes(self): 
        """
        Creates Xarray axes from information provided in the NASA Ames dictionary.
        """
        if not hasattr(self, 'xr_axes'):
            self.xr_axes = []

        for ivar_number in range(self.na_file_obj.NIV):
            axis = self._convertNAIndVarToXarrayAxis(ivar_number)
            self.xr_axes.append(axis)

    def _convertNAIndVarToXarrayAxis(self, ivar_number):
        """
        Creates an Xarray axis from a NASA Ames independent variable.
        """
        if not self.na_file_obj._normalized_X:
            self.na_file_obj._normalizeIndVars()

        if self.na_file_obj.NIV == 1:
            array = self.na_file_obj.X
        else:
            array = self.na_file_obj.X[ivar_number]

        axis_name = self.na_file_obj.XNAME[ivar_number]

        (var_name, units) = self.na_file_obj.getIndependentVariable(ivar_number)
        axis_xr_name = nappy.utils.common_utils.safe_name(var_name)

        axis = xr.DataArray(array, name=axis_xr_name, attrs={'long_name': axis_name, 'units': units})
    
        # Sort units, name etc...
        if units:   
             axis.attrs["units"] = units

        if len(var_name) < max_id_length:
            axis.name = safe_nc_id.sub("_", var_name).lower()
        else:
            axis.name = f"naIndVariable_{ivar_number}"

        axis_types = [("longitude", "X"), ("latitude", "Y"), ("level", "Z"), ("time", "T")]

        for axis_type, axis_label in axis_types:

            if re.search(axis_type, axis.name, re.IGNORECASE):

                axis.attrs["standard_name"] = axis.name = axis_type
                axis.attrs["axis"] = axis_label

        # Check warning for time units pattern
        if xarray_utils.is_time(axis) and not time_units_pattn.match(str(getattr(axis, "units"))):

            # Request user input for time units (if interactive)
            if self.time_units is None:
                time_units_input = "I WON'T MATCH"

                while time_units_input != "" and not time_units_pattn.match(time_units_input):
                    message = time_units_warning_message                

                    if self.time_warning:
                        log.debug(message)
                        time_units_input = input("Please insert your time unit string here (or leave blank):").strip()
                    else: 
                        time_units_input = ""

                self.output_message.append(message)
                self.time_units = time_units_input

            axis.attrs["units"] = self.time_units
            axis.encoding["units"] = self.time_units
            axis.attrs["long_name"] = f"time ({self.time_units})"
            axis.name = "time"

        axis.attrs["name"] = axis.name

        # Rename dimension of axis
        dim_name = axis.dims[0]
        axis = axis.rename({dim_name: axis.name})

        if not getattr(axis, "units", None):
            if units:
                axis.attrs["units"] = units
            else:
                axis.attrs["units"] = "Not known"

        return axis

