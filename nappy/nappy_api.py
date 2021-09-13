"""
nappy_api.py
============

Top-level API module that allows user to access most of the useful stuff in
nappy. API examples:

 1. Working with NASA Ames file objects
 2. Converting between formats (NASA Ames, NetCDF and CSV)
 3. Comparing NASA Ames files (and/or CSV files)
 4. General NASA Ames utilities 

 1. Working with NASA Ames file objects

# Start python interactive shell
$ python

# Import the nappy package
import nappy

# Let's open a NASA Ames file and examine its contents
f = nappy.openNAFile("data_files/2010.na")

# Get number of header lines
n_lines = f.getNumHeaderLines()

# Get Organisation from header
org = f.getOrg()
# Get the Normal Comments (SCOM) lines.
norm_comms = f.getNormalComments()

# Get the Special Comments (SCOM) lines.
spec_comms = f.getSpecialComments()

# Get a list of metadata for all main (non-auxiliary or independent) variables
var_list = getVariables()

# Get Auxiliary variable metadata for auxiliary variable number 2
(variable, units, miss, scale) = f.getAuxVariable(2)

# Get scale factor for primary variable number 3
scale_factor = f.getScaleFactor(3)

# Get missing value for primary variable number 1
missing = f.getMissingValue(1)

# Let's get the contents dictionary of the whole file
na_dict = f.getNADict()

# Let's write the na_dict object to a new NASA Ames file
fout = openNAFile("test_outputs/mytest.na", mode="w", na_dict=na_dict)
fout.write()
fout.close()

 2. Converting between formats (NASA Ames, NetCDF and CSV)

# Let's convert a NASA Ames file into a NetCDF file, and add some of our own global attributes
glob_atts = [("Project", "Really important scientific project involving worms"),
             ("Errata": "I meant worm holes!")]
na_file = "data_files/1020.na"
nc_file = "test_outputs/try_1020.nc"
nappy.convertNAToNC(na_file, nc_file, global_attributes=glob_atts)

# Let's convert a NASA Ames file to a CSV and add an annotation column to explain the header
nappy.convertNAToCSV(na_file, annotation=True)

# Let's read a NetCDF and write one (or more) output NASA Ames files,
# but only including and variables "temp" and "ozone". Also let's write 
# the output using tabs as the delimiters and a float format of "%6.3f".
nappy.convertNCToNA("data_files/test1.nc", "test_outputs/test1nc.na", 
              var_ids=("temp", "ozone"), delimiter="\t", float_format="%6.3f")
  
# Let's convert a NetCDF file to one (or more) CSV files and don't write the header at all
nappy.convertNCToCSV("data_files/test1.nc", "test_outputs/test1nc_no_header.csv",
                     no_header=True)

# Let's take some in-memory Xarray objects and write them to one, or more, NASA Ames file(s).
# We need to give it a list of Xarray variables (Data Arrays) and a global attributes list of tuples/lists.
# We also want to instruct nappy to overwrite the content of its 
# MNAME (Mission Name) header line with our specific mission name.
# Also, tell nappy to write the output to NASA Ames file format index (FFI) 2310
# because we know it is compatible.
nappy.convertXarrayObjectsToNA([xr_var_1, xr_var_2], [("Institute", "British Atmospheric Data Centre")], 
              na_file="test_outputs/xr_to_na.na", 
              na_items_to_override={"MNAME": "Atlantic Divergence Mission 2009"}, 
              requested_ffi=2310)

# Let's take a list of Xarray variables and a global attributes list and write
# them to a CSV file.
nappy.convertXarrayObjectsToCSV(xr_vars, global_atttributes, csv_file)

# Let's take a NASA Ames dictionary object, and write it to a NetCDF file
nappy.writeNADictToNC(na_dict, nc_file, mode="w")

# Let's try and write a second na_dict object to the same NetCDF file using mode="a".
nappy.writeNADictToNC(na_dict_2, nc_file, mode="a")

# Now let's read in a NASA Ames file and convert the contents in-memory into
# Xarray objects so that we can manipulate them with NetCDF-compatible tools
(xr_vars_primary, xr_vars_aux, global_attributes) = nappy.readXarrayObjectsFromNA(na_file)

# Actually, I only want to get a single variable from that file, so I'll try
temp_var = getXarrayVariableFromNA(na_file, "temperature")

 3. Comparing NASA Ames files (and/or CSV files)

# I'd like to compare a NASA Ames and CSV file to check they are the same.
# It will allow for different formatting of numbers as long as the values 
# are the same. Compare both header and body by setting as True (default).
result = nappy.compareNA(na_file, csv_file, header=True, body=True, 
            number_clever=True, delimiter_1="    ", delimiter_2=",")

 4. General NASA Ames utilities 

# Get the FFI from a NASA Ames file
ffi = nappy.readFFI(na_file)

# Given a NASA Ames dictionary (na_dict) get an appropriate FFI.
ffi = nappy.chooseFFI(na_dict)


"""

