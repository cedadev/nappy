# nappy

*NASA Ames Package in Python.*

## Description

A NASA Ames I/O package - A python input/output package for NASA Ames file formats.

## Version History

This repository was previously hosted on CEDA's Subversion repository. The first tagged release here is:

 - version 1.1.4

## Reference doc

Software written with reference to:

'Format Specification for Data Exchange' paper by Gaines and Hipkind (1998).
`makeheader.f` fortran application to write NASA Ames headers, Anne de Rudder (2000).
Ames python library developed by Bryan Lawrence (2003).

## Conventions:

The basic NASAAmes class holds a dictionary called naVars which holds all the variables described in the Gaines and Hipkind document and these are all named using CAPITAL LETTERS for compliance/reference with that document.

For example the number of independent variables is held in the instance variable:

`self["NIV"]`

Return values are being calculated for many functions/methods are often prefixed with 'rt' symbolising 'return'.

## Usage documentation for nappy

Nappy provides the following functionality:

 1. A set of I/O routines for most NASA Ames File Format Indices (FFIs).
 2. An implicit checking facility for NASA Ames compliance - i.e. if the file is formatted incorrectly then a python error will be raised. This checking facility will eventually be made explicit to report NASA Ames specific errors.
 3. Methods to interrogate the contents the contents of NASA Ames files (such as: `naFile.getVariable()`, `naFile.getIndependentVariables()`, `naFile.getMissingValue()` etc.).
 4. A set of  to allow conversion to and from NetCDF (for the most common FFIs) using the Xarray library. *Note* that any Xarray-compatible format can potentially be converted to NASA Ames via these libraries. In order to use this feature your software should have `nappy[netcdf_conversion]` in its requirements. 
 5. Some command line utilities for the format conversions in (4).

### PYTHONPATH and import issues

The most common stumbling block for python users is getting to grips with PYTHONPATH (or `sys.path`), an environment variable used to tell python where it should look for modules and packages.  

In order for your python scripts, modules and interactive sessions to find the nappy package you must make the directory visible by pointing to it in one of the following ways.

If the nappy directory has been installed at `/my/nappy/location/nappy` then the directory you need to tell python about is `/my/nappy/location`.

#### Option 1. Append your nappy path to the `PYTHONPATH` environment variable:

```bash
export PYTHONPATH=$PYTHONPATH:/my/nappy/location
```

#### Option 2: Append your nappy path once within python:

```pydoc
>>> import sys   # Imports the sys module
>>> sys.path.append("/my/nappy/location")   # Adds the directory to others
                                            # used when searching for a module.
```

You should then be able to import nappy with:

```pydoc
>>> import nappy
```

#### Option 3: Installing to a virtualenv

```bash
virtualenv nappy
cd nappy
source bin/activate
git clone https://github.com/cedadev/nappy.git
cd nappy
python setup.py install
```

## Usage Examples

The following examples demonstrate and overview of nappy usage:

### Example 1: Opening and interrogating a NASA Ames file

Open the python interactive prompt:

```bash
python
```

Import the nappy package:

```pydoc
>>> import nappy
```

Open a NASA Ames file (reading the header only):

```pydoc
>>> myfile = nappy.openNAFile('some_nasa_ames_file.na')
```

Query the methods on the 'myfile' objects:

```pydoc
>>> dir(myfile)

['A', 'AMISS', 'ANAME', 'ASCAL', 'DATE', 'DX', 'FFI', 'IVOL', 
'LENA', 'LENX', 'MNAME', 'NAUXC', 'NAUXV', 'NCOM', 'NIV', 
'NLHEAD', 'NNCOML', 'NSCOML', 'NV', 'NVOL', 'NVPM', 'NX', 
'NXDEF', 'ONAME', 'ORG', 'RDATE', 'SCOM', 'SNAME', 'V', 
'VMISS', 'VNAME', 'VSCAL', 'X', 'XNAME', '__doc__', 
'__getitem__', '__init__', '__module__', '_checkForBlankLines', 
'_normalizeIndVars', '_normalizedX', '_open', '_parseDictionary', 
'_readAuxVariablesHeaderSection', '_readCharAuxVariablesHeaderSection',
'_readComments', '_readCommonHeader', '_readData1', '_readData2', 
'_readLines', '_readNormalComments', '_readSpecialComments', 
'_readTopLine', '_readVariablesHeaderSection', '_setupArrays', 
'_writeAuxVariablesHeaderSection', '_writeComments', 
'_writeCommonHeader', '_writeVariablesHeaderSection', 
'auxToXarrayVariable', 'close', 'createXarrayAuxVariables', 
'createXarrayAxes', 'createXarrayVariables', 'file', 'filename', 
'floatFormat', 'getAuxMissingValue', 'getAuxScaleFactor', 
'getAuxVariable', 'getAuxVariables', 'getFFI', 'getFileDates', 
'getIndependentVariable', 'getIndependentVariables', 
'getMissingValue', 'getMission', 'getNADict', 'getNormalComments', 
'getNumHeaderLines', 'getOrg', 'getOrganisation', 'getOriginator', 
'getScaleFactor', 'getSource', 'getSpecialComments', 'getVariable', 
'getVariables', 'getVolumes', 'naDict', 'pattnBrackets', 'readData', 
'readHeader', 'delimiter', 'toXarrayAxis', 'toXarrayFile', 'toXarrayVariable', 
'writeData', 'writeHeader']
```

