#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
naFile1001.py
=============

Container module for NAFile1001 class.

"""

# Imports from python standard library

# Imports from local package
import nappy.utils.text_parser
import nappy.na_file.na_file
import nappy.utils.common_utils
getAnnotation = nappy.utils.common_utils.getAnnotation
wrapLine = nappy.utils.common_utils.annotateLine
wrapLines = nappy.utils.common_utils.annotateLines


class NAFile1001(nappy.na_file.na_file.NAFile):
    """
    Class to read, write and interact with NASA Ames files conforming to the
    File Format Index (FFI) 1001.
    """

    def readHeader(self):
        """
        Reads FFI-specific header section.
        """
        self._readCommonHeader()
        self.DX = nappy.utils.text_parser.readItemsFromLine(self.file.readline(), self.NIV, float)
        self.XNAME = nappy.utils.text_parser.readItemsFromLines(self._readLines(self.NIV), self.NIV, str)
        self._readVariablesHeaderSection()
        self._readComments()

    def writeHeader(self):
        """
        Writes FFI-specific header section.
        """        
        self._writeCommonHeader()
        annotation = getAnnotation("DX", self.annotation, delimiter = self.delimiter)
        self.header.write((annotation + "%s" * self.NIV + "\n") % tuple(self.DX))
        annotation = getAnnotation("XNAME", self.annotation, delimiter = self.delimiter)
        self.header.write((annotation + "%s\n") * self.NIV % tuple(self.XNAME))
        self._writeVariablesHeaderSection()
        self._writeComments()
        self._fixHeaderLength()
        self.file.write(self.header.read())

    def _setupArrays(self):
        """
        Sets up FFI-specific arrays to fill with data (lists of lists).
        """
        self.X = []
        self.V = []
        # Set up the variables list
        for n in range(self.NV):
            self.V.append([])

    def _readData1(self, datalines, ivar_count):
        """
        Reads first line/section of current block of data.
        """
        (x_and_v, rtlines) = nappy.utils.text_parser.readItemsFromUnknownLines(datalines, 1 + self.NV, float)
        (x, v) = (x_and_v[0], x_and_v[1:])
        self.X.append(x)
        count = 0
        # Set up mth list in self.V
        for n in range(self.NV):
            self.V[n].append(v[count])
            count = count + 1
        return rtlines    

    def _readData2(self, datalines, ivar_count):
        """
        Reads second line/section (if used) of current block of data.
        """
        return datalines  

    def writeData(self):
        """
        Writes the data section of the file.
        This method can be called directly by the user.
        """
        for m in range(len(self.X)):

            var_string = self.format % self.X[m]

            for n in range(self.NV):
                var_string = var_string + (self.format % self.V[n][m])

            self.file.write(wrapLine("Data", self.annotation, self.delimiter, "%s\n" % var_string.rstrip(" ,")))
