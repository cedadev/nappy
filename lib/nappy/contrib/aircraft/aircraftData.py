#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
airCraftData.py
===============

Container module for AircraftData class that deals with
flight data which has unusual time axes and flags in separate 
variables. This class also does sub-sampling by averaging to 
1Hz frequency.


"""

# Imports from python standard library
import os,sys
import MA, Numeric, cdms, MV, cdtime

# Imports from local package


class AircraftData:
    """
    AircraftData class that deals with
    flight data which has unusual time axes and flags in separate
    variables. This class also does sub-sampling by averaging to
    1Hz frequency.
    """

    def __init__(self, var, timeVar, flagVar=None, args=["av"]):
        """
        Parses args and calls required methods.
        """
        if args[0]=="av":
            samplingMethod="averaging"
        elif args[0]=="ss":
            samplingMethod="selection"

        flagsToUse=[0,1]
        samplingRate=1
        if len(args)>1:
            samplingRate=int(args[1])

            if len(args)>2:
                flagsToUse=[int(flag[0]) for flag in args[2:]]

        if samplingMethod=="averaging":
            self.subSampledVar=self._subSampleByAveraging(var, timeVar, flagVar,
                    samplingRate, flagsToUse)
        elif samplingMethod=="selection":
            self.subSampledVar=self._subSampleBySelection(var, timeVar, flagVar,
                    samplingRate, flagsToUse)


    def _subSampleBySelection(self, var, timeVar, flagVar, samplingRate, flagsToUse):
        """
        Returns a new variable which is 'var' sub-sampled by selecting the value
        at the given samplingRate with data selected according to flagVar
        including the flag values  specified in flagsToUse (defaults are 0 and 1).
        """
        if samplingRate!=1:
            raise "Sampling rates of values other than 1Hz are not yet supported."
        maskedArray=self._getMaskedArray(var[:,0](squeeze=1), flagVar[:,0](squeeze=1), flagsToUse)
        # Now re-construct variable axes etc
        newTimeAxis=self._flatten2DTimeAxis(timeVar, samplingRate)
        newVar=self._recreateVariable(var, maskedArray, newTimeAxis, flagVar, max(flagsToUse), missingValue=maskedArray.fill_value(), sampleBy="selection")
        return newVar

        
    def _subSampleByAveraging(self, var, timeVar, flagVar, samplingRate, flagsToUse):
        """
        Returns a new variable which is 'var' sub-sampled by averaging
        at the given samplingRate with data selected according to flagVar
        including the flag values specified in flagsToUse (defaults are 0 and 1).
        """
        maskedArray=self._getMaskedArray(var, flagVar, flagsToUse)
        shape=var.shape
        if shape[1]==1:
            newNumArray=MV.ravel(maskedArray)
            newArrayMask=MV.ravel(maskedArray.mask())
            newArray=MA.masked_array(newNumArray, mask=newArrayMask, fill_value=maskedArray.fill_value())
        else:
            newArray=Numeric.zeros(shape[0], 'f')
            for t0 in range(shape[0]):
                # Set as missing if less than half are valid                 
                t1Array=maskedArray[t0]

                if samplingRate==1:
                    # If half or more are good values then calculate the mean
                    if t1Array.count()>=(shape[1]/2.):
                        newArray[t0]=MA.average(t1Array)
                    # otherwise set as missing value
                    else:
                        newArray[t0]=maskedArray.fill_value()
        
                else:
                    raise "Averaging for non 1Hz sampling rates not yet supported!"

        # Now re-construct variable axes etc
        newTimeAxis=self._flatten2DTimeAxis(timeVar, samplingRate)
        newVar=self._recreateVariable(var, newArray, newTimeAxis, flagVar, max(flagsToUse), missingValue=maskedArray.fill_value(), sampleBy="averaging") 
        return newVar


    def _flatten2DTimeAxis(self, timevar, samplingRate):
        """
        Returns a flattened 2D time axis.
        """
        if samplingRate!=1:
            raise "Cannot yet deal with sub-sampling to non 1Hz sampling rates!"

        timevalues=timevar._data
        timeunit=timevar.units
        newTimeValues=[]
        rate=samplingRate

        for t in timevalues:
            for i in range(rate):
                tvalue=t+((1./rate)*i)
                newTimeValues.append(tvalue)

        newTimeAx=cdms.createAxis(newTimeValues)
        newTimeAx.units=timeunit
        newTimeAx.designateTime()
        newTimeAx.id=newTimeAx.long_name=newTimeAx.standard_name="time"
        return newTimeAx


    def _recreateVariable(self, var, newArray, timeAxis, flagVar, flagMax, missingValue, sampleBy="averaging"):
        """
        Rebuilds a variable using new array and new time axis.
        """
        atts=var.attributes
        newAtts={}
        for att,value in atts.items():
            if type(value) in (type((1,1)), type([1,2]), type(Numeric.array([1.]))) and len(value)==1:
                value=value[0]
            if type(value) in (type(1), type(1.), type(long(1))):
                newAtts[att]=value
            elif type(value)==type(""):
                newAtts[att]=value.strip()

        # Now create the variable
        missing=missingValue
        data=newArray
        newvar=cdms.createVariable(data, id=var.id, fill_value=missing, axes=[timeAxis], attributes=newAtts)
        newvar.frequency=1
        if sampleBy=="averaging":
            newvar.comment="Data averaged to give a pseudo sampling frequency of 1 Hz. "
            if flagVar:
                newvar.comment=newvar.comment+"Values were included where the flag variable was less than %s and where both the flag value and actual data value were present (i.e. not missing values)." % (flagMax+1)
                newvar.comment=newvar.comment+" Average data values were set to missing where more than half the values in any one second period were already missing. Missing value was also used where more than half the flags were either missing value or values of 2 or greater."
            else:
                newvar.comment=newvar.comment+"The flag variable was not used in creating this variable."
                newvar.comment=newvar.comment+" Average data values were set to missing where more than half the values in any one second period were already missing."
        elif sampleBy=="selection":
            newvar.comment="Data sub-sampled to give a pseudo sampling frequency of 1 Hz by selecting only the per-second frequency values. "
            if flagVar:
                newvar.comment=newvar.comment+" Values were included where the flag variable was less than 2 and where both the flag value and actual data value were present (i.e. not missing values)."
            else:
                newvar.comment=newvar.comment+" The flag variable was not used in creating this variable." 
        return newvar
  

    def _getMaskedArray(self, var, flagVar=None, flagValues=(0,1), missingValuesToTest=(-9999., -32767.)):
        """
        Returns a masked array that has the values only present where the flag
        values are acceptable and the data itself is not missing.
        """
        if flagVar:
            flagFillValue=-1
            flagGTValue=max(flagValues)

            flagMaskWhereUnacceptable=MA.masked_greater(flagVar, flagGTValue).mask()
            flagMaskWhereMissing=MA.masked_equal(flagVar, flagFillValue).mask()
            flagMask=flagMaskWhereUnacceptable+flagMaskWhereMissing

        for fv in missingValuesToTest:
            if fv in MV.ravel(var):
                print "Setting missing value for '%s' as: %s" % (var.id, fv)
                varFillValue=fv
        else:
            varFillValue=missingValuesToTest[0]

        if flagVar:
            varMask=MA.masked_array(var, mask=MA.equal(var, varFillValue), fill_value=varFillValue).mask()
            fullmask=MA.bitwise_or(varMask, flagMask)
            maskedArray=MA.masked_array(var, mask=fullmask, fill_value=varFillValue)
        else:
            maskedArray=MA.masked_array(var, mask=MA.equal(var, varFillValue), fill_value=varFillValue)

        #maskedArray=cdms.createVariable(maskedArray, id=var.id, fill_value=varFillValue)
        #maskedArray.missing_value=varFillValue
        return maskedArray 

