#    Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#    This software may be distributed under the terms of the
#    Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
common_utils.py
===============

Functions and classes commonly used in nappy.

"""

# Standard library imports
import logging

# Imports from local package
import parse_config
import text_parser as text_parser

logging.basicConfig()
log = logging.getLogger(__name__)


def getNAFileClass(ffi):
    """
    Returns class for an FFI.
    """
    mod = "nappy.na_file.na_file_" + `ffi`
    cls = "NAFile" + `ffi`
    exec "import %s" % mod
    return eval("%s.%s" % (mod, cls))
   

def readFFI(filename):
    """
    Function to read the top line of a NASA Ames file to extract
    the File Format Index (FFI) and return it as an integer.
    """
    fin = open(filename)
    topline = fin.readline()
    fin.close()

    ffi = text_parser.readItemsFromLine(topline, 2, int)[-1]
    return ffi


def chooseFFI(na_dict):
    """
    Function to choose the appropriate FFI based on the contents of the
    'na_dict' dictionary object that holds NASA Ames internal variables.
    """
    d = na_dict

    if d["NIV"] > 4:      # More than 4 independent variables not allowed
        raise Exception("NASA Ames cannot write more than 4 independent variables.")

    elif d["NIV"] == 4:     # 4 independent variables
        return 4010

    elif d["NIV"] == 3:     # 3 independent variables
        return 3010

    elif d["NIV"] == 2:    # 2 independent variables
        if type(d["X"][0][0]) == type("string"):
            # 2160 - the  independent unbounded variable is a character string
            return 2160
        elif type(d["X"][0][1]) == type([1,2]) and len(d["X"][0][1]) > 1:
            # 2110 - one independent variable changes length and the values are specified
            return 2110
        elif type(d["X"][0][1]) == type([1,2]) and len(d["X"][0][1]) == 1:
            # 2310 - one indepenent variable changes length but only the first value is specifically stated
            return 2310
        else:            
            # 2010 - Straightforward 2-D variables
            return 2010

    elif d["NIV"] == 1:   # 1 independent variable 
        if not d.has_key("NAUXV"):
            # 1001 - No auxiliary variables
            return 1001
        elif d.has_key("NVPM"):
            # 1020 - Implied values for independent variable
            return 1020
        else:
            # 1010 - Auxiliary variables included
            return 1010
    else:
        raise Exception("Could not resolve the dictionary object to create a suitable NASA Ames File Format Index (FFI). Please modify the contents and try again.")


def getFileNameWithNewExtension(input_file, format):
    """
    Takes an input_file name and applies new extension to it by:
    (i) replacing initial extension if there is one, OR
    (ii) just appending new extension.
    """
    base_name = input_file
    last_four = base_name[-4:]
    found = last_four.find(".")
    if found > -1:
        idx = len(base_name) + found
        base_name = base_name[:idx]
    return base_name + "." + format


def modifyNADictCopy(indict, v_new, start, end, ivol, nvol):
    """
    Returns a copy of a dictionary with some modifications.
    """
    newDict = {}
    for key,value in indict.items(): 
        if key == "X":
            newlist = indict["X"][start:end]
            newDict["X"] = newlist
        elif key == "V":
            newDict["V"] = v_new
        elif key == "IVOL":
            newDict["IVOL"] = ivol
        elif key == "NVOL":
            newDict["NVOL"] = nvol
        else:
            newDict[key] = value
    return newDict


def getVersion():
    """
    Gets config dict for version.
    """
    version = parse_config.getConfigDict()["main"]["version"]
    return version


def getDebug():
    """
    Returns true or false for DEBUG status.
    """
    DEBUG = parse_config.getConfigDict()["main"]["DEBUG"]
    return eval(DEBUG)


def getDefault(item):
    """
    Returns value of item from 'main' config file section.
    """
    value =  parse_config.getConfigDict()["main"][item]
    return value


def makeDictFromCommaSepString(s):
    """
    Reads in comma-separated list and converts to dictionary of successive
    keyword,value pairs.
    """
    if s.count(",") % 2 == 0:
        raise Exception("Must provide even number of items in argument of commas-separated pairs of values: " + s)

    d = {}
    items = s.split(",")
    while len(items) > 0:
        d[items[0]] = items[1]
        items = items[2:] 
    return d


def makeListFromCommaSepString(s):
    """
    Reads in comma-separated list and converts to list of successive
    keyword,value pairs.
    """
    if s.count(",") % 2 == 0:
        raise Exception("Must provide even number of items in argument of commas-separated pairs of values: " + s)

    l = []
    items = s.split(",")
    while len(items) > 0:
        l.append((items[0], items[1]))
        items = items[2:]
    return l


def getAnnotation(item, annotation, delimiter=None, count=None):
    """
    Returns the annotation string for a given NASA Ames item.
    """
    if delimiter == None:
        delimiter = getDefault("default_delimiter") 
    dict = parse_config.getAnnotationsConfigDict()

    if count == None:
        count_string = ""
    else:
        count_string = " %s" % count
    
    if annotation:
        return "%s%s%s" % (dict[item], count_string, delimiter)
    else:
        return ""


def annotateLines(item_name, annotate, delimiter, lines):
    """
    Takes item_name to look up, delimiter and item to render and returns full line.
    """

    split_lines = lines.splitlines(1)
    output = ""

    count = 1
    for line in split_lines:
        output = output + annotateLine(item_name, annotate, delimiter, line, count)
        count += 1

    return output

    
def annotateLine(item_name, annotate, delimiter, line, count=None):
    """
    Takes item_name to look up, delimiter and item to render and returns full line.
    """

    if annotate:
        annotation = getAnnotation(item_name, annotate, delimiter=delimiter, count=count)
        line = "%s%s" % (annotation, line)
        return line
    else:
        return line


def stripQuotes(s):
    "Strips extra quotes"
    if type(s) != type("string"): s  = str(s)
    if s[0] in ("'", '"'): s = s[1:]
    if s[-1] in ("'", '"'): s = s[:-1]
    return s
