#!/usr/bin/env python

"""
run_cmd_line_tests.py
=====================

Usage:

    run_cmd_line_tests.py <test_file> [<n>] [<n2> .... <nm>]

Where:

    <test_file>  has one cmd line test per line
    n and friends are numbers of tests in <test_file>.

"""


import os
import sys
import subprocess

args = sys.argv[1:]

if len(args) == 0:
    print("Please provide at least the file arg.")
    sys.exit()

fname = args[0]
with open(fname) as fh:
    tests = fh.readlines()
limited_tests = [int(i) for i in args[1:]]


for count, test in enumerate(tests):
    count = count + 1    
    if limited_tests and count not in limited_tests:
        continue

    test = "python " + test
    print("\n\n\n================================================================================")
    print("         Test number: %s  " % count)
    print("===================================================================================")
    print("Running: ", test)
    ret_code = subprocess.check_call(test.split()) 
    print("Return code: %s" % ret_code)
     
