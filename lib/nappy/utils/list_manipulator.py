#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
listManipulator.py
===================

Contains a set of list-related functions and the RecursiveListManipulator 
class that is wrapped in nice functions. This class transforms
arrays into multi-dimensional list objects. Wrapper functions are
provided to call these directly as functions.

"""

# Import local modules
import nappy.utils

# Define module variables
default_delimiter = nappy.utils.getDefault("default_delimiter")
default_float_format = nappy.utils.getDefault("default_float_format")


def arrayToList(array, inlist):
    """ 
    Takes an n-dimensional Numeric array and converts it to an 
    n-dimensional list object.
    """
    dimlist = array.shape
    if len(dimlist[1:]) > 0:
        for i in range(dimlist[0]):
            arrayToList(inlist[i], array[i])
    else:
        for i in range(dimlist[0]):
            inlist.append(array[i])
    return inlist


def listOfListsCreator(inlist, dimlist):
    """
    Creates a list of lists with dimensions defined in dimlist (a list of integers).
    """
    if len(dimlist[1:]) > 0:
        for i in range(dimlist[0]):
            inlist.append([])
            listOfListsCreator(inlist[i], array, dimlist[1:])
    return inlist


def recursiveListPopulator(inlist, array, dimlist):
    "Function wrapper around class method RecursiveListManipulator().populator()."
    return RecursiveListManipulator().populator(inlist, array, dimlist)


def recursiveListWriter(inlist, dimlist, delimiter=default_delimiter, float_format=default_float_format):
    "Function wrapper around class method RecursiveListManipulator().writeLines()."
    return RecursiveListManipulator().writeLines(inlist, dimlist, delimiter=delimiter, float_format=float_format)


class RecursiveListManipulator:
    """
    Container class with methods to convert a 1-D array into a multi-dimensional list.
    """

    def populator(self, inlist, array, dimlist):    
        """
        Populates the list object 'inlist' (e.g. []) with sublists of
        dimensionality defined in the 'dimlist' list of dimensions (e.g [181, 360]).
        At the deepest level it then inserts values from the long list
        'array'.
        """

        if not hasattr(self, "_counter"):
            self._counter = 0
        if len(dimlist[1:]) > 0:
            for i in range(dimlist[0]):
                inlist.append([])
                self.populator(inlist[i], array, dimlist[1:])
        else:
            count = self._counter
            self._counter = self._counter + dimlist[0]
            endcount = self._counter
            for i in range(count, endcount):
                inlist.append(array[i])
        return inlist

    def writeLines(self, inlist, dimlist, delimiter=default_delimiter, float_format=default_float_format):
        """
        Method to walk through all the levels of the multi-level list object
        'inlist' and writes out appropriate values to a list of lines called
        'self.rtlines'. 'dimlist' is a list of the dimensions within 'inlist'.
        """
        if not hasattr(self, "rtlines"):
            self.rtlines = []
        if len(dimlist[1:]) > 0:
            for i in range(dimlist[0]):
                self.writeLines(inlist[i], dimlist[1:], delimiter=delimiter, float_format=float_format)
        else:
            var_string = ""
            for i in range(dimlist[0]):
                var_string = var_string + ((float_format+delimiter) % inlist[i])
            self.rtlines.append("%s\n" % var_string.rstrip(" ,"))
        return self.rtlines
            