# Import standard library modules
import logging
log = logging.getLogger(__name__)

# Import local modules
import nappy.utils.common_utils
import nappy.utils.compare_na
import nappy.utils.text_parser

# Bring some utils into the API
compareNA = nappy.utils.compare_na.compareNA
readFFI = nappy.utils.common_utils.readFFI
chooseFFI = nappy.utils.common_utils.chooseFFI
getNAFileClass = nappy.utils.common_utils.getNAFileClass
getFileNameWithNewExtension = nappy.utils.common_utils.getFileNameWithNewExtension

__version__ = nappy.utils.common_utils.getVersion()
default_delimiter = nappy.utils.common_utils.getDefault("default_delimiter")
default_float_format = nappy.utils.common_utils.getDefault("default_float_format")


def openNAFile(filename, mode="r", na_dict=None, ignore_header_lines=0):
    """
    Function wrapper around the NASA Ames File classes. Any NASA Ames
    file can be opened through this function and the appropriate read or
    write NASA Ames File class instance is returned.
    """
    if mode == "r":
        ffi = readFFI(filename, ignore_header_lines)
        na_class = getNAFileClass(ffi)
        return na_class(filename, ignore_header_lines, mode)

    elif mode == "w":
        if 'FFI' in na_dict and type(na_dict['FFI']) == type(3):
            ffi = na_dict['FFI']
        else:
            ffi = chooseFFI(na_dict)
            na_dict['FFI'] = ffi
            log.info("\nFormat identified as: %s" % ffi)

        na_class = getNAFileClass(ffi)
        return na_class(filename, mode=mode, na_dict=na_dict)
    else:
        raise Exception("File mode not recognised '" + mode + "'.")


def convertNAToNC(na_file, nc_file=None, mode="w", variables=None, aux_variables=None,
                 global_attributes=None,
                 time_units=None, time_warning=True,
                 rename_variables=None):
    """
    Takes a NASA Ames file and converts to a NetCDF file. Options are:

    na_file - the input NASA Ames file.
    nc_file - name for the output NetCDF file (default is to replace ".na" from NASA Ames 
              file with ".nc").
    mode - is the file mode, either "w" for write or "a" for append
    variables - is a list of variable names that you wish to be converted. If not set then 
              nappy will attempt to convert all files.
    aux_var_list - is a list of auxiliary variables names that you wish to be converted. 
              If not set then nappy will use any compatible variables it finds as 
              auxiliary variables.
    global_attributes - is a list of global attributes to add to the output file.
    rename_variables - is a dictionary of {old_name: new_name} variable ID pairs that nappy 
              should use to rename variables before it writes them to file.  
    time_units - is a valid time units string such as "hours since 2003-04-30 10:00:00" to 
              use for time units if there is a valid time axis.
    time_warning - suppresses the time units warning for invalid time units if set to False.
    """
    global_attributes = global_attributes or []
    rename_variables = rename_variables or {}

    arg_dict = vars()

    for arg_out in ("nc_file", "mode"):
        del arg_dict[arg_out]

    import nappy.nc_interface.na_to_nc
    convertor = nappy.nc_interface.na_to_nc.NAToNC(*[], **arg_dict)
    convertor.convert()

    if nc_file == None:
        nc_file = getFileNameWithNewExtension(na_file, "nc")

    convertor.writeNCFile(nc_file, mode)
    return nc_file   
  

