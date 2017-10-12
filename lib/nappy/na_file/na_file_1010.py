#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
naFile1010.py
=============

Container module for NAFile1010 class.

"""

# 08/05/04 updated by selatham for bug fixes and new write methods

# Imports from python standard library

# Imports from local package
import nappy.utils.text_parser
import nappy.na_file.na_file_1001
import nappy.utils.common_utils
wrapLine = nappy.utils.common_utils.annotateLine
wrapLines = nappy.utils.common_utils.annotateLines

class NAFile1010(nappy.na_file.na_file.NAFile):
    """
    Class to read, write and interact with NASA Ames files conforming to the
    File Format Index (FFI) 1010.
    """

    def readHeader(self):
        """
        Reads FFI-specifc header section.
        """        
        self._readCommonHeader()
        self.DX = nappy.utils.text_parser.readItemsFromLine(self.file.readline(), self.NIV, float)
        self.XNAME = nappy.utils.text_parser.readItemsFromLines(self._readLines(self.NIV), self.NIV, str)
        self._readVariablesHeaderSection()
        self._readAuxVariablesHeaderSection()
        self._readComments()

    def writeHeader(self):								
        """											
        Writes FFI-specifc header section.					
        """   											
        self._writeCommonHeader()   						
        self.header.write(wrapLine("DX", self.annotation, self.delimiter, ("%s " * self.NIV + "\n") % tuple(self.DX)))
        self.header.write(wrapLines("XNAME", self.annotation, self.delimiter, ("%s\n") * self.NIV % tuple(self.XNAME)))
        self._writeVariablesHeaderSection()   					
        self._writeAuxVariablesHeaderSection()   				
        self._writeComments() 							
        self._fixHeaderLength()
        self.file.write(self.header.read())

    def _setupArrays(self):
        """
        Sets up FFI-specific arrays to fill with data (lists of lists).
        """        
        self.X = []
        self.V = []
        self.A = []

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
        self.X.append(x)

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
        (v, rtlines) = nappy.utils.text_parser.readItemsFromUnknownLines(datalines, self.NV, float)              
					
        count = 0
        for n in range(self.NV):				
            self.V[n].append(v[count])							
            count = count + 1

        return rtlines

    def writeData(self):									
         """   											
         Writes the data section of the file.   					
         This method can be called directly by the user.   			
         """   											
         for m in range(len(self.X)):   						
             # Write Independent variable mark and auxiliary variables   	
             var_string = self.format % self.X[m]   
					
             for a in range(self.NAUXV):   						
                 var_string = var_string + (self.format % self.A[a][m])
	
             self.file.write(wrapLine("Data", self.annotation, self.delimiter, "%s\n" % var_string.rstrip(" ,")))	
			
             # Write dependant variables   						
             var_string = ""   								
             for n in range(self.NV):							
                  var_string = var_string + (self.format % self.V[n][m])   	
	
             self.file.write(wrapLine("Data", self.annotation, self.delimiter, "%s\n" % var_string.rstrip(' ,'))) 					
