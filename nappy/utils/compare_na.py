#!/usr/bin/env python

"""
compare_na.py
=============

Tool to compare contents of NASA Ames files or directories full of files.
Allows you to compare headers and data blocks in NASA Ames.

Usage:
======

    compare_na.py [-h | --header-only]  [-b | --body-only]
                  [-n | --number-strict] [-a | --approx-equal] 
                  [-1 <delimiter_1> | --delimiter-1=<delimiter_1>]
                  [-2 <delimiter_2> | --delimiter-2=<delimiter_2>]
                  <item1> <item2>
                                                                   

Where:
======

    <item1> and <item2> 	can either be a text file or directory.
    -h | --header-only    	selects compare only header(s)
    -b | --body-only		selects compare only body(s)
    -n | --number-strict	compares exact formatting of numbers in data block
                                (default is to compare them by value).
    -a | --approx-equal         considers any two numbers being compared the same as long
                                as the difference between them is less than 1%.
    <delimiter_1>		delimiter to use for file 1.
    <delimiter_2>		delimiter to use for file 2. 

"""

# Import standard library modules
import os
import sys
import re
import getopt

# Import local modules
from nappy.utils.compare import *

equality_threshold = 0.01 # i.e. within 1% of each other
file_exclusion_patterns = (r".*CSV.*", r".*svn.*", r"\..*", r".*\.pyc$", r".*~$") 
file_exclusions = [re.compile(pattn) for pattn in file_exclusion_patterns]
letter_match = re.compile(r"[a-zA-Z]")


def exitNicely(msg):
    "Tidy exit."
    print(__doc__)
    print(msg)
    sys.exit()


def compareNA(i1, i2, **kwargs):
    """
    Compares items whether files or directories.
    Reports any differences at the command line but
    also returns them in a dictionary as:
    ???
    **kwargs are forwarded as dictionary to compNAFiles().
    """
    if os.path.isfile(i1):
        apply(compNAFiles, (i1, i2), kwargs)
    elif os.path.isdir(i1):
        compDirs(i1, i2)
    else:
        exitNicely("Cannot recognise/find item '" + i1 + "'.")


def compareSections(l1, l2, number_clever=True, approx_equal=False, 
                   delimiter_1=None, delimiter_2=None):
    """
    Compares sections of NASA Ames files (i.e. headers and bodies).
    """ 
    leng = len(l1)
    if len(l2) < leng:
        leng = len(l2)

    all_same = True

    for i in range(leng):

        # Start by setting same equal to True and then try and disprove this
        same = True

        l1[i] = l1[i].strip()
        l2[i] = l2[i].strip()

        # If letters found in line then not going to be numeric 
        # Hence we can just test if lines are identical
        if letter_match.search(l1[i]):
            if l1[i] == l2[i]:
                continue

        items1 = l1[i].split(delimiter_1)
        items2 = l2[i].split(delimiter_2)
        
        if len(items1) != len(items2):
            # Check that space delimiter hasn't just split identical lines to different lengths
            if len(items1) == 1 and items1[0].split() == items2:
                continue
            elif len(items2) == 1 and items2[0].split() == items1:
                continue
            else:
                same = False
        else: 
            if not number_clever:
                if items1 != items2:
                    same = False
            else:
                for count in range(len(items1)):
                    try:
                        a = float(items1[count])
                        b = float(items2[count])
                    except:
                        a = items1[count]
                        b = items2[count]

                    if a != b:
                        
                        if approx_equal:
                        # Check to see if testing for approximate equality
                            if a == 0:  a = 0.000000001
                            if b == 0:  b = 0.000000001
                            divided = a/b
                            if divided < 1:
                                divided = b/a
                            if (1 - divided) > equality_threshold:
                                same = False
                                break  
                        else: 
                            same = False
                            break 
              
        if not same:
            all_same = False
            print("Line %s:" % (i+1))
            print(">>>", l1[i])
            print("<<<", l2[i])

    return all_same


def compNAFiles(f1, f2, header=True, body=True, number_clever=True, approx_equal=False,
                delimiter_1=None, delimiter_2=None):
    """
    Compares contents of two NASA Ames files f1 and f2.
    header=False or body=False will not compare these sections of the files.
    number_clever=True will compare 5.00000 and 5 making them equal in the body.
    If approx_equal is True then approximate equality is good enough to return two
    numbers as being equal (within equality_threshold set at top of this module).
    If f1_delimiter and f2_delimiter are provided then the comparer will consider
    two lines identical if they have the delimiters sent in as arguments.
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
    
    # Note delimiter set as None will do split on white-space (which we want!)

    with open(f1) as fh1:
        l1 = fh1.readlines()

    with open(f2) as fh2:
        l2 = fh2.readlines()

    head_len1 = int(l1[0].split(delimiter_1)[0])
    head_len2 = int(l2[0].split(delimiter_2)[0])

    header1 = l1[:head_len1]
    header2 = l2[:head_len2]
    body1 = l1[head_len1:]
    body2 = l2[head_len2:]

    same = True
    if header:
        print("Comparing headers:")
        print(">>> %s header:" % f1)
        print("<<< %s header:" % f2)
        same = compareSections(header1, header2, number_clever, approx_equal, delimiter_1, delimiter_2) 
        if same:
            print("HEADERS ARE IDENTICAL.")
        if len(header1) != len(header2):
            print("Header lengths differ:\n>>> %s: %s\n<<< %s: %s" % (f1, len(header1), f2, len(header2)))

    if body:
        print("Comparing bodies:")
        print(">>> %s body:" % f1)
        print("<<< %s body:" % f2)
        same = compareSections(body1, body2, number_clever, approx_equal, delimiter_1, delimiter_2)
        if same:
            print("BODIES ARE IDENTICAL.")
        if len(body1) != len(body2):
            print("Body lengths differ:\n>>> %s: %s\n<<< %s: %s" % (f1, len(body1), f2, len(body2)))
       
    return same


def parseArgs(args):
    """
    Parses arguments returning a dictionary.
    """
    arg_dict = {}
    a = arg_dict
    a["header"] = True
    a["body"] = True
    a["number_clever"] = True
    a["approx_equal"] = False
    a["delimiter_1"] = None
    a["delimiter_2"] = None

    (arg_list, files) = getopt.getopt(args, "hbna1:2:", ["header-only", "body-only",
                    "number-strict", "approx-equal", "delimiter-1=", "delimiter-2="])

    for arg, value in arg_list:
        if arg in ("--header-only", "-h"):
            a["body"] = False
        elif arg in ("--body-only", "-b"):
            a["header"] = False 
        elif arg in ("--number-strict", "-n"):
            a["number_clever"] = False
        elif arg in ("--approx-equal", "-a"):
            a["approx_equal"] = True
        elif arg in ("--delimiter-1", "-1"):
            a["delimiter_1"] = value
        elif arg in ("--delimiter-2", "-2"):
            a["delimiter_2"] = value
        else:
            exitNicely("Unrecognised argument provided: " + arg)

    if len(files) != 2:
        exitNicely("Must provide a minimum of two file names as command line arguments.")

    if not a["header"] and not a["body"]:
        exitNicely("Invalid selection: header-only and body-only cannot be selected together.")

    return (files, a)


def main(args):
    "Main controller."
    files, arg_dict = parseArgs(args)
    apply(compareNA, files, arg_dict) 
   
 
if __name__=="__main__":

    args = sys.argv[1:]
    main(args)