def convertNAToCSV(na_file, csv_file=None, annotation=False, no_header=False):
    """
    Reads in a NASA Ames file and writes it out a new CSV file which is identical to the
    input file except that commas are used as the delimiter. Arguments are:

    na_file - NASA Ames file path
    csv_file - CSV file path (default is to replace ".na" from NASA Ames file with ".csv").
    annotation - if set to True write the output file with an additional left-hand column 
                 describing the contents of each header line.
    no_header - if set to True then only the data blocks are written to file.
    """
    fin = openNAFile(na_file)
    fin.readData()
    na_dict = fin.getNADict()
    fin.close()

    if csv_file == None:
        csv_file = getFileNameWithNewExtension(na_file, "csv")

    fout = openNAFile(csv_file, "w", na_dict=na_dict)
    fout.write(delimiter=",", annotation=annotation)
    fout.close()
    return True


def convertNCToNA(nc_file, na_file=None, var_ids=None, na_items_to_override=None,
            only_return_file_names=False, exclude_vars=None,
            requested_ffi=None, delimiter=default_delimiter, float_format=default_float_format, 
            size_limit=None, annotation=False, no_header=False,
            ):
    """
    Takes a NetCDF file and converts the contents to one or more NASA Ames files. 
    Arguments are:

    nc_file - is the name of input file (NetCDF).
    na_file - is the name of output file (default is to replace ".nc" from NASA Ames 
              file with ".na"). If multiple files produced then this name will be used 
              as the base name.
    var_ids - is a list of variables (as ids) to include in the output file(s).
    na_items_to_override - is a dictionary of {key: value} pairs to overwrite in output 
              files. Typically the keys are in:  
              ("DATE", "RDATE", "ANAME", "MNAME","ONAME", "ORG", "SNAME", "VNAME".)
    only_return_file_names - if set to True then only return a list of file names that 
              would be written (i.e. don't convert actual file).
    exclude_vars - is a list of variables (as ids) to exclude in the output file(s).
    requested_ffi - is the NASA Ames File Format Index (FFI) you wish to write to. Note 
              that there are only limited options available depending on the data 
              structures found.
    delimiter - the delimiter you wish to use between data items in the output file such 
              as "   ", "\t" or ",".
    float_format - a python formatting string such as "%s", "%.10g" or "%5.2f" used for 
              formatting floats when written to file.
    size_limit - if format FFI is 1001 then chop files up into size_limit rows of data.
    annotation - if set to True write the output file with an additional left-hand column 
              describing the contents of each header line.
    no_header - if set to True then only the data blocks are written to file.
    """
    na_items_to_override = na_items_to_override or {}
    exclude_vars = exclude_vars or []

    arg_dict = vars()
    for arg_out in ("na_file", "only_return_file_names", "delimiter", "float_format", 
                    "size_limit", "annotation", "no_header"):
        del arg_dict[arg_out]

    if na_file == None:
        na_file =  getFileNameWithNewExtension(nc_file, "na")

    import nappy.nc_interface.nc_to_na
    convertor = nappy.nc_interface.nc_to_na.NCToNA(*[], **arg_dict)
    convertor.convert()

    # If user only wants files then only give them that
    if only_return_file_names:
        return convertor.constructNAFileNames(na_file)
    else:
        convertor.writeNAFiles(na_file, delimiter=delimiter, float_format=float_format, 
                               size_limit=size_limit, annotation=annotation, no_header=no_header)
        log.info(convertor.output_message)
        output_files_written = convertor.output_files_written
        log.info(output_files_written)
        return output_files_written

    
def convertNCToCSV(nc_file, csv_file=None, **arg_dict):
    """
    Reads in a NetCDF file and writes the data out to a CSV file following the
    NASA Ames standard.
    """
    if csv_file == None:
        csv_file = getFileNameWithNewExtension(nc_file, "csv")
        arg_dict["na_file"] = csv_file
        arg_dict["delimiter"] = ","
  
    return convertNCToNA(*[nc_file], **arg_dict)
    

