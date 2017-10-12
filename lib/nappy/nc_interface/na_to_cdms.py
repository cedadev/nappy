#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
na_to_cdms.py
=============

Container module for class NADictToCdmsObjects that is sub-classed
by NAToNC classes.

"""

# Imports from python standard library
import sys
import re
import time
import logging

# Import from nappy package
from nappy.na_error import na_error
import nappy.utils
import nappy.utils.common_utils

config_dict = nappy.utils.getConfigDict()
na_to_nc_map = config_dict["na_to_nc_map"]
header_partitions = config_dict["header_partitions"]
hp = header_partitions

# Import external packages (if available)
if sys.platform.find("win") > -1:
    raise na_error.NAPlatformError("Windows does not support CDMS. CDMS is required to convert to CDMS objects and NetCDF.")

try:
    import cdms2 as cdms
    import numpy as N
except:
    try:
        import cdms
        import Numeric as N
    except:
        raise Exception("Could not import third-party software. Nappy requires the CDMS and Numeric packages to be installed to convert to CDMS and NetCDF.")


# Define global variables
safe_nc_id = re.compile("[\/\s\[\(\)\]\=\+\-\?\#\~\@\&\$\%\!\*\{\}\^]+")
time_units_pattn = re.compile("\w+\s+since\s+\d{4}-\d{1,2}-\d{1,2}\s+\d+:\d+:\d+")
max_id_length = 40
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

logging.basicConfig()
log = logging.getLogger(__name__)

class NADictToCdmsObjects:
    """
    Converts a NA File instance to a tuple of CDMS objects.
    """
    
    def __init__(self, na_file_obj, variables="all", aux_variables="all",
                 global_attributes=[("Conventions", "CF-1.0")],
                 time_units=None, time_warning=True, 
                 rename_variables={}):
        """
        Sets up instance variables.
        """
        self.na_file_obj = na_file_obj	   
        self.variables = variables
        self.aux_variables = aux_variables
        self.global_attributes = global_attributes
        self.time_units = time_units
        self.time_warning = time_warning
        self.rename_variables = rename_variables

        # Check if we have capability to convert this FFI
        if self.na_file_obj.FFI in (2110, 2160, 2310): 
	        raise Exception("Cannot convert NASA Ames File Format Index (FFI) " + `self.na_file_obj.FFI` + " to CDMS objects. No mapping implemented yet.")

        self.output_message = []  # for output displaying message
        self.converted = False

    def convert(self):
        """
        Reads the NASA Ames file object and converts to CDMS objects.
        Returns (variable_list, aux_variable_list, global_attributes_list).
        All these can be readily written to a CDMS File object.
        """
        if self.converted == True:
            log.info("Already converted to CDMS objects so not re-doing.")
            return (self.cdms_variables, self.cdms_aux_variables, self.global_attributes)

        self.na_file_obj.readData()

        # Convert global attribute
        self._mapNACommentsToGlobalAttributes()

        # Convert axes
        if not hasattr(self, 'cdms_axes'):  self._convertCdmsAxes()

        # Convert main variables
        if not hasattr(self, 'cdms_variables'):  self._convertCdmsVariables()

        # Then do auxiliary variables
        if hasattr(self.na_file_obj, "NAUXV") and (type(self.na_file_obj.NAUXV) == type(1) and self.na_file_obj.NAUXV > 0):   # Are there any auxiliary variables?
            if not hasattr(self, 'cdms_aux_variables'):  
                self._convertCdmsAuxVariables()
        else:
            self.cdms_aux_variables = []
            
        self.converted = True
        return (self.cdms_variables, self.cdms_aux_variables, self.global_attributes)


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
                    # Map the two organisation NA files to the institution field in CDMS (NetCDF)
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
                hist = "%s\n%s - Converted to CDMS (NetCDF) format using nappy-%s." % (hist, time_string, version)
                # self.cdms_file.history = hist
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

    def _convertCdmsVariables(self):
        """
        Creates cdms variable list for writing out.
        """
        self.cdms_variables = []

        if self.variables in (None, "all"):    
            for var_number in range(self.na_file_obj.NV):
                self.cdms_variables.append(self._convertNAToCdmsVariable(var_number))
        else:
            if type(self.variables[0]) == type(1) or re.match("\d+", str(self.variables[0])): # They are integers = indices
                for var_number in self.variables:
                    vn = int(var_number)
                    self.cdms_variables.append(self._convertNAToCdmsVariable(vn))   
            elif type(self.variables[0]) == type("string"):  # Vars are strings
                for var_name in self.variables:
                    if var_name in self.na_file_obj.VNAME:
                        var_number = self.na_file_obj.VNAME.index(var_name)
                        self.cdms_variables.append(self._convertNAToCdmsVariable(var_number))
                    else:
                        raise Exception("Variable name not known: " + var_name)


    def _convertNAToCdmsVariable(self, var_number, attributes={}):
        """
        Creates a single cdms variable from the variable number provided in the list.
        """
        (var_name, units, miss, scal) = self.na_file_obj.getVariable(var_number)
        msg = "\nAdding variable: %s" % self.na_file_obj.VNAME[var_number]
        log.debug(msg)
        self.output_message.append(msg)
        array = N.array(self.na_file_obj.V[var_number])
        array = array * scal
        # Set up axes
        if not hasattr(self, 'cdms_axes'):
            self._convertCdmsAxes()

        # Set up variable
        var=cdms.createVariable(array, axes=self.cdms_axes, fill_value=miss, attributes=attributes)

        # Sort units etc
        if units:   var.units=units
	
        # Add the best variable name
        if len(var_name) < max_id_length:
            var.id=safe_nc_id.sub("_", var_name).lower()
        else:
            var.id="naVariable_%s" % (var_number)
        
	     # Check if mapping provided for renaming this variable
        if var_name in self.rename_variables.keys():
            var_name = self.rename_variables[var_name]
	    
        var.long_name = var.name = var.title = var_name

        # Add a NASA Ames variable number (for mapping correctly back to NASA Ames)
        var.nasa_ames_var_number = var_number
        return var

    def _convertCdmsAuxVariables(self):
        """
        Creates a cdms variable from an auxiliary variable
        """
        self.cdms_aux_variables = []

        if self.aux_variables in (None, "all"):
            for avar_number in range(self.na_file_obj.NAUXV):
                self.cdms_aux_variables.append(self._convertNAAuxToCdmsVariable(avar_number))
        else:
            if type(self.aux_variables[0]) == type(1): # They are integers = indices
                for avar_number in self.aux_variables:
                    self.cdms_aux_variables.append(self._convertNAAuxToCdmsVariable(avar_number))   

            elif type(self.aux_variables[0]) == type("string"): # They are strings
                for avar_name in self.aux_variables:
                    if avar_name in self.na_file_obj.ANAME:
                        avar_number = self.na_file_obj.ANAME.index(avar_name)
                        self.cdms_aux_variables.append(self._convertNAAuxToCdmsVariable(avar_number)) 
            else:
                raise Exception("Auxiliary variable name not known: " + avar_name)	    

    def _convertNAAuxToCdmsVariable(self, avar_number, attributes={}):
        """
        Converts an auxiliary variable to a cdms variable.
        """
        (var_name, units, miss, scal) = self.na_file_obj.getAuxVariable(avar_number)
        array = N.array(self.na_file_obj.A[avar_number])
        array = array * scal

        msg="\nAdding auxiliary variable: %s" % self.na_file_obj.ANAME[avar_number]
        log.debug(msg)
        self.output_message.append(msg)

        # Set up axes
        if not hasattr(self, 'cdms_axes'):
            self._convertCdmsAxes()

        # Set up variable
        var = cdms.createVariable(array, axes=[self.cdms_axes[0]], fill_value=miss, 
                                  attributes=attributes)

        # Sort units etc
        if units:   var.units = units
        if len(var_name) < max_id_length:
            var.id = safe_nc_id.sub("_", var_name).lower()
        else:
            var.id = "naAuxVariable_%s" % (avar_number)

	    # Check if mapping provided for renaming this variable
        if var_name in self.rename_variables.keys():
            var_name = self.rename_variables[var_name]

        var.long_name = var.name = var.title = var_name

        # Add a NASA Ames auxiliary variable number (for mapping correctly back to NASA Ames)
        var.nasa_ames_aux_var_number = avar_number
        return var        

    def _convertCdmsAxes(self): 
        """
        Creates cdms axes from information provided in the NASA Ames dictionary.
        """
        if not hasattr(self, 'cdms_axes'):        
            self.cdms_axes = []

        for ivar_number in range(self.na_file_obj.NIV):
            self.cdms_axes.append(self._convertNAIndVarToCdmsAxis(ivar_number))


    def _convertNAIndVarToCdmsAxis(self, ivar_number):
        """
        Creates a cdms axis from a NASA Ames independent variable.
        """
        if self.na_file_obj._normalized_X == False:   self.na_file_obj._normalizeIndVars()

        if self.na_file_obj.NIV == 1:
            array = self.na_file_obj.X
        else:
            array = self.na_file_obj.X[ivar_number]

        axis = cdms.createAxis(array)
        axis.id = axis.name = axis.long_name = self.na_file_obj.XNAME[ivar_number]
        (var_name, units) = self.na_file_obj.getIndependentVariable(ivar_number)
	
        # Sort units etc
        if units:   axis.units = units
        if len(var_name) < max_id_length:
            axis.id = safe_nc_id.sub("_", var_name).lower()
        else:
            axis.id = "naIndVariable_%s" % (ivar_number)

        if units: axis.units = units

        axis_types = ("longitude", "latitude", "level", "time")

        for axis_type in axis_types:
            if re.search(axis_type, var_name, re.IGNORECASE):
                axis.standard_name = axis.id = axis_type
                # Designate it CF-style if known axis type (e.g. axis.designateTime() etc..)
                exec "axis.designate%s()" % axis_type.title()

        # Check warning for time units pattern
        if axis.isTime() and (not hasattr(axis, "units") or not time_units_pattn.match(axis.units)):
            if self.time_units == None:
                time_units_input = "I WON'T MATCH"

                while time_units_input != "" and not time_units_pattn.match(time_units_input):
                    message = time_units_warning_message			    
                    if self.time_warning == True:
                        log.debug(message)
                        time_units_input = raw_input("Please insert your time unit string here (or leave blank):").strip()
                    else: 
                        time_units_input = ""

                self.output_message.append(message)
                self.time_units = time_units_input

	    axis.units = self.time_units
            axis.long_name = axis.name = "time (%s)" % self.time_units

        if not hasattr(axis, "units") or axis.units == None:  
            if units:
                axis.units = units	
            else:
                axis.units = "Not known"

        return axis
