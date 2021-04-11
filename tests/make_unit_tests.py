#!/usr/bin/env python

"""
make_unit_tests.py
==================

Simple script for making basic unit test stubs for a given directory full of python files.

"""

# Import standard library modules
import sys
import glob
import os

template = """\"\"\"
test_%s
==================

Tests for the %s module.

\"\"\"

# Import standard library modules
import unittest

# Import local modules
import 

class TestCase(unittest.TestCase):

    def setUp(self):
        self. = ()

    def test_(self):
        "Tests ."
        data = self.()
        self.assertEqual()
        self.assert()				


if __name__ ==  "__main__":

    unittest.main()

"""

def makeUnitTestModule(dr, include_init=False):
    """
    Makes a unit test module for each module in a directory. It excludes
    __init__.py unless you set include_init to True.
    """
    cwd = os.getcwd()
    glob_pattn = os.path.join(dr, "*.py")
    mods = glob.glob(glob_pattn)
    
    for mod in mods:
        mod_name = os.path.split(mod)[-1]
        content = template % (mod_name, mod_name)
        ut_name = "test_%s" % mod_name
        with open(ut_name, "w") as fh:
            ut_file = fh.write(content)
        print("Wrote:", ut_name)


if __name__ == "__main__":

    dirs = sys.argv[1:]
    dirs = ["na_file"]
    for dr in dirs:
        makeUnitTestModule(dr)
