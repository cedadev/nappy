#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
naFile2160.py
=============

Container module for NAFile2160 class.

"""

# Imports from python standard library

# Imports from local package
import nappy.utils.text_parser
import nappy.na_file.na_file_2110
import nappy.utils.common_utils
wrapLine = nappy.utils.common_utils.annotateLine
wrapLines = nappy.utils.common_utils.annotateLines

class NAFile2160(nappy.na_file.na_file_2110.NAFile2110):
    """
    Class to read, write and interact with NASA Ames files conforming to the
    File Format Index (FFI) 2160.
    """

    def readHeader(self):
        """
        Reads FFI-specifc header section.
        """
        self._normalized_X = False
        self._readCommonHeader()
        self.DX = nappy.utils.text_parser.readItemsFromLine(self.file.readline(), 1, float)
        self.LENX = nappy.utils.text_parser.readItemFromLine(self.file.readline(), float)
        self.XNAME = nappy.utils.text_parser.readItemsFromLines(self._readLines(self.NIV), self.NIV, str)
        self.XNAME.reverse()  # Reverse because C-type array is least-changing first
        self._readVariablesHeaderSection()
        self._readCharAuxVariablesHeaderSection()
        self._readComments()

    def writeHeader(self):
        """
        Writes FFI-specific header section.
        """
        self._writeCommonHeader()
        DX = self.DX
        DX.reverse()
        self.header.write(wrapLine("DX", self.annotation, self.delimiter, "%s\n" % tuple(DX)))
        self.header.write(wrapLine("LENX", self.annotation, self.delimiter, "%s\n" % self.LENX))
        XNAME = self.XNAME
        XNAME.reverse()
        self.header.write(wrapLines("XNAME", self.annotation, self.delimiter, "%s\n" * self.NIV % tuple(XNAME)))
        self._writeVariablesHeaderSection()
        self._writeAuxVariablesHeaderSection()
        self._writeComments()
        self._fixHeaderLength()
        self.file.write(self.header.read())

    def _writeAuxVariablesHeaderSection(self):
        """
        Writes the auxiliary variables section of the header for FFI 2160.
        Assumes we are at the right point in the file.
        """
        self.header.write(wrapLine("NAUXV", self.annotation, self.delimiter, "%d\n" % self.NAUXV))
        self.header.write(wrapLine("NAUXC", self.annotation, self.delimiter, "%d\n" % self.NAUXC))
        if self.NAUXV > 0:
            line = (("%s" + self.delimiter) * (self.NAUXV - self.NAUXC - 1) + "%s\n")  % tuple(self.ASCAL)
            self.header.write(wrapLine("ASCAL", self.annotation, self.delimiter, line))
            line = (("%s" + self.delimiter) * (self.NAUXV - self.NAUXC - 1) + "%s\n")  % tuple(self.AMISS[0:(self.NAUXV - self.NAUXC)])
            self.header.write(wrapLine("AMISS", self.annotation, self.delimiter, line))
            line = (("%s" + self.delimiter) * (self.NAUXC - 1) + "%s\n") % tuple(self.LENA[(self.NAUXV - self.NAUXC):])
            self.header.write(wrapLine("LENA", self.annotation, self.delimiter, line))
            line = ("%s\n" * self.NAUXC) % tuple(self.AMISS[(self.NAUXV - self.NAUXC):])
            self.header.write(wrapLines("AMISS", self.annotation, self.delimiter, line))
            line = "%s\n" * self.NAUXV % tuple(self.ANAME)
            self.header.write(wrapLines("ANAME", self.annotation, self.delimiter, line))

    def _setupArrays(self):
        """
        Sets up FFI-specific arrays to fill with data (lists of lists).
        """
        self.V = []
        self.A = []
        self.X = []
        self.NX = []
        
        for n in range(self.NV):
            self.V.append([])
        for i in range(self.NAUXV):
            self.A.append([])

    def _readData1(self, datalines, ivar_count):
        """
        Reads first line/section of current block of data.
        """      
        # Start with independent and Auxilliary vars
        # Get character string independent variable
        (x1, datalines) = nappy.utils.text_parser.readItemsFromUnknownLines(datalines, 1, str)
	self.X.append([])
        self.X[ivar_count].append(x1[0])
        # Set up list to take second changing independent variable
        self.X[ivar_count].append([])  

        # Get NX and Non-character AUX vars
        (aux, datalines) = nappy.utils.text_parser.readItemsFromUnknownLines(datalines, (self.NAUXV - self.NAUXC), float)
        self.NX.append(int(aux[0]))

        count = 0
        for a in range(self.NAUXV - self.NAUXC):
            self.A[a].append(aux[count])
            count = count + 1

        # Get character AUX vars
        (auxc) = nappy.utils.text_parser.readItemsFromLines(datalines[:self.NAUXC], self.NAUXC, str)
        rtlines = datalines[self.NAUXC:]
        count = 0
        for a in range(self.NAUXC):
            self.A[(self.NAUXV - self.NAUXC) + a].append(auxc[count])
            count = count + 1

        return rtlines
    
    def writeData(self):
        """
        Writes the data section of the file.
        This method can be called directly by the user.
        """
        # Set up unbounded IV loop
        for m in range(len(self.X)):

            # Write Independent variable mark and auxiliary variables
            var_string = "%s" % self.X[m][0]
            self.file.write(wrapLine("Data", self.annotation, self.delimiter, "%s\n" % var_string.rstrip(" ,")))
            var_string = ""

            for a in range(self.NAUXV - self.NAUXC):
                var_string = var_string + (self.format % self.A[a][m])

            self.file.write(wrapLine("Data", self.annotation, self.delimiter, "%s\n" % var_string.rstrip(" ,")))

            for a in range(self.NAUXC):
                var_string = (("%s" + self.delimiter) % self.A[(self.NAUXV - self.NAUXC) + a][m])
                self.file.write(wrapLine("Data", self.annotation, self.delimiter, "%s\n" % var_string.rstrip(" ,")))

            # Write second independant variable and dependant variables
            for p in range(self.NX[m]):
                var_string = self.format % self.X[m][1][p]

                for n in range(self.NV):
                    var_string = var_string + (self.format % self.V[n][m][p])

                self.file.write(wrapLine("Data", self.annotation, self.delimiter, "%s\n" % var_string.rstrip(" ,")))