List the variables:

```pydoc
>>> myfile.getVariables()
[('Mean zonal wind', 'm/s', 200.0, 1.0)]
```

List the independent variables (or dimension axes):

```pydoc
>>> myfile.getIndependentVariables()
[('Altitude', 'km'), ('Latitude', 'degrees North')]
```

Get a dictionary of the file contents in the form of NASA Ames documentation:

```pydoc
>>> myfile.getNADict()
{'ASCAL': [1.0], 'NLHEAD': 43, 'NNCOML': 11, 'NCOM': 
['The files included in this data set illustrate each of the 9 NASA Ames file', 
'format indices (FFI). A detailed description of the NASA Ames format can be', 
'found on the Web site of the British Atmospheric Data Centre (BADC) at', 
'http://www.badc.rl.ac.uk/help/formats/NASA-Ames/', 
'E-mail contact: badc@rl.ac.uk', 
'Reference: S. E. Gaines and R. S. Hipskind, Format Specification for Data', 
'Exchange, Version 1.3, 1998. This work can be found at', 
'http://cloud1.arc.nasa.gov/solve/archiv/archive.tutorial.html', 
'and a copy of it at', 
'http://www.badc.rl.ac.uk/help/formats/NASA-Ames/G-and-H-June-1998.html', ''], 
'DX': [20.0, 10.0], 'DATE': [1969, 1, 1], 'NXDEF': [1], 
'ONAME': 'De Rudder, Anne', 'SNAME': 'Anemometer measurements averaged over longitude', 
'MNAME': 'NERC Data Grid (NDG) project', 'NX': [9], 'NSCOML': 9, 
'RDATE': [2002, 10, 31], 'AMISS': [2000.0], 'VSCAL': [1.0], 'NV': 1, 
'NVOL': 13, 'X': [[], [0.0]], 'XNAME': ['Altitude (km)', 'Latitude (degrees North)'], 
'VNAME': ['Mean zonal wind (m/s)'], 'SCOM': ['Example of FFI 2010 (b).', 
'This example illustrating NASA Ames file format index 2010 is based on results', 
'from Murgatroyd (1969) as displayed in Brasseur and Solomon, Aeronomy of the', 
'Middle Atmosphere, Reidel, 1984 (p.36). It is representative of the mean zonal', 
'wind distribution in the winter hemisphere as a function of latitude and height.', 
'The first date on line 7 (1st of January 1969) is fictitious.', 
'From line 10 (NXDEF = 1) we know that the latitude points are defined by', 
'X(i) = X(1) + (i-1)DX1 for i = 1, ..., NX', 
'with X(1) = 0 deg (line 11), DX1 = 10 deg (line 8) and NX = 9 (line 9).'], 
'VMISS': [200.0], 'IVOL': 7, 'FFI': 2010, 
'ORG': 'Rutherford Appleton Laboratory, Chilton OX11 0QX, UK - Tel.: +44 (0) 1235 445837', 'NIV': 2, 
'ANAME': ['Pressure (hPa)'], 'NAUXV': 1}
```

Grab the normal comments:

```pydoc
>>> comm=myfile.naDict["NCOM"]
>>> print(comm)
['The files included in this data set illustrate each of the 9 NASA Ames file', 
'format indices (FFI). A detailed description of the NASA Ames format can be', 
'found on the Web site of the British Atmospheric Data Centre (BADC) at', 
'http://www.badc.rl.ac.uk/help/formats/NASA-Ames/', 'E-mail contact: badc@rl.ac.uk', 
'Reference: S. E. Gaines and R. S. Hipskind, Format Specification for Data', 
'Exchange, Version 1.3, 1998. This work can be found at', 
'http://cloud1.arc.nasa.gov/solve/archiv/archive.tutorial.html', 
'and a copy of it at', 
'http://www.badc.rl.ac.uk/help/formats/NASA-Ames/G-and-H-June-1998.html', '']
```

Use the file method to get the normal comments:

