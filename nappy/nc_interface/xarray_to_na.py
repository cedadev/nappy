#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
xarray_to_na.py
===============

Holds the class XarrayToNA that converts a set of Xarray variables (DataArrays) and global attributes.

"""

# Imports from python standard library
import sys
import logging

import xarray as xr
import numpy as np

# Import from nappy package
import nappy
import nappy.utils
from nappy.utils.common_utils import modifyNADictCopy, get_rank_zero_array_value

import nappy.na_file.na_core

from . import xarray_utils
from . import na_content_collector

# Define global variables
DEBUG = nappy.utils.getDebug() 
default_delimiter = nappy.utils.getDefault("default_delimiter")
default_float_format = nappy.utils.getDefault("default_float_format")
comment_override_rule = nappy.utils.getDefault("comment_override_rule")
add_column_headers = bool(nappy.utils.getDefault("add_column_headers"))

config_dict = nappy.utils.getConfigDict()
header_partitions = config_dict["header_partitions"]
hp = header_partitions

permitted_overwrite_metadata = ("DATE",  "RDATE", "ANAME", "MNAME",
           "ONAME", "ORG", "SNAME", "VNAME", "SCOM", "NCOM")
items_as_lists = ["DATE", "RDATE", "ANAME", "VNAME"]

var_limit = 5000 # surely never going to get this many vars in a file!

DEBUG = nappy.utils.getDebug() 

log = logging.getLogger(__name__)


class XarrayToNA:
    """
    Converts Xarray objects to NASA Ames file dictionaries.
    """

    def __init__(self, xr_variables, global_attributes=None, na_items_to_override=None, 
                 only_return_file_names=False, requested_ffi=None):
        """
        Sets up instance variables. 
        """
        self.xr_variables = xr_variables
        self.global_attributes = global_attributes or []
        self.na_items_to_override = na_items_to_override or {}
        self.only_return_file_names = only_return_file_names
        self.requested_ffi = requested_ffi

        self.converted = False
        self.na_dict_list = []
        self.output_message = []
    
    def convert(self):
        """
        Reads the Xarray objects and convert to a set of dictionaries that
        provide the structure for a NA File object.
        Returns [(na_dict, var_ids), (na_dict, var_ids), ....]
        All these na_dict dictionaries can be readily written to a NA File object.

        Note that NASA Ames is not as flexible as NetCDF so you cannot just send any 
        set of variables to write to a NASA Ames file. Essentially there is one
        multi-dimensional structure and all variables must be defined against it.

        Otherwise variables must be auxiliary variables within that structure (i.e. only
        defined once per the least changing dimension.
        """
        if self.converted:
            return self.na_dict_list
        
        # Convert any singleton variables to Xarray variables
        variables = self._convertSingletonVars(self.xr_variables)

        # Re-order variables if they have the attribute "nasa_ames_var_number" which means they came
        # from a NASA Ames file originally
        variables = self._reorderVars(variables)

        # Make first call to collector class that creates NA dict from Xarray variables and global atts list 
        collector = nappy.nc_interface.na_content_collector.NAContentCollector(variables, 
                                        self.global_attributes, requested_ffi=self.requested_ffi)
        collector.collectNAContent()

        # Return if no files returned
        if not collector.found_na:
            msg = "\nNo files created after variables parsed."
            if DEBUG: log.debug(msg)
            self.output_message.append(msg)
            return None

        # NOTE: collector has attributes: na_dict, var_ids, unused_vars

        # Set up a list to collect multiple calls to content collector
        na_dict_list = [(collector.na_dict, collector.var_ids)]

        # If there are variables that were not captured (i.e. unused) by NAContentCollector then loop through these
        # in attempt to convert all to a set of na_dicts
        log.debug(f"\nUnused_vars: {collector.unused_vars}")
        while len(collector.unused_vars) > 0:
            collector = nappy.nc_interface.na_content_collector.NAContentCollector(collector.unused_vars, 
                                        self.global_attributes, requested_ffi=self.requested_ffi,
                                        )
            collector.collectNAContent()           
            self.output_message += collector.output_message

            # Append to list if more variables were captured
            if collector.found_na:
                na_dict_list.append((collector.na_dict, collector.var_ids))

        self.na_dict_list = na_dict_list
        self.converted = True

        return self.na_dict_list

    def _convertSingletonVars(self, variables):
        """
        Loops through variables to convert singleton variables (i.e. Masked Arrays/Numeric Arrays) 
        to proper Xarray variables. Then code won't break when asking for rank attribute later.
        Returns a list of Xarray variable objects
        """
        vars = []

        for variable in variables:
            var_obj = variable

            # If singleton variable then convert into proper Xarray variables so code doesn't break later
            if not hasattr(var_obj, "rank") or len(var_obj.shape) == 0:
              
                var_metadata = var_obj.attrs
                var_obj = xr.DataArray(np.array(var_obj), 
                                   name=xarray_utils.getBestName(var_obj), ###.replace(" ", "_"), 
                                   attrs=var_metadata)
                # Add the single value to the attributes so it will get rendered in the NA comments
                var_obj.attrs['value'] = get_rank_zero_array_value(var_obj.values)
                
            vars.append(var_obj)

        return vars

    def _reorderVars(self, variables):
        """
        Returns a reordered list of variables. Any that have the attribute 
        "nasa_ames_var_number" get ordered first in the list (according to numbering).
        """
        # Set up a long list (longer than number of vars)
        if len(variables) > var_limit:
            raise Exception("Can only handle converting less than " + var_limit + " variables in any batch.")

        # Collect up those that are ordered and unordered
        ordered_vars = [None] * var_limit
        unordered_vars = []

        # Collect up the dimensions (coordinate variables) that can be excluded when writing to NA
        dim_names = xarray_utils.get_dim_names_for_variables(variables)

        # Set ordered and unordered variables
        for var in variables:

            # Do not define dimensions (coordinate variables) as variables
            if var.name in dim_names:
                continue

            var_metadata = var.attrs

            if hasattr(var_metadata, "nasa_ames_var_number"):
                num = var_metadata.nasa_ames_var_number
                ordered_vars[num] = var
            else:
                unordered_vars.append(var)
    
        ret_variables = []

        # Clear any None values in ordered_vars and place in final vars list
        for var in ordered_vars + unordered_vars:
            # Test for Real var types
            if var is not None: 
                ret_variables.append(var)
	     
        return ret_variables

    def constructNAFileNames(self, na_file=None):
        """
        Works out what the file names of the output NA files will be and 
        returns a list of them.
        """
        if not self.converted:
            self.convert()

        # create file name if not given
        if na_file == None:
            base_name = self.nc_file

            if base_name[-3:] == ".nc":
                base_name = base_name[:-3]
            na_file = base_name + ".na"

        name_parts = na_file.split(".")

        # Now, create some valid file names
        if len(self.na_dict_list) == 1:
            file_names = [na_file]
        else:
            file_names = []

            for file_counter in range(1, len(self.na_dict_list) + 1):
                suffix = f"_{file_counter}"
                new_name = (".".join(name_parts[:-1])) + suffix + "." + name_parts[-1]
                file_names.append(new_name)
	    
        return file_names

    def writeNAFiles(self, na_file=None, delimiter=default_delimiter, annotation=False,
                     float_format=default_float_format, size_limit=None, no_header=False):
        """
        Writes the self.na_dict_list content to one or more NASA Ames files.
        Output file names are based on the self.nc_file name unless specified
        in the na_file_name argument in which case that provides the main name
        that is appended to if multiple output file names are required.
        """
        if not self.converted: 
            self.convert()

        # Gets a list of NA file_names that will be produced.
        file_names = self.constructNAFileNames(na_file)

        # Set up some counters: file_counter is the expected number of files.
        #      full_file_counter includes any files that have been split across multiple output NA files
        #              because size_limit exceeded.
        file_counter = 1
        full_file_counter = 1
        file_list = []

        # Get any NASA Ames dictionary values that should be overwritten with local values
        local_attributes = nappy.utils.getLocalAttributesConfigDict()
        local_na_atts = local_attributes["na_attributes"]

        # define final override list by using defaults then locally provided changes
        # (Take a copy - to avoid changing the config dict - which will persist)
        overriders = local_na_atts.copy()

        for (okey, ovalue) in self.na_items_to_override.items():
            overriders[okey] = ovalue

        # Now loop through writing the outputs
        for na_dict_and_var_ids in self.na_dict_list:
            file_name = file_names[file_counter - 1]
            msg = "\nWriting output NASA Ames file: %s" % file_name

            if DEBUG: log.debug(msg)
            self.output_message.append(msg)

            # Set up current na dict
            (this_na_dict, vars_to_write) = na_dict_and_var_ids

            # Override content of NASA Ames if they are permitted
            for key in overriders:

                if key in permitted_overwrite_metadata:    
                    if key in items_as_lists:
                        new_item = overriders[key].split()		   
                        if key in ("DATE", "RDATE"):
                            new_item = [int(list_item) for list_item in new_item]
                    else:
                        new_item = overriders[key]

                    # Do specific overwrite for comments by inserting lines at start
                    if key in ("SCOM", "NCOM"):

                        # Use rule defined in config file in terms of where to put new comments
                        if comment_override_rule == "replace":
                            comments_list = new_item[:]

                        elif comment_override_rule in ("insert", "extend"):
                            new_comments = new_item[:]
                            existing_comments = this_na_dict.get(key, [])
                            comments_list = self._cleanWrapComments(existing_comments, new_comments, key, comment_override_rule)

                        else:
                            raise Exception(f"Did not recognise comment_override_rule: {str(comment_override_rule)}")

                        this_na_dict[key] = comments_list
                        this_na_dict[f"N{key}L"] = len(comments_list)
		    	 
                    elif key not in this_na_dict or new_item != this_na_dict[key]:
                        this_na_dict[key] = new_item
                        msg = f"Metadata overwritten in output file: '{key}' is now '{this_na_dict[key]}'"
                        if DEBUG: log.debug(msg)
                        self.output_message.append(msg)

            # For certain FFIs create final Normal comments as a list of column headers before data section 
            if add_column_headers:
                self._updateWithColumnHeaders(this_na_dict, delimiter)
        
            # Cope with size limits if specified and FFI is 1001
            # Seems to be writing different chunks of a too long array to different na_dicts to then write to separate files.
            if size_limit is not None and (this_na_dict["FFI"] == 1001 and len(this_na_dict["V"][0]) > size_limit):
                files_written = self._writeNAFileSubsetsWithinSizeLimit(this_na_dict, file_name, delimiter=delimiter,
                                                                        float_format=float_format, size_limit=size_limit,
                                                                        annotation=annotation)
                file_list.extend(files_written)

            # If not having to split file into multiple outputs (normal condition)
            else:		
                log.info("Output NA file name: %s" % file_name)
                x = nappy.openNAFile(file_name, 'w', this_na_dict)
                x.write(delimiter=delimiter, float_format=float_format,
                        no_header=no_header, annotation=annotation)

                x.close()
                file_list.append(file_name)

            # Report on what has been written
            msg = "\nWrote the following variables:" + "\n  " + ("\n  ".join(vars_to_write[0]))
            if DEBUG: log.debug(msg)
            self.output_message.append(msg)
	
            msg = ""
            aux_var_count = vars_to_write[1]
            if len(aux_var_count) > 0:
                msg = "\nWrote the following auxiliary variables:" + "\n  " + ("\n  ".join(aux_var_count))	
	    
            singleton_var_count = vars_to_write[2]
            if len(singleton_var_count) > 0:
                msg = "\nWrote the following Singleton variables:" + "\n  " + ("\n  ".join(singleton_var_count))

            if len(file_list) > 0:
                msg = msg + ("\n\nNASA Ames file(s) written successfully: \n%s" % "\n".join(file_list))

            full_file_counter += len(file_list)
            file_counter += 1

            if DEBUG: log.debug(msg)
            self.output_message.append(msg)
	    
        full_file_count = full_file_counter - 1

        if full_file_count == 1:
            plural = ""
        else:
            plural = "s"
	      
        msg = f"\n{full_file_count} file{plural} written."
    
        if DEBUG: log.debug(msg)
        self.output_message.append(msg)
        self.output_files_written = file_list

        return self.output_message

    def _writeNAFileSubsetsWithinSizeLimit(self, this_na_dict, file_name, delimiter, 
                      float_format, size_limit, annotation):
        """
        If self.size_limit is specified and FFI is 1001 we can chunk the output into 
        different files in a NASA Ames compliant way. 
        Returns list of file names of outputs written.
        """
        file_names = []
        var_list = this_na_dict["V"]
        array_length = len(var_list[0])
        nvol_info = divmod(array_length, size_limit)
        nvol = nvol_info[0]

        # create the number of volumes (files) that need to be written.
        if nvol_info[1] > 0: nvol = nvol + 1

        start = 0
        letter_count = 0
        ivol = 0

        # Loop through until full array length has been written to a set of files.
        while start < array_length:
            ivol = ivol + 1
            end = start + size_limit

            if end > array_length:
                end = array_length

            current_block = []
            # Write new V array
            for v in var_list:
                current_block.append(v[start:end])

            # Adjust X accordingly in the na dictionary, because independent variable has been reduced in size
            na_dict_copy = modifyNADictCopy(this_na_dict, current_block, 
                                                                      start, end, ivol, nvol)
            # Append a letter to the file name for writing this block to
            file_name_plus_letter = f"{file_name[:-3]}-{ivol:03d}.na"
            file_names.append(file_name_plus_letter)

            # Write data to output file
            x = nappy.openNAFile(file_name_plus_letter, 'w', na_dict_copy)
            x.write(delimiter=delimiter, float_format=float_format, annotation=annotation)
            x.close()

            msg = "\nOutput files split on size limit: %s\nFilename used: %s" % (size_limit, file_name_plus_letter)
            if DEBUG: log.debug(msg)
            self.output_message.append(msg)
            letter_count = letter_count + 1
            start = end

            file_names.append(file_name_plus_letter) 

        return file_names

    def _updateWithColumnHeaders(self, na_dict, delimiter):
        """
        Updates the NCOM and NCOML parts of the na_dict so that 
        the last normal comments line is in fact a set of headers 
        for the data section. E.g.:

           UTs     Spd  Direc
           30446.9 305  2592
           20447.9 204  2596

        The 'delimiter' argument is used to separate out the arguments.

        This option is only compatible with a limited range of FFIs and
        only works if there are no Auxiliary variables defined.
        """
        ffi = na_dict["FFI"]
        compatible_ffis = (1001, 1010, 2110)

        if ffi not in compatible_ffis or na_dict["NAUXV"] > 0:
            log.debug(f"Column Headers are not written for FFIs other than: {compatible_ffis}")
            return

        if ffi in (1001, 2110):
            col_names = [na_dict["XNAME"][0]]
        elif ffi in (1010,):
            col_names = []

        col_names.extend(na_dict["VNAME"])
        col_names_line = ",".join(col_names)
        na_dict["NCOM"].append(col_names_line) 
        na_dict["NNCOML"] = len(na_dict["NCOM"])
        return  

    def _cleanWrapComments(self, existing_comments, new_comments, key, comment_override_rule):
        """
        Combines new_comments with existing_comments where comments are
        either Special or Normal. 'key' defines this being defined as either
        "SCOM" or "NCOM". 'comment_override_rule' is either "insert" (new_comments first)
        or "extend" (existing_comments first).
        Returns a new list of combined_comments.
        """
        if not existing_comments:   
            return new_comments

        if not new_comments:        
            return existing_comments

        # Strip start header if used
        c1 = key[0].lower()
        start_line = hp[c1 + "c_start"]
        start_used = False

        if existing_comments[0] == start_line:
            existing_comments = existing_comments[1:]
            start_used = start_line
        
        # Now check last line
        end_line = hp[c1 + "c_end"]
        end_used = False

        if existing_comments[-1] == end_line:
            existing_comments = existing_comments[:-1]
            end_used = end_line

        # Check for alternative last line in NCOM
        if not end_used and key == "NCOM":
            end_line2 = hp["data_next"]
            if existing_comments[-1] == end_line2:
                existing_comments = existing_comments[:-1]
                end_used = end_line2 
       
        # Now put back together
        ordered_comments = [existing_comments, new_comments]
        if comment_override_rule == "insert":
            ordered_comments.reverse() 

        combined_comments = ordered_comments[0] + ordered_comments[1]

        if start_used:
            combined_comments.insert(0, start_used)

        if end_used:
            combined_comments.append(end_used)
    
        return combined_comments


class XarrayDatasetToNA(XarrayToNA):
    """
    Converts an Xarray Dataset to NASA Ames file dictionaries.
    """
    def __init__(self, xr_dset, na_items_to_override=None, 
                 only_return_file_names=False, requested_ffi=None):
        """
        Sets up instance variables and call parent class.
        """
        main_var_keys = list(xr_dset.keys())

        # Also capture variables that are auxiliary coords of main variables 
        # (i.e. they are non-dimension coordinates)
        aux_coord_var_keys = set([coord for var in xr_dset.values() for coord in var.coords.keys() \
                                  if coord not in var.dims])

        # Compile into one list of variable to convert
        xr_variables = [xr_dset[key] for key in main_var_keys]
        xr_variables.extend([xr_dset[key] for key in aux_coord_var_keys \
                             if key not in main_var_keys])

        global_attributes = xr_dset.attrs.copy()

        super().__init__(xr_variables, global_attributes=global_attributes,
                         na_items_to_override=na_items_to_override,
                         only_return_file_names=only_return_file_names,
                         requested_ffi=requested_ffi)

