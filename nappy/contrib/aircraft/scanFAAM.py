#!/usr/bin/env python

"""
scanFAAM.py
===========

Holds the scanFAAM function that is used to work out the first and last
index of real data (i.e. non-missing data in a load of FAAM flight data).
It is used in conjunction with nappy to reduce the size of output files
by missing out beginning and end periods that hold only misssing values.

Usage
=====

    scanFAAM.py -f <filename> [-m <missing_value>]

Where:
------

    filename   - path to a FAAM NetCDF file
    missing_value - missing value to use for variables.

"""

import os, sys, cdms, getopt

def scanFAAM(fileName=None, vars=None, nth=4, missingValuesToUse=(-9999., -32767.)):
    """
    Scans every 'nth' variable in the list of variables (or found in the
    file and gets the first and last index of the first (time) dimension
    that holds real (non-missing) values.
    """
    if type(missingValuesToUse)!=type((1,2)):
        missingValuesToUse=(missingValuesToUse,)
    startList=[]
    endList=[]
    start=None
    end=None

    if not fileName and not vars:
        raise "You must provide either a file name or a list of cdms variables."
    
    if fileName:
        f=cdms.open(fileName)
        vars=f.listvariables()

    for var in vars:
        if type(var)!=type(""):
            id=var.id
        else:
            id=var

        if id[-4:]=="FLAG" or id=="Time":
            continue

        if type(var)==type(""):
            var=f(var)

        step=1000
        while (start, end)==(None, None):
            (start, end)=findMissing(var, step, missingValuesToUse)
            step=step/2

        startList.append(start)
        endList.append(end)
        print("Start/End index: %s %s:%s" % (id, start, end))
  
    startMin=min(startList)
    endMax=max(endList)
    return (startMin, endMax)

            
def findMissing(var, step, missingValuesToUse):
    """
    Returns the (start, end) tuple for a given variable where
    they are indices of an array where missing values end and begin.
    """
    start=None
    end=None
    i0=0    
    sh=var.shape
    iend=sh[0]-1

    print(var.id, step)
    for miss in missingValuesToUse:
        for i in range(i0, iend, step):
            if var[i][0]==miss:
                start=i
                break
            
        for e in range(iend, i0, -step):
            if var[e][0]==miss:
                end=e
                break
            
    return (start, end)

if __name__=="__main__":

    argList=sys.argv[1:]
    args=getopt.getopt(argList, "f:m:")
    fileName=None
    missingValue=None

    for arg,value in args[0]:
        if arg=="-f":
            fileName=value
        elif arg=="-m":
            missingValue=float(value)

    scanFAAM(fileName=fileName, missingValuesToUse=(missingValue,))
