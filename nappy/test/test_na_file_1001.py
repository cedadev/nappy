"""
test_na_file_1001.py
====================

Tests for the na_file_1001.py module.

"""

# Import standard library modules
import unittest
import os
import sys

import nappy
import nappy.utils.compare_na

# Common test info
here = os.path.dirname(__file__)
example_files = os.path.join(here, '../../example_files')


# Common set up for these tests
infile = os.path.join(example_files, "1001.na")
fin = nappy.openNAFile(infile)
fin.readData()
na_dict = fin.getNADict()    


def test_read1001():
    "Tests reading FFI 1001."
    assert(type(na_dict) == dict)


def test_write1001(tmpdir):
    "Tests writing FFI 1001."
    outfile = os.path.join(tmpdir.strpath, "test_1001.na")
    fobj = nappy.openNAFile(outfile, mode="w", na_dict=na_dict)
    fobj.write()
    assert(isinstance(fobj, nappy.na_file.na_file.NAFile))

    # Test comparison of written and original files for equivalence
    res = nappy.utils.compare_na.compNAFiles(infile, outfile, approx_equal=True)
    assert(res == True)


def test_writeCSV1001(tmpdir):
    "Tests conversion to CSV."
    out_csv = os.path.join(tmpdir.strpath, "test_1001.csv")
    fobj = nappy.openNAFile(out_csv, mode="w", na_dict=na_dict)
    fobj.write(delimiter=",", float_format="%.6f")
    assert(isinstance(fobj, nappy.na_file.na_file.NAFile))

    # Test comparison of original and CSV version written
    res = nappy.utils.compare_na.compNAFiles(infile, out_csv, delimiter_2=",")
    assert(res == True)


def test_writeAnnotatedCSV1001(tmpdir):
    "Tests conversion to Annotated CSV."
    out_csv_annotated = os.path.join(tmpdir.strpath, "test_1001_annotated.csv")
    fobj = nappy.openNAFile(out_csv_annotated, mode="w", na_dict=na_dict)
    fobj.write(delimiter=",", annotation=True)
    assert(isinstance(fobj, nappy.na_file.na_file.NAFile))

 
def test_na1001CurlyWithCurlyBraces(tmpdir):
    "Tests an input file with curly braces."
    cb_file = os.path.join(example_files, "1001_cb.na")
    fin = nappy.openNAFile(cb_file)
    fin.readData()

    na_dict = fin.getNADict()

    foutname = os.path.join(tmpdir.strpath, "test_1001_cb_rewritten.na")
    fobj = nappy.openNAFile(foutname, mode="w", na_dict=na_dict)
    fobj.write()
    assert(isinstance(fobj, nappy.na_file.na_file.NAFile))


if __name__ ==  "__main__":

    unittest.main()


