#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
naFile2010.py
=============

Container module for NAFile2010 class.

"""

# Imports from python standard library

# Imports from local package
import nappy.utils.text_parser
import nappy.utils.list_manipulator
import nappy.na_file.na_file
import nappy.utils.common_utils
wrapLine = nappy.utils.common_utils.annotateLine
wrapLines = nappy.utils.common_utils.annotateLines


class NAFile2010(nappy.na_file.na_file.NAFile):
    """
    Class to read, write and interact with NASA Ames files conforming to the
    File Format Index (FFI) 2010.
    """

    def readHeader(self):
        """
        Reads FFI-specifc header section.
        """        
        self._normalized_X = False
        self._readCommonHeader()
        self.DX = nappy.utils.text_parser.readItemsFromLine(self.file.readline(), self.NIV, float)
        self.DX.reverse()  # Reverse because C-type array is least-changing first
        self.NX = nappy.utils.text_parser.readItemsFromLine(self.file.readline(), self.NIV - 1, int)
        self.NX.reverse()  # Reverse because C-type array is least - changing first
        self.NXDEF = nappy.utils.text_parser.readItemsFromLine(self.file.readline(), self.NIV - 1, int)
        self.NXDEF.reverse()  # Reverse because C-type array is least-changing first
        self.X = []
        for i in range(self.NIV - 1):
            self.X.append(nappy.utils.text_parser.readItemsFromUnknownLines(self.file, self.NXDEF[i], float))
        # Unbounded Independent variable should be first so insert empty list at start
        self.X.reverse()                 
        self.X.insert(0, [])
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
        NX = self.NX
        NX.reverse()
        self.header.write(wrapLine("NX", self.annotation, self.delimiter, (("%s" + self.delimiter) * (self.NIV - 2) + "%s\n") % tuple(NX)))
        NXDEF = self.NXDEF[:]
        NXDEF.reverse()
        self.header.write(wrapLine("NXDEF", self.annotation, self.delimiter, (("%s" + self.delimiter) * (self.NIV - 2) + "%s\n") % tuple(NXDEF)))

        X_lines = []

        for i in range(self.NIV - 1):
            X_lines.append((self.format * self.NXDEF[i] % tuple(self.X[i + 1][0:self.NXDEF[i]])).rstrip(" ,") + "\n")

        X_lines.reverse()
        for line in X_lines:
            self.header.write(wrapLine("X", self.annotation, self.delimiter, line.lstrip()))

        XNAME = self.XNAME[:]
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

        # Create an array size to request using read routines
        self.arraySize = 1
        for i in self.NX:
            self.arraySize = self.arraySize * i
        for n in range(self.NV):
            self.V.append([])
        for a in range(self.NAUXV):
            self.A.append([])
            
    def _readData1(self, datalines, ivar_count):
        """
        Reads first line/section of current block of data.
        """        
        # Start with independent and Auxilliary vars
        (x2_and_a, rtlines) = nappy.utils.text_parser.readItemsFromUnknownLines(datalines, 1 + self.NAUXV, float)
        (x, aux) = (x2_and_a[0], x2_and_a[1:])
        self.X[0].append(x)
        count = 0
        for a in range(self.NAUXV):
            self.A[a].append(aux[count])
            count = count + 1
        return rtlines

    def _readData2(self, datalines, ivar_count):
        """
        Reads second line/section (if used) of current block of data.
        """
        # Now get the dependent variables
        for n in range(self.NV):
            (v, rtlines) = nappy.utils.text_parser.readItemsFromUnknownLines(datalines, self.arraySize, float)
            self.V[n].append([])
            nappy.utils.list_manipulator.recursiveListPopulator(self.V[n][ivar_count], v, self.NX)
            datalines = rtlines
        return rtlines

    def writeData(self):
        """
        Writes the data section of the file.
        This method can be called directly by the user.
        """        
        # Set up unbounded IV loop
        self.NX.reverse()
        for m in range(len(self.X[0])):

            # Write unbounded independent variable mark and auxiliary variables
            var_string = self.format % self.X[0][m]

            for a in range(self.NAUXV):
                var_string = var_string + (self.format % self.A[a][m])
            self.file.write(wrapLine("Data", self.annotation, self.delimiter, "%s\n" % var_string.rstrip(" ,")))
            
            # Write Variables
            for n in range(self.NV):
                outlines = nappy.utils.list_manipulator.recursiveListWriter(self.V[n][m], self.NX, delimiter = self.delimiter, float_format = self.float_format)
                for line in outlines:
                    self.file.write(wrapLine("Data", self.annotation, self.delimiter, line))

    def _normalizeIndVars(self):
        """
        Normalizes the values in the unbounded independent variable for FFIs
        that store an abbreviated version of this axis.
        """
        for i in range(self.NIV - 1):
            if self.NXDEF[i] == self.NX[i]:
                pass
            else:
                del self.X[i + 1][1:]
                count = 0
                while len(self.X[i + 1])<self.NX[i]:
                    nextx = self.X[i + 1][count] + self.DX[i + 1]
                    self.X[i + 1].append(nextx)
                    count = count + 1
        self._normalized_X = True
