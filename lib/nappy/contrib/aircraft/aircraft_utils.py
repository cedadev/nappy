#!/usr/bin/env python
#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
aircraft_utils.py
==================

UNSUPPORTED!

"""

# Imports from python standard library

# Import external packages
import cdms
import Numeric
import MV

cdms.setAutoBounds("off") 


def flatten2DTimeData(var, time_var):
    """
    Returns a flattened 2D array variable with a recalculated time axies.
    """
    data = MV.ravel(var)
    missing = var.getMissing()
    time_values = time_var._data
    time_unit = time_var.units
    sampling_rate = var.getAxis(1)
    rate = int(sampling_rate.id[3:])
    newtime_values = []

    for t in time_values:
        for i in range(rate):
            tvalue = t + ((1./rate)*i)
            newtime_values.append(tvalue)

    new_time_ax = cdms.createAxis(newtime_values)
    new_time_ax.units = time_unit
    new_time_ax.designateTime()
    new_time_ax.id = new_time_ax.long_name = new_time_ax.standard_name = "time"

    atts = var.attributes
    newAtts = {}
    for att,value in atts.items():
        if type(value) in (type((1,1)), type([1,2]), type(Numeric.array([1.]))) and len(value) == 1:
            value = value[0]
        if type(value) in (type(1), type(1.), type(long(1))):
            newAtts[att] = value
        elif type(value) == type("string"):
            newAtts[att] = value.strip()

    # Now create the variable
    newvar = cdms.createVariable(data, id=var.id, fill_value=missing, axes=[new_time_ax], attributes=newAtts)
    return newvar