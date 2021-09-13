#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
na_core.py
==========

Holds the NACore class that holds the None type version
of all the possible NASA Ames variables described in the Gaines
and Hipskind (1998)document. It also holds a number of useful methods
for accessing metadata within the file.

"""

# Imports from standard python library
import copy
import re


class NACore:
    """
    Abstract class to hold the empty NASA Ames contents and 
    a number of methods to access information in files. This
    class is sub-classed by all NAFile classes.
    """
    
    var_and_units_pattern = re.compile(r"^\s*(.*)\((.+?)\)(.*)\s*$")
    na_dictionary_keys = ("A", "AMISS", "ANAME", "ASCAL", "DATE", "DX",
                     "FFI", "IVOL", "LENA", "LENX", "MNAME", "NAUXC",
                     "NAUXV", "NCOM", "NIV", "NLHEAD", "NNCOML",
                     "NSCOML", "NV", "NVOL", "NVPM", "NX", "NXDEF",
                     "ONAME", "ORG", "RDATE", "SCOM", "SNAME", "V",
                     "VMISS", "VNAME", "VSCAL", "X", "XNAME", "ignored_header_lines")

    def __init__(self):
        """
        Creates an instance variable of every type used in all
        NA formats. All are set to None until/unless defined.
        """
        # Set up attributes for all possible NASA Ames dictionary items
        for key in NACore.na_dictionary_keys:
            setattr(self, key, None)

    def getNADict(self):
        """
        Returns a dictionary of the contents of a NASA Ames file.
        """
        dct = {}
        for key in NACore.na_dictionary_keys:
            dct[key] = getattr(self, key)

        self.na_dict = {}

        for key in dct:
            if dct[key] != None:
                self.na_dict[key] = dct[key]

        return self.na_dict

    def setNADict(self, na_dict):
        """
        Dynamic setting of the na_dict dictionary.
        """
        self.na_dict = copy.deepcopy(na_dict)

    def __getitem__(self, item):
        """
        Dictionary item access to NASA Ames contents, called NAFileObj['NIV']
        will return NAFileObj.NIV.
	
        Note: In future this might return whatever user wants and to translate
        NASA Ames variables such as 'NIV' to explanatory strings
        such as 'number_of_independent_variables'. Need a map for
        this defined at top of the nasaAmesData.py module
        """
        if hasattr(self, item):
            return getattr(self, item)
        else:
            return "Item '%s' not found." % item

    def _attemptVarAndUnitsMatch(self, item):
        """
        If it can match variable name and units from the name it does and returns
        (var_name, units). Otherwise returns (item, None).
        """
        match = NACore.var_and_units_pattern.match(item)

        if match:
            (v1, units, v2) = match.groups()
            var_name = v1 + " " + v2
        else:
            (var_name, units) = (item, None)   
  
        return (var_name.strip(), units)

    def getVariable(self, var_number): 
        """
        Returns variable metadata corresponding to the var_number argument in the 
        list of varibles. Tuple of (variable_name, units, missing_value, scale_factor)
        is returned.
        """
        (variable, units) = self._attemptVarAndUnitsMatch(self.VNAME[var_number])
        miss = self.getMissingValue(var_number)
        scale = self.getScaleFactor(var_number)
        return (variable, units, miss, scale)

    def getIndependentVariable(self, ivar_number):
        """
        Returns an independent variable name and units in a tuple corresponding to
        the ivar_number index in the list.
        """
        (variable, units) = self._attemptVarAndUnitsMatch(self.XNAME[ivar_number])
        return (variable, units)

    def getAuxVariable(self, avar_number):        
        """
        Returns an auxiliary variable name and units in a tuple corresponding to
        the ivar_number index in the list.
        """
        (variable, units) = self._attemptVarAndUnitsMatch(self.ANAME[avar_number])
        miss = self.getAuxMissingValue(avar_number)
        scale = self.getAuxScaleFactor(avar_number)
        return (variable, units, miss, scale)    

    def getVariables(self):
        """
        Returns metadata for all main (non-auxiliary or independent) variables.
        """
        vars = []

        for i in range(self.NV):
            vars.append(self.getVariable(i))

        return vars

    def getIndependentVariables(self):
        """
        Returns metadata for all independent variables.
        """
        ivars = []

        for i in range(self.NIV):
            ivars.append(self.getIndependentVariable(i))

        return ivars

    def getAuxVariables(self):
        """
        Returns metadata for all auxiliary variables.
        """
        avars = []

        if not hasattr(self, "NAUXV"):
            for i in range(self.NAUXV):
                avars.append(self.getAuxVariable(i))

        return avars

    def getMissingValue(self, var_number):
        """
        Returns a missing value for a given variable.
        """
        return self.VMISS[var_number]


    def getScaleFactor(self, var_number):
        """
        Returns a scale factor for a given variable.
        """
        return self.VSCAL[var_number]
	
    def getAuxMissingValue(self, avar_number):
        """
        Returns the missing value of an auxiliary variable.
        """
        return self.AMISS[avar_number]

    def getAuxScaleFactor(self, avar_number):
        """
        Returns the scale factor of an auxiliary variable.
        """ 
        return self.ASCAL[avar_number]

    def getNumHeaderLines(self):
        """
        Returns the number of header lines.
        """
        return self.NLHEAD

    def getFFI(self):
        """
        Returns the File Format Index for the file.
        """
        return self.FFI

    def getOriginator(self):
        """
        Returns the Originator (ONAME) string.
        """
        return self.ONAME

    def getOrganisation(self):
        """
        Returns the Organisation (ORG) string.
        """
        return self.ORG

    def getOrg(self):
        """
        Returns the Organisation (ORG) string.
        """
        return self.getOrganisation()

    def getSource(self):
        """
        Returns the Source (SOURCE) string.
        """
        return self.SNAME

    def getMission(self):
        """
        Returns the mission (MNAME) string.	
        """
        return self.MNAME

    def getVolumes(self):
        """
        Returns the volume numbers (IVOL and NVOL).
        """
        return (self.IVOL, self.NVOL)

    def getFileDates(self):
        """
        Returns the first valid date in the data (DATE) and the 
        Revision Date (RDATE).
        """
        return (self.DATE, self.RDATE)

    def getNormalComments(self):
        """
        Returns the Normal Comment (NCOM) lines.
        """
        return self.NCOM

    def getSpecialComments(self):
        """
        Returns the Special Comments (SCOM) lines.
        """
        return self.SCOM

