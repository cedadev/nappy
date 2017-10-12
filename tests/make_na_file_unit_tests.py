#!/usr/bin/env python

"""
make_na_file_unit_tests.py
==========================

Simple script for making basic unit tests for each of the NAFile classes.

"""

# Import standard library modules
import sys
import glob
import os


def makeNAFileTests():
    "Makes unit tests for the main NAFile classes."
    ffis = ("1001", "1010", "1020", "2010", "2110", "2160",
            "2310", "3010", "4010")

    template = open("test_na_file_template.tmpl").read()

    for ffi in ffis:
        content = template.replace("<FFI>", ffi)
        test_file_name = "test_na_file_%s.py" % ffi
        test_file = open(test_file_name, "w")
        test_file.write(content)
        test_file.close()
        print "Wrote:", test_file_name


if __name__ == "__main__":

    makeNAFileTests()
