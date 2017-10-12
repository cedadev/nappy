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

here = os.path.dirname(__file__)
data_files = os.path.join(here, '../data_files')
test_outputs = os.path.join(here, '../test_outputs')

class NAFile1001_TestCase(unittest.TestCase):

    def setUp(self):
        self.infile = os.path.join(data_files, "1001.na")
        self.outfile = os.path.join(test_outputs, "test_1001.na")
        self.out_csv = os.path.join(test_outputs, "test_1001.csv")
        self.out_csv_annotated = os.path.join(test_outputs, "test_1001_annotated.csv")
        self.fin = nappy.openNAFile(self.infile)
        self.fin.readData()
        self.na_dict = self.fin.getNADict()        

    def test_read1001(self):
        "Tests reading FFI 1001."
        self.assertEqual(type(self.na_dict), type({1:2}))

    def test_write1001(self):
        "Tests writing FFI 1001."
        fobj = nappy.openNAFile(self.outfile, mode="w", na_dict=self.na_dict)		
        fobj.write()
        self.failUnless(isinstance(fobj, nappy.na_file.na_file.NAFile))

    def test_writeCSV1001(self):
        "Tests conversion to CSV."
        fobj = nappy.openNAFile(self.out_csv, mode="w", na_dict=self.na_dict)
        fobj.write(delimiter=",", float_format="%.6f")
        self.failUnless(isinstance(fobj, nappy.na_file.na_file.NAFile))

    def test_writeAnnotatedCSV1001(self):
        "Tests conversion to Annotated CSV."
        fobj = nappy.openNAFile(self.out_csv_annotated, mode="w", na_dict=self.na_dict)
        fobj.write(delimiter=",", annotation=True)
        self.failUnless(isinstance(fobj, nappy.na_file.na_file.NAFile))
 
    def test_compareFiles1001(self):
        "Tests comparison of written and original files for equivalence."
        res = nappy.utils.compare_na.compNAFiles(self.infile, self.outfile, approx_equal=True)
        self.assertEqual(res, True)
       
    def test_compareNAToCSV1001(self):
        "Tests comparison of original and CSV version written." 
        res = nappy.utils.compare_na.compNAFiles(self.infile, self.out_csv, delimiter_2=",")
        self.assertEqual(res, True)


    def test_na1001CurlyWithCurlyBraces(self):
        "Tests an input file with curly braces."
        cb_file = os.path.join(data_files, "1001_cb.na")
        fin = nappy.openNAFile(cb_file)
        fin.readData()
        na_dict = fin.getNADict()
        foutname = os.path.join(test_outputs, "test_1001_cb_rewritten.na")
        fobj = nappy.openNAFile(foutname, mode="w", na_dict=na_dict)
        fobj.write()
        self.failUnless(isinstance(fobj, nappy.na_file.na_file.NAFile))

if __name__ ==  "__main__":

    unittest.main()


