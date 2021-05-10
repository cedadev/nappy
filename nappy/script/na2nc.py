#!/usr/bin/env python
#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
na2nc.py
========

Converts a NASA Ames file to a NetCDF file.

Usage
=====

   na2nc.py [-m <mode>] [-g <global_atts_list>]
            [-r <rename_vars_list>] [-t <time_units>] [-n] 
            -i <na_file> [-o <nc_file>] 

Where
-----

    <mode>			is the file mode, either "w" for write or "a" for append
    <global_atts_list>		is a comma-separated list of global attributes to add
    <rename_vars_list>		is a comma-separated list of <old_name>,<new_name> pairs to rename variables
    <time_units>		is a valid time units string such as "hours since 2003-04-30 10:00:00"
    -n				suppresses the time units warning if invalid
    <na_file>			is the input NASA Ames file path
    <nc_file>			is the output NetCDF file path (default is to replace ".na" from NASA Ames
           			 file with ".nc").
 
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
    a["na_file"] = None
    a["mode"] = "w"
    a["variables"] = "all"
    a["aux_variables"]  = "all"
    a["global_attributes"] = {}
    a["rename_variables"] = {}
    a["time_units"] = None
    a["time_warning"] = True
    a["nc_file"] = None

    try:
        (arg_list, dummy) = getopt.getopt(args, "i:o:m:v:a:g:t:nr:")
    except getopt.GetoptError as e:
        exitNicely(str(e))
    
    for arg, value in arg_list:
        if arg == "-i":
            a["na_file"] = value
        elif arg == "-o":
            a["nc_file"] = value
        elif arg == "-m":
            a["mode"] = value
        elif arg == "-v":
            a["variables"] = value.split(",")
            exitNicely("OPTION NOT IMPLEMENTED: %s : Not yet fully functional. Sorry." % arg)
        elif arg == "-a":
            a["aux_variables"] = value.split(",")
            exitNicely("OPTION NOT IMPLEMENTED: %s : Not yet fully functional. Sorry." % arg)
        elif arg == "-g":
            a["global_attributes"] = makeListFromCommaSepString(value)
        elif arg == "-t":
            a["time_units"] = value
        elif arg == "-n":
            a["time_warning"] = False
        elif arg == "-r":
            a["rename_variables"] = makeDictFromCommaSepString(value)
        else:
            exitNicely("Argument '" + arg + "' not recognised!")

    if not a["na_file"]:
        exitNicely("Please provide argument '-i <na_file>'")

    if not a["nc_file"]:
        fn = a["na_file"]
        if fn[-3:] == ".na": fn = fn[:-3]
        nc_file = fn + ".nc"
        print("Auto-generating output file name:", nc_file)
        a["nc_file"] = nc_file

    return a


def na2nc(args=None):
    """
    Controller for conversion of NASA Ames file to NetCDF file.
    """

    if args is None:
        args = sys.argv[1:]
    
    arg_dict = parseArgs(args)
    na_file = arg_dict["na_file"]
    del arg_dict["na_file"]
    nc_file = apply(nappy.convertNAToNC, [na_file], arg_dict)


if __name__ == "__main__":

    args=sys.argv[1:]
    na2nc(args)
