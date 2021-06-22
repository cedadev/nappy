#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
naFile.py
=========

A containter module for the mixin base class NAFile that is subclassed
for individual FFIs. Each FFI class is held in an individual file.

"""
   
# 08/05/04 updated by selatham for bug fixes and new write methods

# Imports from python standard library
import sys
import time
import re
from io import StringIO

# Imports from nappy package
import nappy.na_file.na_core
import nappy.utils.text_parser
import nappy.utils.common_utils

default_delimiter = nappy.utils.getDefault("default_delimiter")
default_float_format = nappy.utils.getDefault("default_float_format")
getAnnotation = nappy.utils.common_utils.getAnnotation
wrapLine = nappy.utils.common_utils.annotateLine
wrapLines = nappy.utils.common_utils.annotateLines
stripQuotes = nappy.utils.common_utils.stripQuotes


class NAFile(nappy.na_file.na_core.NACore):
    """
    NAFile class is a sub-class of NACore abstract classes.
    NAFile is also an abstract class and should not be called directly.
    
    NAFile holds all the methods that are common to either all or more than
    one NASA Ames FFI class. These methods set up the main read and write
    functionality for the NASA Ames format.

    When a sub-class of NAFile is called with a read ('r' - default) 
    mode the header in the file is automatically read. To read the data
    section the user must call the 'readData' method.
      
    When a sub-class of NAFile is called with the write ('w') mode
    then the file is opened but nothing is written. The user must then 
    send an 'na_dict' object to the 'write' method to write the output.
    The output file is then flushed to ensure the data is written even if 
    the user forgets to close it.
    """

    def __init__(self, filename, ignore_header_lines=0, mode="r", na_dict=None): 
        """
        Initialization of class, decides if user wishes to read or write
        NASA Ames file.
        """
        nappy.na_file.na_core.NACore.__init__(self)
        self.filename = filename
        self._open(mode)

        self.mode = mode
        self.ignore_header_lines = ignore_header_lines
        self.ignored_header_lines = []
        self.na_dict = na_dict or {}

        if self.mode == "r":
            self._normalized_X = True
            self.readHeader()
        elif self.mode == "w":
            # Self flag to check if data written
            self.data_written = False
        else:
            raise "Unknown file mode '%s'." % self.mode

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def _open(self, mode):
        "Wrapper to builtin open file function."
        self.file = open(self.filename, mode)
        self.is_open = True

    def write(self, delimiter=default_delimiter, float_format=default_float_format,
              annotation=False, no_header=False):
        """
        Writes an na_dict to the file and then flushes it to ensure data not 
        being buffered.
        If annotation is True then add annotation column to left of file.
        If no_header is True then suppress writing the header and only write the data section. 
        """ 
        self.delimiter = delimiter
        self.float_format = float_format
        self.format = float_format + delimiter
        self.annotation = annotation
        
        # Raise errors if dangerous behaviour
        if self.mode != "w":
            raise Exception("WARNING: Cannot write to read-only file. Can only write to NA file object when mode='w'.")

        if self.data_written:
            raise Exception("WARNING: Cannot write multiple NASA Ames dictionaries to a single file. Please open a new NASA Ames file instance to write new data to.")

        if not self.is_open:
            raise Exception("WARNING: NASA Ames file instance is closed and cannot be written to.")
   
        # Parse na_dict then write header and data
        self._parseDictionary()
        self.header = StringIO()

        if not no_header:
            self.writeHeader()

        self.writeData()
        self.file.flush()
        
        # Set flag to make sure cannot try and write more data
        self.data_written = True
         
    def close(self):
        "Wrapper to builtin close file function."
        self.file.close()
        self.is_open = False

    def _parseDictionary(self):
        """
        Parser for the optional na_dict argument containing a dictionary
        of NASA Ames internal variables. These are saved as instance attributes
        with the name used in the NASA Ames documentation.
        """
        for i in self.na_dict.keys():
            setattr(self, i, self.na_dict[i])

    def _readTopLine(self):
        """
        Reads number of header lines and File Format Index from top line.
        Also assigns a value to NIV for the number of independent variables
        based on the first character in the FFI.

        Returns NLHEAD and FFI in a tuple.
        """
        (self.NLHEAD, self.FFI) = nappy.utils.text_parser.readItemsFromLine(self.file.readline(), 2, int)
        self.NIV = int(self.FFI/1000)
        return (self.NLHEAD, self.FFI)

    def _readLines(self, nlines):
        "Reads nlines lines from a file and returns them in a list."
        lines = []
        for i in range(nlines):
            lines.append(self.file.readline().strip())
        return lines

    def _checkForBlankLines(self, datalines):
        """
        Searches for empty lines in the middle of the data section and raises
        as error if found. It ignores empty lines at the end of the file but
        strips them out before returning a list of lines for reading.
        """
        empties = None
        count = 0
        rtlines = []
        for line in datalines:
            if line.strip() == "":
                empties = 1
            else:
                if empties == 1:   # If data line found after empty line then raise
                    raise Exception("Empty line found in data section at line: " + str(count))
                else:
                    rtlines.append(line)
            count = count + 1
        return rtlines


    def _readCommonHeader(self):
        """
        Reads the header section common to all NASA Ames files.
        """
        for i in range(self.ignore_header_lines):
            self.ignored_header_lines.append(nappy.utils.text_parser.readItemFromLine(self.file.readline()))
        
        self._readTopLine()
        self.ONAME = nappy.utils.text_parser.readItemFromLine(self.file.readline(), str)
        self.ORG = nappy.utils.text_parser.readItemFromLine(self.file.readline(), str)
        self.SNAME = nappy.utils.text_parser.readItemFromLine(self.file.readline(), str)
        self.MNAME = nappy.utils.text_parser.readItemFromLine(self.file.readline(), str)
        (self.IVOL, self.NVOL) = nappy.utils.text_parser.readItemsFromLine(self.file.readline(), 2, int)
        dates = nappy.utils.text_parser.readItemsFromLine(self.file.readline(), 6, int)
        (self.DATE, self.RDATE) = (dates[:3], dates[3:])
        self.NLHEAD += self.ignore_header_lines

    def _writeCommonHeader(self):
        """
        Writes the header section common to all NASA Ames files.
        """
        # Line 1 if often overwritten at _fixHeaderLength
        self.header.write(wrapLine("NLHEAD_FFI", self.annotation, self.delimiter, "%d%s%d\n" % (self.NLHEAD, self.delimiter, self.FFI)))
        self.header.write(getAnnotation("ONAME", self.annotation, delimiter = self.delimiter) + stripQuotes(self.ONAME) + "\n")
        self.header.write(getAnnotation("ORG", self.annotation, delimiter = self.delimiter) + stripQuotes(self.ORG) + "\n")
        self.header.write(getAnnotation("SNAME", self.annotation, delimiter = self.delimiter) + stripQuotes(self.SNAME) + "\n")
        self.header.write(getAnnotation("MNAME", self.annotation, delimiter = self.delimiter) + stripQuotes(self.MNAME) + "\n")
        self.header.write(wrapLine("IVOL_NVOL", self.annotation, self.delimiter, "%d%s%d\n" % (self.IVOL, self.delimiter, self.NVOL)))
        line = "%d %d %d%s%d %d %d\n" % (self.DATE[0], self.DATE[1], self.DATE[2], self.delimiter, self.RDATE[0], self.RDATE[1], self.RDATE[2])
        self.header.write(wrapLine("DATE_RDATE", self.annotation, self.delimiter, line))

    def _readVariablesHeaderSection(self):
        """
        Reads the variables section of the header.
        Assumes we are at the right point in the file.
        """
        self.NV = nappy.utils.text_parser.readItemFromLine(self.file.readline(), int)
        self.VSCAL = nappy.utils.text_parser.readItemsFromUnknownLines(self.file, self.NV, float)
        self.VMISS = nappy.utils.text_parser.readItemsFromUnknownLines(self.file, self.NV, float)
        self.VNAME = nappy.utils.text_parser.readItemsFromLines(self._readLines(self.NV), self.NV, str)

    def _writeVariablesHeaderSection(self):
        """
        Writes the variables section of the header.
        Assumes we are at the right point in the file.
        """
        self.header.write(wrapLine("NV", self.annotation, self.delimiter, "%d\n" % self.NV))
        self.header.write(wrapLine("VSCAL", self.annotation, self.delimiter, (("%s" + self.delimiter) * (self.NV - 1) + "%s\n") % tuple(self.VSCAL)))
        self.header.write(wrapLine("VMISS", self.annotation, self.delimiter, (("%s" + self.delimiter) * (self.NV - 1) + "%s\n") % tuple(self.VMISS)))
        self.header.write(wrapLines("VNAME", self.annotation, self.delimiter, "%s\n" * self.NV % tuple(self.VNAME)))

    def _readAuxVariablesHeaderSection(self):
        """
        Reads the auxiliary variables section of the header.
        Assumes we are at the right point in the file.
        """
        self.NAUXV = nappy.utils.text_parser.readItemFromLine(self.file.readline(), int)
        if self.NAUXV > 0:        
            self.ASCAL = nappy.utils.text_parser.readItemsFromUnknownLines(self.file, self.NAUXV, float)
            self.AMISS = nappy.utils.text_parser.readItemsFromUnknownLines(self.file, self.NAUXV, float)
            self.ANAME = nappy.utils.text_parser.readItemsFromLines(self._readLines(self.NAUXV), self.NAUXV, str)

    def _writeAuxVariablesHeaderSection(self):
        """
        Writes the auxiliary variables section of the header.
        Assumes we are at the right point in the file.
        """
        self.header.write(wrapLine("NAUXV", self.annotation, self.delimiter, "%d\n" % self.NAUXV))
        if self.NAUXV > 0:
            line = (("%s" + self.delimiter) * (self.NAUXV - 1) + "%s\n")  % tuple(self.ASCAL)
            self.header.write(wrapLine("ASCAL", self.annotation, self.delimiter, line))
            line = (("%s" + self.delimiter) * (self.NAUXV - 1) + "%s\n")  % tuple(self.AMISS)
            self.header.write(wrapLine("AMISS", self.annotation, self.delimiter, line))
            line = "%s\n" * self.NAUXV % tuple(self.ANAME)
            self.header.write(wrapLines("ANAME", self.annotation, self.delimiter, line))

    def _readCharAuxVariablesHeaderSection(self):
        """
        Reads the character-encoded auxiliary variables section of the header.
        Assumes we are at the right point in the file.
        """
        self.NAUXV = nappy.utils.text_parser.readItemFromLine(self.file.readline(), int)
        self.NAUXC = nappy.utils.text_parser.readItemFromLine(self.file.readline(), int)
        nonCharAuxVars = self.NAUXV - self.NAUXC
        if self.NAUXV > 0:
            self.ASCAL = nappy.utils.text_parser.readItemsFromUnknownLines(self.file, nonCharAuxVars, float)
            self.AMISS = nappy.utils.text_parser.readItemsFromUnknownLines(self.file, nonCharAuxVars, float)
            self.LENA = nappy.utils.text_parser.readItemsFromUnknownLines(self.file, self.NAUXC, int)
            for i in range(nonCharAuxVars):
                self.LENA.insert(0, None)
            self.AMISS = self.AMISS + nappy.utils.text_parser.readItemsFromUnknownLines(self.file, self.NAUXC, str)    
            self.ANAME = nappy.utils.text_parser.readItemsFromLines(self._readLines(self.NAUXV), self.NAUXV, str)        
            
    def _readComments(self):
        """
        Reads the special and normal comments sections.
        Assumes we are at the right point in the file.
        """        
        self.NSCOML = nappy.utils.text_parser.readItemFromLine(self.file.readline(), int)
        self._readSpecialComments()
        self.NNCOML = nappy.utils.text_parser.readItemFromLine(self.file.readline(), int)
        self._readNormalComments()

    def _writeComments(self):
        """
        Writes the special and normal comments sections.
        Assumes we are at the right point in the file.
        """
        self.header.write(wrapLine("NSCOML", self.annotation, self.delimiter, "%d\n" % self.NSCOML))
        self.header.write(wrapLines("SCOM", self.annotation, self.delimiter, "%s\n" * self.NSCOML % tuple(self.SCOM)))
        self.header.write(wrapLine("NNCOML", self.annotation, self.delimiter, "%d\n" % self.NNCOML))
        self.header.write(wrapLines("NCOM", self.annotation, self.delimiter, "%s\n" * self.NNCOML % tuple(self.NCOM)))

    def _fixHeaderLength(self):
        """
        Takes the self.header StringIO object and counts the number of lines
        and corrects the NLHEAD value in the header line.
        Resets to start of self.header.
        """
        self.header.seek(0)
        lines = self.header.readlines()
        headlength = len(lines)
        lines[0] = wrapLine("NLHEAD_FFI", self.annotation, self.delimiter, "%d%s%d\n" % (headlength, self.delimiter, self.FFI))
        self.header = StringIO("".join(lines))
        self.header.seek(0) 

    def _readSpecialComments(self):
        """
        Reads the special comments section.        
        Assumes that we are at the right point in the file and that NSCOML
        variable is known.
        """
        self.SCOM = self._readLines(self.NSCOML)
        return self.SCOM

    def _readNormalComments(self):
        """
        Reads the normal comments section.        
        Assumes that we are at the right point in the file and that NNCOML
        variable is known.
        """
        self.NCOM = self._readLines(self.NNCOML)
        return self.NCOM

    def readData(self):
        """
        Reads the data section of the file. This method actually calls a number
        of FFI specific methods to setup the data arrays (lists of lists) and
        read the various data sections.

        This method can be called directly by the user.
        """
        self._setupArrays()

        with open(self.filename) as fh:
            datalines = fh.readlines()[self.NLHEAD:]

        datalines = self._checkForBlankLines(datalines)

        # Set up loop over unbounded indpendent variable
        m = 0   # Unbounded independent variable mark        
        while len(datalines) > 0:
            datalines = self._readData1(datalines, m)
            datalines = self._readData2(datalines, m)
            m = m + 1

