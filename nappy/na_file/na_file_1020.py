#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
naFile1020.py
=============

Container module for NAFile1020 class.

"""

# Imports from python standard library


# Imports from local package
import nappy.utils.text_parser
import nappy.na_file.na_file_1010
import nappy.utils.common_utils
wrapLine = nappy.utils.common_utils.annotateLine
wrapLines = nappy.utils.common_utils.annotateLines

class NAFile1020(nappy.na_file.na_file_1010.NAFile1010):
    """
    Class to read, write and interact with NASA Ames files conforming to the
    File Format Index (FFI) 1020.
    """

    def readHeader(self):
        """
        Reads FFI-specifc header section.
        """    
        self._normalized_X = False
        self._readCommonHeader()
        self.DX = nappy.utils.text_parser.readItemsFromLine(self.file.readline(), self.NIV, float)
        if self.DX == 0:
            raise "DX found to be zero (0). Not allowed for FFI 1020."

        self.NVPM = nappy.utils.text_parser.readItemFromLine(self.file.readline(), int)
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
        self.header.write(wrapLine("NVPM", self.annotation, self.delimiter, ("%s\n") %self.NVPM))							
        self.header.write(wrapLine("XNAME", self.annotation, self.delimiter, ("%s\n") * self.NIV % tuple(self.XNAME)))
        self._writeVariablesHeaderSection()   						
        self._writeAuxVariablesHeaderSection()   						
        self._writeComments() 								
        self._fixHeaderLength()
        self.file.write(self.header.read())

    def _readData2(self, datalines, ivar_count):
        """
        Reads second line/section (if used) of current block of data.
        """
        # Now get the dependent variables
        (v, rtlines) = nappy.utils.text_parser.readItemsFromUnknownLines(datalines, self.NV * self.NVPM, float)              
        count = 0
        for n in range(self.NV):
            for i in range(self.NVPM):   # Number of steps where independent variable is implied
                self.V[n].append(v[count])
                count = count + 1
        return rtlines

    def _normalizeIndVars(self):
        """
        Normalizes the values in the unbounded independent variable for FFIs
        that store an abbreviated version of this axis.
        """
        if self._normalized_X: return
        newX = []
        for x in self.X[0]:
            for i in range(self.NVPM):
                newX.append(x + (i * self.DX))

        self.X[0] = newX
        self._normalized_X = True

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
            count = 0											
            for n in range(self.NV):									
                var_string = ""	
								        
                for p in range(self.NVPM):								
                    var_ind = (m * self.NVPM) + p 							
                    var_string = var_string + (self.format % self.V[n][var_ind])   		
                    count = count + 1	
								
                self.file.write(wrapLine("Data", self.annotation, self.delimiter, "%s\n" %var_string.rstrip(' ,')))

