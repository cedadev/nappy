"""
test_na_file_2310.py
====================

Tests for the na_file_2310.py module.

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

class NAFile2310_TestCase(unittest.TestCase):

    def setUp(self):
        self.infile = os.path.join(data_files, "2310.na")
        self.outfile = os.path.join(test_outputs, "test_2310.na")
        self.out_csv = os.path.join(test_outputs, "test_2310.csv")
        self.out_csv_annotated = os.path.join(test_outputs, "test_2310_annotated.csv")
        self.fin = nappy.openNAFile(self.infile)
        self.fin.readData()
        self.na_dict = self.fin.getNADict()        

    def test_read2310(self):
        "Tests reading FFI 2310."
        self.assertEqual(type(self.na_dict), type({1:2}))

    def test_write2310(self):
        "Tests writing FFI 2310."
        fobj = nappy.openNAFile(self.outfile, mode="w", na_dict=self.na_dict)		
        fobj.write()
        self.failUnless(isinstance(fobj, nappy.na_file.na_file.NAFile))

    def test_writeCSV2310(self):
        "Tests conversion to CSV."
        fobj = nappy.openNAFile(self.out_csv, mode="w", na_dict=self.na_dict)
        fobj.write(delimiter=",", float_format="%.6f")
        self.failUnless(isinstance(fobj, nappy.na_file.na_file.NAFile))

    def test_writeAnnotatedCSV2310(self):
        "Tests conversion to Annotated CSV."
        fobj = nappy.openNAFile(self.out_csv_annotated, mode="w", na_dict=self.na_dict)
        fobj.write(delimiter=",", annotation=True)
        self.failUnless(isinstance(fobj, nappy.na_file.na_file.NAFile))
 
    def test_compareFiles2310(self):
        "Tests comparison of written and original files for equivalence."
        res = nappy.utils.compare_na.compNAFiles(self.infile, self.outfile, approx_equal=True)
        self.assertEqual(res, True)
       
    def test_compareNAToCSV2310(self):
        "Tests comparison of original and CSV version written." 
        res = nappy.utils.compare_na.compNAFiles(self.infile, self.out_csv, delimiter_2=",")
        self.assertEqual(res, True)


if __name__ ==  "__main__":

    unittest.main()


