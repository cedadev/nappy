#!/usr/bin/env python

"""
compare.py
==========

Tool to compare contents of files or directories full of files.

Usage:
======

    compare.py <item1> <item2>

Where:
======

    <item1> and <item2> can either be a text file or directory.
"""

# Import standard library modules
import os
import sys
import re

file_exclusion_patterns = (r".*CSV.*", r".*svn.*", r"\..*", r".*\.pyc$", r".*~$") 
file_exclusions = [re.compile(pattn) for pattn in file_exclusion_patterns]
dir_exclusion_patterns = (r".*CSV.*", r".*svn.*")
dir_exclusions = [re.compile(pattn) for pattn in dir_exclusion_patterns]


def exitNicely(msg):
    "Tidy exit."
    print(__doc__)
    print(msg)
    sys.exit()


def compare(i1, i2):
    """
    Compares items whether files or directories.
    Reports any differences at the command line but
    also returns them in a dictionary as:
    ???
    """
    if os.path.isfile(i1):
        compFiles(i1, i2)
    elif os.path.isdir(i1):
        compDirs(i1, i2)
    else:
        exitNicely("Cannot recognise/find item '" + i1 + "'.")


def compDirs(d1, d2):
    """
    Compares directories by looping through and then calling
    compFiles() for each pair of files found.
    """
    dname = os.path.split(d1)[-1]
    # Ignore anything that is in exclusion list
    for excl in dir_exclusions:
        if excl.match(dname):
            print("IGNORING EXCLUDED Directory:", d1)
            return

    items = os.listdir(d1)
    
    for item in items:

        d1f = os.path.join(d1, item)
        d2f = os.path.join(d2, item)
	
        if not os.path.exists(d2f):
            print("WARNING: cannot find item:", d2f)
            continue

        if os.path.isdir(d1f):
            compDirs(d1f, d2f)
            continue

        compFiles(d1f, d2f)


def compFiles(f1, f2):
    """
    Compares contents of two files.
    """	
    name = os.path.split(f1)[-1]
    # Ignore anything that is in exclusion list
    for excl in file_exclusions:
        if excl.match(name):
            print("IGNORING EXCLUDED file:", f1)
            return

    # Check they exist
    for f in (f1, f2):
        if not os.path.isfile(f):
            exitNicely("CANNOT compare files as item does not exist:" + f)
            

    with open(f1) as fh1:
        l1 = fh1.readlines()

    with open(f2) as fh2:
        l2 = fh2.readlines()

    leng = len(l1)
    if len(l2) < leng: 
        leng=len(l2)

    print("\n>>>", f1, "\n<<<", f2)

    for i in range(leng):
        if l1[i] != l2[i]:
            print("Line %s:" % (i+1))
            print(">>>", l1[i])
            print("<<<", l2[i])

    
if __name__=="__main__":

    args = sys.argv[1:]
    if len(args) != 2:
       exitNicely("Must provide two items to compare as command-line arguments.")

    compare(args[0], args[1])
