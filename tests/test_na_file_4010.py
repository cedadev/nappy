"""
test_na_file_4010.py
====================

Tests for the na_file_4010.py module.

"""

# Import standard library modules
import unittest
import os
import sys

import nappy
import nappy.utils.compare_na

here = os.path.dirname(__file__)
data_files = os.path.join(here, 'testdata')
test_outputs = os.path.join(here, './test_outputs')


class NAFile4010_TestCase(unittest.TestCase):

    def setUp(self):
        self.infile = os.path.join(data_files, "4010.na")
        self.outfile = os.path.join(test_outputs, "test_4010.na")
        self.out_csv = os.path.join(test_outputs, "test_4010.csv")
        self.out_csv_annotated = os.path.join(test_outputs, "test_4010_annotated.csv")
        self.fin = nappy.openNAFile(self.infile)
        self.fin.readData()
        self.na_dict = self.fin.getNADict()        

    def test_read4010(self):
        "Tests reading FFI 4010."
        self.assertEqual(type(self.na_dict), type({1:2}))

    def test_write4010(self):
        "Tests writing FFI 4010."
        fobj = nappy.openNAFile(self.outfile, mode="w", na_dict=self.na_dict)		
        fobj.write()
        self.failUnless(isinstance(fobj, nappy.na_file.na_file.NAFile))

    def test_writeCSV4010(self):
        "Tests conversion to CSV."
        fobj = nappy.openNAFile(self.out_csv, mode="w", na_dict=self.na_dict)
        fobj.write(delimiter=",", float_format="%.6f")
        self.failUnless(isinstance(fobj, nappy.na_file.na_file.NAFile))

    def test_writeAnnotatedCSV4010(self):
        "Tests conversion to Annotated CSV."
        fobj = nappy.openNAFile(self.out_csv_annotated, mode="w", na_dict=self.na_dict)
        fobj.write(delimiter=",", annotation=True)
        self.failUnless(isinstance(fobj, nappy.na_file.na_file.NAFile))
 
    def test_compareFiles4010(self):
        "Tests comparison of written and original files for equivalence."
        res = nappy.utils.compare_na.compNAFiles(self.infile, self.outfile, approx_equal=True)
        self.assertEqual(res, True)
       
    def test_compareNAToCSV4010(self):
        "Tests comparison of original and CSV version written." 
        res = nappy.utils.compare_na.compNAFiles(self.infile, self.out_csv, delimiter_2=",")
        self.assertEqual(res, True)


if __name__ ==  "__main__":

    unittest.main()