def convertXarrayObjectsToNA(xr_vars, global_attributes, na_file, 
              na_items_to_override=None, requested_ffi=None, delimiter=default_delimiter, 
              float_format=default_float_format, size_limit=None, annotation=False, no_header=False,
              ):
    """
    Takes a list of Xarray variables and a list of global attributes and
    writes them to one or more NASA Ames files. Arguments are:
 
    xr_vars - is a list of Xarray variables
    global_attributes - is a list of (key, value) pairs for header
    na_file - is the name of output file. If multiple files produced then this name will be used
              as the base name.
    na_items_to_override - is a dictionary of {key: value} pairs to overwrite in 
                output files. Typically the keys are in:  
                ("DATE", "RDATE", "ANAME", "MNAME","ONAME", "ORG", "SNAME", "VNAME", "SCOM", "NCOM".)
    requested_ffi - is the NASA Ames File Format Index (FFI) you wish to write to. 
                Note that there are only limited options available depending on the data 
                structures found.
    delimiter - the delimiter you wish to use between data items in the output file 
                such as "   ", "\t" or ",".
    float_format - a python formatting string such as "%s", "%.10g" or "%5.2f" used for 
                formatting floats when written to file.
    size_limit - if format FFI is 1001 then chop files up into size_limit rows of data.
    annotation - if set to True write the output file with an additional left-hand 
                column describing the contents of each header line.
    no_header - if set to True then only the data blocks are written to file.
    """
    na_items_to_override = na_items_to_override or {}

    import nappy.nc_interface.xarray_objs_to_na_file
    convertor = nappy.nc_interface.xarray_objs_to_na_file.XarrayObjectsToNAFile(xr_vars, global_attributes=global_attributes, 
                        na_items_to_override=na_items_to_override, requested_ffi=requested_ffi,
                        )
    convertor.convert()

    na_files = convertor.writeNAFiles(na_file, delimiter=delimiter, float_format=float_format, 
                                      annotation=annotation, no_header=no_header)

    return convertor.output_files_written 


def convertXarrayObjectsToCSV(xr_vars, global_attributes, csv_file, **arg_dict):
    """
    Takes a list of Xarray variables and a global attributes list and
    writes them to one or more CSV files.
    """
    arg_dict["delimiter"] = ","
    return convertXarrayObjectsToNA(*[xr_vars, global_attributes, csv_file], **arg_dict)


def writeNADictToNC(na_dict, nc_file, mode="w"):
    """
    Writes an NASA Ames dictionary object called na_dict to a NetCDF file called nc_file.
    Can set mode="a" or mode="w" to either append to existing nc_file or write new one.
    Note that mode="a" might not always work.
    """
    # Note, this needs to pretend that the na_dict exists, do this by instantiating NACore and cheating...
    import nappy.na_file.na_core
    na_file_obj = nappy.na_file.na_core.NACore()
    na_file_obj.setNADict(na_dict)

    # Fake up some required methods
    def fakeCaller():pass
    na_file_obj.readData = fakeCaller

    import nappy.nc_interface.na_to_xarray
    convertor = nappy.nc_interface.na_to_xarray.NAToXarray(na_file_obj)
    (xr_primary_vars, xr_aux_vars, global_attributes) = convertor.convert()

    # Now write them out
    import xarray as xr

    fout = xr.open_dataset(nc_file, mode=mode)
    for var in (xr_primary_vars + xr_aux_vars):
        fout.write(var)

    # Write global attributes
    for (att, value) in global_attributes:
        setattr(fout, att, value)
        
    fout.close()
    log.info("NetCDF file '%s' written successfully." % file_name)
    return True


def readXarrayObjectsFromNA(na_file):
    """
    Reads the NASA Ames file and converts to Xarray objects.
    Returns a tuple containing:
      * a list of primary NASA Ames variables as Xarray variables
      * a list of auxiliary NASA Ames variables as Xarray variables,
      * a list of global attributes
    """
    xr_var_list = []
    global_attributes = {}

    # Open the NA file
    na_file_obj = openNAFile(na_file)

    import nappy.nc_interface.na_to_xarray
    convertor = nappy.nc_interface.na_to_xarray.NADictToXarrayObjects(na_file_obj)
    (xr_vars_primary, xr_vars_aux, global_attributes) = convertor.convert()

    return (xr_vars_primary, xr_vars_aux, global_attributes)


def getXarrayVariableFromNA(na_file, var):
    """
    Returns a Xarray variable object (TransientVariable) identified by the var argument which
    can either be an integer index in the list of variables or the name of the variable.
    The variable is created from the variables found in the NASA Ames file na_file.
    """
    na_file_obj = openNAFile(na_file)

    import nappy.nc_interface.na_to_xarray
    convertor = nappy.nc_interface.na_to_xarray.NADictToXarrayObjects(na_file_obj, variables=[var])
    (xr_primary_vars, xr_aux_vars, global_attributes) = convertor.convert()

    # Must now be a primary var
    return xr_primary_vars[0]
