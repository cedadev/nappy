#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
nc_to_na.py
=============

Holds the class NCToNA (sub-classing CDMSToNA) that converts a NetCDF file to
one or more NASA Ames files.

"""

# Imports from python standard library
import sys
import logging

# Import from nappy package
import nappy
from nappy.na_error import na_error
import nappy.utils
import nappy.utils.common_utils
import nappy.nc_interface.cdms_to_na
import nappy.nc_interface.na_content_collector

# Import external packages (if available)
if sys.platform.find("win") > -1:
    raise na_error.NAPlatformError("Windows does not support CDMS. CDMS is required to convert to CDMS objects and NetCDF.")

try:
    import cdms2 as cdms
    import numpy
except:
    try:
        import cdms
        import numpy
    except:
        raise Exception("Could not import third-party software. Nappy requires the CDMS and Numeric packages to be installed to convert to CDMS and NetCDF.")

cdms.setAutoBounds("off") 

# Define global variables
DEBUG = nappy.utils.getDebug() 
default_delimiter = nappy.utils.getDefault("default_delimiter")
default_float_format = nappy.utils.getDefault("default_float_format")
comment_override_rule = nappy.utils.getDefault("comment_override_rule")
add_column_headers = bool(nappy.utils.getDefault("add_column_headers"))

config_dict = nappy.utils.getConfigDict()
header_partitions = config_dict["header_partitions"]
hp = header_partitions

# Define global variables
permitted_overwrite_metadata = ("DATE",  "RDATE", "ANAME", "MNAME",
           "ONAME", "ORG", "SNAME", "VNAME", "SCOM", "NCOM")
items_as_lists = ["DATE", "RDATE", "ANAME", "VNAME"]

logging.basicConfig()
log = logging.getLogger(__name__)

class NCToNA(nappy.nc_interface.cdms_to_na.CDMSToNA):
    """
    Converts a NetCDF file to one or more NASA Ames files.
    """

    def __init__(self, nc_file, var_ids=None, na_items_to_override={}, 
            only_return_file_names=False, exclude_vars=[],
            requested_ffi=None,
            ):
        """
        Sets up instance variables.
        Typical usage is:
        >>>    import nappy.nc_interface.nc_to_na as nc_to_na
        >>>    c = nc_to_na.NCToNA("old_file.nc") 
        >>>    c.convert()
        >>>    c.writeNAFiles("new_file.na", delimiter=",") 

        OR:
        >>>    c = nc_to_na.NCToNA("old_file.nc") 
        >>>    file_names = c.constructNAFileNames() 
        """
        self.nc_file = nc_file

        # Now need to read CDMS file so parent class methods are compatible
        (cdms_variables, global_attributes) = self._readCDMSFile(var_ids, exclude_vars)
        nappy.nc_interface.cdms_to_na.CDMSToNA.__init__(self, cdms_variables, global_attributes=global_attributes, 
                                                        na_items_to_override=na_items_to_override, 
                                                        only_return_file_names=only_return_file_names,
                                                        requested_ffi=requested_ffi)
 

    def _readCDMSFile(self, var_ids=None, exclude_vars=[]):
        """
        Reads the file and returns all the CDMS variables in a list as well
        as the global attributes: (cdms_variable_list, global_atts_list)
        If var_ids is defined then only get those.
        """
        fin = cdms.open(self.nc_file)
        cdms_variables = []

        # Make sure var_ids is a list
        if type(var_ids) == type("string"):
            var_ids = [var_ids]

        for var_id in fin.listvariables():
            if var_ids == None or var_id in var_ids:
                if var_id not in exclude_vars:

                    # Check whether singleton variable, if so create variable
                    vm = fin[var_id]
                    var = fin(var_id)
                   
                    if hasattr(vm, "rank") and vm.rank() == 0:
                        var = cdms.createVariable(numpy.array(float(fin(var_id))), id=vm.id, attributes=vm.attributes)

                    cdms_variables.append(var)

        globals = fin.attributes.items()
        return (cdms_variables, globals) 

    def constructNAFileNames(self, na_file=None):
        """
        Works out what the file names of the output NA files will be and 
        returns a list of them.
        """
        self.convert()

        file_names = []
        # create file name if not given
        if na_file == None:
            base_name = self.nc_file
            if base_name[-3:] == ".nc":
                base_name = base_name[:-3]
            na_file = base_name + ".na"

        file_counter = 1
        # Now, create some valid file names
        for this_na_dict in self.na_dict_list:
            if len(self.na_dict_list) == 1:
                suffix = ""
            else:
                suffix = "_%s" % file_counter

            # Create file name
            name_parts = na_file.split(".")    
            new_name = (".".join(name_parts[:-1])) + suffix + "." + name_parts[-1]
            file_names.append(new_name)
            file_counter += 1
	    
        return file_names

    def writeNAFiles(self, na_file=None, delimiter=default_delimiter, annotation=False,
                     float_format=default_float_format, size_limit=None, no_header=False):
        """
        Writes the self.na_dict_list content to one or more NASA Ames files.
        Output file names are based on the self.nc_file name unless specified
        in the na_file_name argument in which case that provides the main name
        that is appended to if multiple output file names are required.

        TODO: no_header is NOT implemented.
        """
        self.convert() # just in case not already called

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
        overriders = local_na_atts
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
            for key in overriders.keys():

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
                            raise Exception("Did not recognise comment_override_rule: " + str(comment_override_rule))

                        this_na_dict[key] = comments_list
                        this_na_dict["N%sL" % key] = len(comments_list)
		    	 
                    elif not this_na_dict.has_key(key) or new_item != this_na_dict[key]:
                        this_na_dict[key] = new_item
                        msg = "Metadata overwritten in output file: '%s' is now '%s'" % (key, this_na_dict[key])
                        if DEBUG: log.debug(msg)
                        self.output_message.append(msg)

            # For certain FFIs create final Normal comments as a list of column headers before data section 
            if add_column_headers == True:
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
                x.write(delimiter=delimiter, float_format=float_format, annotation=annotation)
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
        msg = "\n%s file%s written." % (full_file_count, plural)
    
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
            na_dict_copy = nappy.utils.common_utils.modifyNADictCopy(this_na_dict, current_block, 
                                                                      start, end, ivol, nvol)
            # Append a letter to the file name for writing this block to
            file_name_plus_letter = "%s-%.3d.na" % (file_name[:-3], ivol)
            file_list.append(file_name_plus_letter)

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
            log.debug("Column Headers are not written for FFIs other than: %s" % str(compatible_ffis))
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
        if existing_comments == []:   return new_comments
        if new_comments == []:        return existing_comments

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
        if end_used == False and key == "NCOM":
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

