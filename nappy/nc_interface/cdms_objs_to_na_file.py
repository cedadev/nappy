#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
cdms_objs_to_na_file.py
========================

Holds the class CDMSObjectsToNAFile (sub-classing NCToNA) that converts a 
CDMS objects (variables and global atts) to one or more NASA Ames files.

"""

# Imports from python standard library
import sys
import logging

# Import from nappy package
import nappy
from nappy.na_error import na_error
import nappy.utils
import nappy.nc_interface.nc_to_na

# Import external packages (if available)
if sys.platform.find("win") > -1:
    raise na_error.NAPlatformError("Windows does not support CDMS. CDMS is required to convert to CDMS objects and NetCDF.")

try:
    import cdms2 as cdms
except:
    try:
        import cdms
    except:
        raise Exception("Could not import third-party software. Nappy requires the CDMS and Numeric packages to be installed to convert to CDMS and NetCDF.")

cdms.setAutoBounds("off")

# Define global variables
DEBUG = nappy.utils.getDebug()
default_delimiter = nappy.utils.getDefault("default_delimiter")
default_float_format = nappy.utils.getDefault("default_float_format")

# Define logger
logging.basicConfig()
log = logging.getLogger(__name__)


class CDMSObjectsToNAFile(nappy.nc_interface.nc_to_na.NCToNA):
    """
    Converts a set of CDMS Objects to one or more NASA Ames files.
    """

    def __init__(self, cdms_variables, global_attributes=[], na_items_to_override={},
                 only_return_file_names=False,
                 requested_ffi=None,
                 ):
        """
        Sets up instance variables.
        Typical usage is:
        >>>    import nappy.nc_interface.cdms_objs_to_na_file as na_maker
        >>>    c = na_maker.CDMSObjectsToNAFile(existing_var_list)
        >>>    c.convert()
        >>>    c.writeNAFiles("new_file.na", delimiter=",")
        """
        self.cdms_variables = cdms_variables
        self.global_attributes = global_attributes
        self.na_items_to_override = na_items_to_override
        self.only_return_file_names = only_return_file_names
        self.requested_ffi = requested_ffi

        self.converted = False
        self.output_message = []

