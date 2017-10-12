#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
naFile3010.py
=============

Container module for NAFile3010 class.

"""

# Imports from python standard library

# Imports from local package
import nappy.utils.text_parser
import nappy.na_file.na_file_2010

class NAFile3010(nappy.na_file.na_file_2010.NAFile2010):
    """
    Class to read, write and interact with NASA Ames files conforming to the
    File Format Index (FFI) 3010.
    
    Identical class rules to FFI 2010. Sub-classed for neatness.
    """
    pass

