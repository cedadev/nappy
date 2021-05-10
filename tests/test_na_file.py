"""
test_na_file.py
===============

Tests for the reading and writing all the NAFile classes:

1001 1010 1020 2010 2110 2160 2310 3010 4010 

"""

# Import standard library modules
import os
import sys

import pytest

from .common import data_files, test_outputs
import nappy
import nappy.utils.compare_na


_FFIS = (1001, 1010, 1020, 2010, 2110, 2160, 2310, 3010, 4010)


@pytest.mark.parametrize("ffi", _FFIS)
def test_na_file(ffi):

    # Set up the paths 
    infile = os.path.join(data_files, f"{ffi}.na")
    outfile = os.path.join(test_outputs, f"test_{ffi}.na")
    out_csv = os.path.join(test_outputs, f"test_{ffi}.csv")
    out_csv_annotated = os.path.join(test_outputs, "test_2010_annotated.csv")

    # Read the NASA Ames file
    fin = nappy.openNAFile(infile)
    fin.readData()
    na_dict = fin.getNADict()        

    # Test content
    assert isinstance(na_dict, dict)

    # Test writing to file
    fobj = nappy.openNAFile(outfile, mode="w", na_dict=na_dict)		
    fobj.write()
    assert isinstance(fobj, nappy.na_file.na_file.NAFile)

    # Test conversion to CSV
    fobj = nappy.openNAFile(out_csv, mode="w", na_dict=na_dict)
    fobj.write(delimiter=",", float_format="%.6f")
    assert isinstance(fobj, nappy.na_file.na_file.NAFile)

    # Test conversion to Annotated CSV
    fobj = nappy.openNAFile(out_csv_annotated, mode="w", na_dict=na_dict)
    fobj.write(delimiter=",", annotation=True)
    assert isinstance(fobj, nappy.na_file.na_file.NAFile)

    # Test comparison of written and original files for equivalence
    res = nappy.utils.compare_na.compNAFiles(infile, outfile, approx_equal=True)
    assert res is True
       
    # Test comparison of original and CSV version written
    res = nappy.utils.compare_na.compNAFiles(infile, out_csv, delimiter_2=",")
    assert res is True

    # An extra test for FFI 1001
    # Tests an input file with curly braces
    cb_file = os.path.join(data_files, "1001_cb.na")
    fin = nappy.openNAFile(cb_file)
    fin.readData()

    na_dict = fin.getNADict()
    foutname = os.path.join(test_outputs, "test_1001_cb_rewritten.na")

    fobj = nappy.openNAFile(foutname, mode="w", na_dict=na_dict)
    fobj.write()
    assert isinstance(fobj, nappy.na_file.na_file.NAFile)

