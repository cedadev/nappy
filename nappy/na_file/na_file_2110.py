#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
naFile2110.py
=============

Container module for NAFile2110 class.

"""

# Imports from python standard library

# Imports from local package
import nappy.utils.text_parser
import nappy.na_file.na_file_2010
import nappy.utils.common_utils
wrapLine = nappy.utils.common_utils.annotateLine
wrapLines = nappy.utils.common_utils.annotateLines

class NAFile2110(nappy.na_file.na_file_2010.NAFile2010):
    """
    Class to read, write and interact with NASA Ames files conforming to the
    File Format Index (FFI) 2110.
    """

    def readHeader(self):
        """
        Reads FFI-specifc header section.
        """
        self._readCommonHeader()
        self.DX = nappy.utils.text_parser.readItemsFromLine(self.file.readline(), self.NIV, float)
        self.DX.reverse()  # Reverse because C-type array is least-changing first
        self.XNAME = nappy.utils.text_parser.readItemsFromLines(self._readLines(self.NIV), self.NIV, str)
        self.XNAME.reverse()  # Reverse because C-type array is least-changing first
        self._readVariablesHeaderSection()
        self._readAuxVariablesHeaderSection()
        self._readComments()

    def writeHeader(self):
        """
        Writes FFI-specific header section.
        """
        self._writeCommonHeader()
        DX = self.DX
        DX.reverse()
        self.header.write(wrapLine("DX", self.annotation, self.delimiter, (("%s" + self.delimiter) * (self.NIV - 1) + "%s\n") % tuple(DX)))
        XNAME = self.XNAME
        XNAME.reverse()
        self.header.write(wrapLines("XNAME", self.annotation, self.delimiter, "%s\n" * self.NIV % tuple(XNAME)))
        self._writeVariablesHeaderSection()
        self._writeAuxVariablesHeaderSection()
        self._writeComments()
        self._fixHeaderLength()
        self.file.write(self.header.read())


    def _setupArrays(self):
        """
        Sets up FFI-specific arrays to fill with data (lists of lists).
        """
        self.V = []
        self.A = []
        self.X = []  # Needs to be a list of sublists each containing [x0n, [x1n, x1n + 1, x1n + 2....]]
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
        (x_and_a, rtlines) = nappy.utils.text_parser.readItemsFromUnknownLines(datalines, self.NAUXV + 1, float)
        (x, aux) = (x_and_a[0], x_and_a[1:])
        count = 0
        for a in range(self.NAUXV):
            self.A[a].append(aux[count])
            count = count + 1
        #for a in range(self.NAUXV):
            #self.A.append(aux[a])
        self.X.append([])
        self.X[ivar_count].append(x)
        # Set up list to take second changing independent variable
        self.X[ivar_count].append([])  
        self.NX.append(int(aux[0]))
        return rtlines

    def _readData2(self, datalines, ivar_count):
        """
        Reads second line/section (if used) of current block of data.
        """
        # Now get the dependent variables
        for n in range(self.NV):
            self.V[n].append([])

        for c in range(self.NX[ivar_count]):
            (x_and_v, datalines) = nappy.utils.text_parser.readItemsFromUnknownLines(datalines, self.NV + 1, float)
            (x, v) = (x_and_v[0], x_and_v[1:])
            self.X[ivar_count][1].append(x)

            count = 0
            for n in range(self.NV):
                self.V[n][ivar_count].append(v[count])
                count = count + 1

        rtlines = datalines
        return rtlines

    def writeData(self):
        """
        Writes the data section of the file.
        This method can be called directly by the user.
        """
        # Set up unbounded IV loop

        for m in range(len(self.X)):

            # Write unbounded independent variable mark and auxiliary variables
            var_string = self.format % self.X[m][0]

            # Loop through aux vars which includes NX as first aux var
            for a in range(self.NAUXV): 
                var_string = var_string + (self.format % self.A[a][m])
            self.file.write(wrapLine("Data", self.annotation, self.delimiter, "%s\n" % var_string.rstrip(" ,")))

            # Write second independant variable and dependant variables
            for p in range(self.NX[m]):
                var_string = self.format % self.X[m][1][p]

                for n in range(self.NV):
                    var_string = var_string + (self.format %self.V[n][m][p])

                self.file.write(wrapLine("Data", self.annotation, self.delimiter, "%s\n" %var_string.rstrip(" ,")))
