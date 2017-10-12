"""
ffi_translator.py
=================

Provides a set of functions to do simple mappings between FFIs by altering the required 
parts of the NASA Ames dictionary (na_dict) sent to them.

A good example is the translation of 2010 --> 2110 that requires some re-jigging of the 
ancillary variables (to include NX in the auxiliary variable rows and X values in the 
main data blocks before the actual data).

"""

# Import standard library modules
import copy

# Import local modules
import nappy.utils

default_missing_value = nappy.utils.getConfigDict()["main"]["default_missing_value"]


def translate2010To2110(na_dict):
    """
    Takes a valid na_dict for 2010 and returns a valid na_dict
    object for 2110.
    NOTE: this is a constrained version of 2110 that does not include
    the "ragged array" structures that are allowed.
    """
    n = copy.deepcopy(na_dict)

    # First need to adjust auxiliary variable definitions and array
    nx1 = n.NX[0]
    n.NAUXV = n.NAUXV + 1
    axis_1_name = n.XNAMES[0]
    n.ANAMES = ["Number of %s values recorded in subsequent data records" % axis_1_name] + n.ANAMES
    n.ASCAL.insert(0, 1.0)
    n.AMISS.insert(0, default_missing_value)
   
    return n   # did it work?



 

    