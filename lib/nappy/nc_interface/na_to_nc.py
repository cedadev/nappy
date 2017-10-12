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

# Imports from external packages
try:
    import cdms2 as cdms
except:
    try:
        import cdms
    except:
        raise Exception("Could not import third-party software. Nappy requires the CDMS and Numeric packages to be installed to convert to CDMS and NetCDF.")


# Import from nappy package
import nappy.nc_interface.na_to_cdms
from nappy.na_error import na_error

logging.basicConfig()
log = logging.getLogger(__name__)

class NAToNC(nappy.nc_interface.na_to_cdms.NADictToCdmsObjects):
    """
    Converts a NASA Ames file to a NetCDF file.
    """
    
    def __init__(self, na_file, variables=None, aux_variables=None,
                 global_attributes=[("Conventions","CF-1.0")],
                 time_units=None, time_warning=True, 
                 rename_variables={}):
        """
        Sets up instance variables. Note that the argument 'na_file' has a relaxes definition
        and can be either a NASA Ames file object or the name of a NASA AMES file.
        Typical usage is:
        >>>    import nappy.nc_interface.na_to_nc as na_to_nc
        >>>    c = na_to_nc.NAToNC("old_file.na") 
        >>>    c.convert()
        >>>    c.writeNCFile("new_file.nc")         
        """
        # First open na_file if it is a file rather than an na_file object
        na_file_obj = na_file
        if type(na_file_obj) == type("string"):
            na_file_obj = nappy.openNAFile(na_file_obj)

        nappy.nc_interface.na_to_cdms.NADictToCdmsObjects.__init__(self, na_file_obj, variables=variables, 
                 aux_variables=aux_variables,
                 global_attributes=global_attributes,
                 time_units=time_units, time_warning=time_warning, 
                 rename_variables=rename_variables)


    def writeNCFile(self, file_name, mode="w"):
        """
        Writes the NASA Ames content that has been converted into CDMS objects to a
        NetCDF file of name 'file_name'. Note that mode can be set to append so you 
        can add the data to an existing file.
        """
        if not self.converted:
            self.convert()

        # Create CDMS output file object
        fout = cdms.open(file_name, mode=mode)

        # Write main variables
        for var in self.cdms_variables:
            fout.write(var)

        # Write aux variables
        for avar in self.cdms_aux_variables:
            fout.write(avar)

        # Write global attributes
        for (att, value) in self.global_attributes:
            setattr(fout, att, value)
        
        fout.close()
        log.info("NetCDF file '%s' written successfully." % file_name)
        return True
