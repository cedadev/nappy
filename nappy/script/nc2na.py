#!/usr/bin/env python
#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""

nc2na.py
========

Converts a NetCDF file into one or more NASA Ames file.

Usage
=====

    nc2na.py [-v <var_list>] [--ffi=<ffi>] [-f <float_format>] 
             [-d <delimiter>] [-l <limit_ffi_1001_rows>] 
             [-e <exclude_vars>] [--overwrite-metadata=<key1>,<value1>[,<key2>,<value2>[...]]] 
             [--names-only] [--no-header] [--annotated]
             -i <nc_file> [-o <na_file>] 
Where
-----

    <nc_file> 			- name of input file (NetCDF).
    <na_file>	 		- name of output file (NASA Ames or CSV) - will be used as base name if multiple files.
    <var_list>           	- a comma-separated list of variables (i.e. var ids) to include in the output file(s).
    <ffi>			- NASA Ames File Format Index (FFI) to write to (normally automatic).  
    <float_format>          	- a python formatting string such as %s, %g or %5.2f
    <delimiter>	 		- the delimiter you wish to use between data items in the output file such as "   " or "\t"
    <limit_ffi_1001_rows> 	- if format FFI is 1001 then chop files up into <limitFFI1001Rows> rows of data.  
    <exclude_vars>          	- a comma-separated list of variables (i.e. var ids) to exclude in the output file(s).
    <key1>,<value1>[,<key2>,<value2>[...]] - list of comma-separated key,value pairs to overwrite in output files:
								* Typically the keys are in: 
                                   * "DATE", "RDATE", "ANAME", "MNAME","ONAME", "ORG", "SNAME", "VNAME".
    --names-only		- only display a list of file names that would be written (i.e. don't convert actual files).
    --no-header			- Do not write NASA Ames header
    --annotated			- add annotation column in first column
    
"""

# Imports from python standard library
import sys
import getopt

# Import from nappy package
import nappy
from nappy.utils.common_utils import makeListFromCommaSepString, makeDictFromCommaSepString


def exitNicely(msg=""):
    "Exits nicely!"
    print(__doc__)
    if msg != "": print("ERROR:", msg)
    sys.exit()


def parseArgs(args):
    """
    Parses arguments and returns dictionary.
    """
    arg_dict = {}
    a = arg_dict

    # Set up defaults
    a["nc_file"] = None
    a["var_ids"] = None
    a["requested_ffi"] = None
    a["float_format"] = nappy.default_float_format
    a["delimiter"] = nappy.default_delimiter
    a["size_limit"] = None
    a["exclude_vars"] = []
    a["na_items_to_override"] = {}
    a["only_return_file_names"] = False
    a["na_file"] = None
    a["no_header"] = False
    a["annotation"] = False

    try:
        (arg_list, dummy) = getopt.getopt(args, "i:o:v:f:d:l:e:", 
                              ["ffi=", "overwrite-metadata=", "names-only",
                               "no-header", "annotated"])
    except getopt.GetoptError as e:
        exitNicely(str(e))

    for arg, value in arg_list:
        if arg == "-i":
            a["nc_file"] = value
        elif arg == "-o":
            a["na_file"] = value
        elif arg == "-v":
            a["var_ids"] = value.split(",")
        elif arg == "--ffi":
            a["requested_ffi"] = int(value)
        elif arg == "-f":
            a["float_format"] = value
        elif arg == "-d":
            a["delimiter"] = value
        elif arg == "--limit_ffi_1001_rows":
            a["size_limit"] = long(value)
        elif arg == "-e":
            a["exclude_vars"] = value.split(",")
        elif arg == "--overwrite-metadata":
            a["na_items_to_override"] = makeDictFromCommaSepString(value)
        elif arg == "--names-only":
            a["only_return_file_names"] = True
        elif arg == "--no-header":
            a["no_header"] = True
        elif arg == "--annotated":
            a["annotation"] = True
        else:
            exitNicely("Argument '" + arg + "' not recognised!")

    if not a["nc_file"]:
        exitNicely("Please provide argument '-i <nc_file>'")

    return a


def nc2na(args=None):
    """
    Controller for conversion of NetCDF file to NASA Ames files.
    """

    if args is None:
        args = sys.argv[1:]

    arg_dict = parseArgs(args)
    nc_file = arg_dict["nc_file"]
    del arg_dict["nc_file"]
    na_files = apply(nappy.convertNCToNA, [nc_file], arg_dict)

    # If user only wants files then only give them that
    if arg_dict["only_return_file_names"]:
        print("\nExpected file names would be:")
        for naf in na_files:
            print("    ", naf)

    else:
        print("\nSuccessfully wrote: ")
        for naf in na_files:
            print("    ", naf)


if __name__ == "__main__":

    args = sys.argv[1:]
    nc2na(args)