```pydoc
>>> myfile.getNormalComments()
['The files included in this data set illustrate each of the 9 NASA Ames file', 
'format indices (FFI). A detailed description of the NASA Ames format can be', 
'found on the Web site of the British Atmospheric Data Centre (BADC) at', 
'http://www.badc.rl.ac.uk/help/formats/NASA-Ames/', 'E-mail contact: badc@rl.ac.uk',
'Reference: S. E. Gaines and R. S. Hipskind, Format Specification for Data', 
'Exchange, Version 1.3, 1998. This work can be found at', 
'http://cloud1.arc.nasa.gov/solve/archiv/archive.tutorial.html', 
'and a copy of it at', 
'http://www.badc.rl.ac.uk/help/formats/NASA-Ames/G-and-H-June-1998.html', '']
```

Read the actual data:

```pydoc
>>> myfile.readData()
```

Inspect the data array ("V") in the NASA Ames dictionary:

```pydoc
>>> print(myfile.naDict["V"})
[[[-3.0, -2.6000000000000001, -2.2999999999999998, 2.0, 4.7999999999999998, 
4.5999999999999996, 4.5, 3.0, -0.90000000000000002], [-15.1, -4.2000000000000002, 
6.9000000000000004, 12.800000000000001, 14.699999999999999, 20.0, 21.5, 18.0, 
8.1999999999999993], [-29.0, -15.199999999999999, 3.3999999999999999, 
28.199999999999999, 41.0, 39.100000000000001, 17.899999999999999, 8.0, 
0.10000000000000001], [-10.0, 8.4000000000000004, 31.199999999999999, 
59.899999999999999, 78.5, 77.700000000000003, 47.0, 17.600000000000001, 
16.0], [200.0, 200.0, 200.0, 200.0, 200.0, 200.0, 200.0, 200.0, 200.0]]]
```

### Example 2: Writing a NASA Ames file

Start the python interactive prompt:

```pydoc
python
```

Import the nappy package:

```pydoc
>>> import nappy
```

Pretend you have created a complete NASA Ames file contents in a dictionary called `na_contents`.

Write the data to a NASA Ames file:

```pydoc
>>> nappy.openNAFile('my_file_to_write.na', 'w', na_contents)
```

### Example 3: Converting a NASA Ames file to a NetCDF file

*[Note: this utility is only available on Unix/linux platforms]*

Run the command-line utility `na2nc`:

```bash
na2nc -t "seconds since 1999-01-01 00:00:00" -i my_nasa_ames_file.na -o my_netcdf_file.nc
```

Note that the `-t` argument allows you to pass a NetCDF-style data/time units description into your NetCDF that will allow software packages to identify the time axis correctly. This is required when the time unit string in your NASA Ames file is non-standard.

For help on the command-line utility type:

```bash
na2nc -h

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

    <mode>                      is the file mode, either "w" for write or "a" for append
    <global_atts_list>          is a comma-separated list of global attributes to add
    <rename_vars_list>          is a comma-separated list of <old_name>,<new_name> pairs to rename variables
    <time_units>                is a valid time units string such as "hours since 2003-04-30 10:00:00"
    -n                          suppresses the time units warning if invalid
    <na_file>                   is the input NASA Ames file path
    <nc_file>                   is the output NetCDF file path (default is to replace ".na" from NASA Ames
                                 file with ".nc").
```

### Example 4: Converting a NetCDF file to a NASA Ames file

*[Note: this utility is only available on Unix/linux platforms]*

Run the command-line utility `nc2na`:

```bash
nc2na -i my_netcdf_file.nc -o my_nasa_ames_file.na
```

For help on the command-line utility type:

```bash
nc2na -h

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

    <nc_file>                   - name of input file (NetCDF).
    <na_file>                   - name of output file (NASA Ames or CSV) - will be used as base name if multiple files.
    <var_list>                  - a comma-separated list of variables (i.e. var ids) to include in the output file(s).
    <ffi>                       - NASA Ames File Format Index (FFI) to write to (normally automatic).
    <float_format>              - a python formatting string such as %s, %g or %5.2f
    <delimiter>                 - the delimiter you wish to use between data items in the output file such as "   " or "    "
    <limit_ffi_1001_rows>       - if format FFI is 1001 then chop files up into <limitFFI1001Rows> rows of data.
    <exclude_vars>              - a comma-separated list of variables (i.e. var ids) to exclude in the output file(s).
    <key1>,<value1>[,<key2>,<value2>[...]] - list of comma-separated key,value pairs to overwrite in output files:
                                                                * Typically the keys are in:
                                   * "DATE", "RDATE", "ANAME", "MNAME","ONAME", "ORG", "SNAME", "VNAME".
    --names-only                - only display a list of file names that would be written (i.e. don't convert actual files).
    --no-header                 - Do not write NASA Ames header
    --annotated                 - add annotation column in first column
```
