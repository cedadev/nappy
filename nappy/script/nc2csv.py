#!/usr/bin/env python
#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""

nc2csv.py
=========

Converts a NetCDF file into one or more NASA Ames file.

Usage
=====

    nc2csv.py [-v <var_list>] [--ffi=<ffi>] [-f <float_format>] 
             [-l <limit_ffi_1001_rows>] 
             [-e <exclude_vars>] [--overwrite-metadata=<key1>,<value1>[,<key2>,<value2>[...]]] 
             [--names-only] [--no-header] [--annotated]
             -i <nc_file> [-o <csv_file>] 
Where
-----

    <nc_file> 			- name of input file (NetCDF).
    <csv_file>	 		- name of output file (NASA Ames or CSV) - will be used as base name if multiple files.
    <var_list>           	- a comma-separated list of variables (i.e. var ids) to include in the output file(s).
    <ffi>			- NASA Ames File Format Index (FFI) to write to (normally automatic).  
    <float_format>          	- a python formatting string such as %s, %g or %5.2f
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
import nc2na

# Uses nc2na(...) directly



if __name__ == "__main__":

    args = sys.argv[1:]
    if "-d" in args:
        exitNicely("nc2csv.py does not accept the -d argument as the delimiter is fixed as a comma, try using nc2na.py instead.")

    args.extend(["-d", ","])
    nc2na.nc2na(args)
