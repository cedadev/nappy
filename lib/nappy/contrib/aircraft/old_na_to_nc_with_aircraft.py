#!/usr/bin/env python
#   Copyright (C) 2004 CCLRC & NERC( Natural Environment Research Council ).
#   This software may be distributed under the terms of the
#   Q Public License, version 1.0 or later. http://ndg.nerc.ac.uk/public_docs/QPublic_license.txt

"""
cdms_to_na.py
=============

Holds the class CDMSToNA that converts a set of CDMS variables and global attributes.

"""

# Imports from python standard library
import sys
import os
import time
import string
import re

# Import from nappy package
from nappy.na_error import na_error
import nappy.utils
import nappy.utils.common_utils
import nappy.na_file.na_core


nc_to_na_map = utils.getConfigDict()["nc_to_na_map"]

# Import external packages (if available)
if sys.platform.find("win") > -1:
    raise na_error.NAPlatformError("Windows does not support CDMS. CDMS is required to convert to CDMS objects and NetCDF.")
try:
    import cdms, Numeric
except:
    raise Exception("Could not import third-party software. Nappy requires the CDMS and Numeric packages to be installed to convert to CDMS and NetCDF.")

cdms.setAutoBounds("off") 

compareAxes = cdms_utils.axis_utils.compareAxes
compareVariables = cdms_utils.var_utils.compareVariables
arrayToList = nappy.utils.list_manipulator.arrayToList
listOfListsCreator = nappy.utils.list_manipulator.listOfListsCreator
getBestName = cdms_utils.var_utils.getBestName
getMissingValue = cdms_utils.var_utils.getMissingValue
flatten2DTimeAxis = nappy.contrib.aircraft.aircraft_utils.flatten2DTimeAxis
modifyNADictCopy = nappy.utils.common_utils.modifyNADictCopy


def cdms2na(ncfile, na_file_names, naVars={}, variables=None, nFilesOnly="no", 
            rule=None, ffi="automatic", delimiter="    ", float_format="%g", 
            rules=None, sizeLimit=None):
    """
    Main conversion function that calls the appropriate classes and functions
    to write a NASA Ames file.
    """
    #print infilename, outfilenames, nFilesOnly, naVars, variables
    if type(na_file_names) == type("string"): 
        na_file_names = [na_file_names]
    
    # Get which NASA Ames internal variables are allowed to be overwritten in the output files (i.e. by user inputs)
    allowedOverwriteMetadata = ("DATE",  "RDATE", "ANAME", "MNAME",
           "ONAME", "ORG", "SNAME", "VNAME")
    arrayArgs=["DATE", "RDATE", "ANAME", "VNAME"]
    # ANAME[a] - array of 'a' x ANAME strings - aux var names
    # DATE (array of three) - UT date at which the data within the file starts 
    # MNAME - mission name 
    # ONAME - name of originator(s) 
    # ORG - org or affiliation of originator(s) 
    # RDATE (array of three) - date of data reduction or revision 
    # SNAME - source of measurement or model output VNAME[n] - array of 'n' x 
    # VNAME strings - var names.
    outputMessage=[]
    msg="Reading data from: %s\n" % infilename
    print msg
    outputMessage.append(msg)
    cdmsfile=cdms.open(infilename)
    globals=cdmsfile.attributes
    
    vars=[]
    if not variables:
        variables=cdmsfile.listvariables()
        #for var in cdmsfile.listvariables():
            #vars.append(cdmsfile(var))    
	    
    for variable in variables:
        varObj=cdmsfile(variable)
	# Deal with singleton variables
	if not hasattr(varObj, "rank"):
	        varMetadata=cdmsfile[variable].attributes
		varValue=varObj
		#print varMetadata, varValue, varMetadata.keys(), varMetadata._obj_.id
		varObj=cdms.createVariable(Numeric.array(varObj), id=getBestName(varMetadata).replace(" ", "_"), attributes=varMetadata)
		#print varObj, dir(varObj); sys.exit()
		varObj.value=varObj._data[0]
		#varObj.rank=0
		
	#print varObj, varObj.attributes	   		 
        vars.append(varObj)
	
    # Re-order variables if they have the attribute 'nasa_ames_var_number'
    orderedVars=[None]*1000
    otherVars=[]
    for var in vars:
        varMetadata=cdmsfile[var]
	if hasattr(varMetadata, "nasa_ames_var_number"):
	    num=varMetadata.nasa_ames_var_number
	    orderedVars[num]=var
	else:
	    otherVars.append(var)
    
    vars=[]
    for var in orderedVars:
        if var!=None:
	    vars.append(var)
	    
    vars=vars+otherVars
    
    builder=NAContentCollector(vars, globals, rule=rule, cdmsfile=cdmsfile)
    #print builder.na_dict["X"]
    builtNADicts=[[builder.na_dict, builder.varIDs]]
    if builder.varIDs==None:
        msg="\nNo files created after variables parsed."
        print msg
        outputMessage.append(msg)
        return outputMessage

    while len(builder.varBin)>0:
	builder=NAContentCollector(builder.varBin, globals, rule=rule, cdmsfile=cdmsfile)
	outputMessage=outputMessage+builder.outputMessage
        if builder.varIDs!=None:  builtNADicts.append([builder.na_dict, builder.varIDs])

    # Return only filenames if only want to know them now.
    ncount=1
    fileNames=[]
    if nFilesOnly=="yes": 
        for i in builtNADicts:
            if len(builtNADicts)==1:
	        suffix=""
	    else:
	        suffix="_%s" % ncount
	    nameparts=outfilenames[0].split(".")    
	    newname=(".".join(nameparts[:-1]))+suffix+"."+nameparts[-1]
	    fileNames.append(newname)
        ncount=ncount+1
	    
        return fileNames
	 	
    msg="\n%s files to write" % len(builtNADicts)
    print msg
    outputMessage.append(msg)

    count=1
    ncount=1
    for i in builtNADicts:
        if len(outfilenames)==1:
	    if len(builtNADicts)==1:
	        suffix=""
	    else:
	        suffix="_%s" % ncount
	    nameparts=outfilenames[0].split(".")    
	    newname=(".".join(nameparts[:-1]))+suffix+"."+nameparts[-1]
	else:
	    newname=outfilenames[count-1]
 
	msg="\nWriting output NASA Ames file: %s" % newname
	print msg
	outputMessage.append(msg)
	
	builtNADict=i[0]
	for key in naVars.keys():
	    if key in allowedOverwriteMetadata:
	    
	        if key in arrayArgs:
		    newItem=naVars[key].split()		   
		else:
	            newItem=naVars[key]
		    		    
		if newItem!=builtNADict[key]:
		    builtNADict[key]=newItem
		    msg="Metadata overwritten in output file: '%s' is now '%s'" % (key, builtNADict[key])
		    print msg
		    outputMessage.append(msg)
        
        fileList=[]
        # Cope with size limits if specified and FFI is 1001
        if sizeLimit and (builtNADict["FFI"]==1001 and len(builtNADict["V"][0])>sizeLimit):
            varList=builtNADict["V"]
            arrayLength=len(varList[0])
            nvolInfo=divmod(arrayLength, sizeLimit)
            nvol=nvolInfo[0]
            if nvolInfo[1]>0: nvol=nvol+1
            start=0
            letterCount=0
            ivol=0
            while start<arrayLength:
                ivol=ivol+1
                end=start+sizeLimit
                if end>arrayLength:
                    end=arrayLength
                currentBlock=[]
                # Write new V array
                for v in varList:
                    currentBlock.append(v[start:end])

                # Adjust X accordingly
                NADictCopy=modifyNADictCopy(builtNADict, currentBlock, start, end, ivol, nvol)
                
                # Write data to output file
                newnamePlusLetter="%s-%.3d.na" % (newname[:-3], ivol)
                fileList.append(newnamePlusLetter)
                general.openNAFile(newnamePlusLetter, 'w', NADictCopy, delimiter=delimiter, float_format=float_format)
                msg="\nOutput files split on size limit: %s\nFilename used: %s" % (sizeLimit, newnamePlusLetter)
                print msg
                outputMessage.append(msg)
                letterCount=letterCount+1
                start=end


        else:		
   	    general.openNAFile(newname, 'w', builtNADict, delimiter=delimiter, float_format=float_format)

	msg="\nWrote the following variables:"+"\n\t"+("\n\t".join(i[1][0]))
	print msg
	outputMessage.append(msg)
	
	if len(i[1][1])>0:
	    msg="\nWrote the following auxiliary variables:"
	    msg=msg+"\n\t"+("\n\t".join(i[1][1]))	
	    
	if len(i[1][2])>0:
	    msg="\nWrote the following Singleton variables:"
	    msg=msg+"\n\t"+("\n\t".join(i[1][2]))

        if len(fileList)>0:
            msg=msg+("\n\nNASA Ames files written successfully: \n%s" % "\n".join(fileList))
            count=count+len(fileList)
        else:
	    msg=msg+"\n\nNASA Ames file written successfully: %s" % newname
            count=count+1
        ncount=ncount+1

	print msg
	outputMessage.append(msg)
	    
    if (count-1)==1:
        plural=""
    else:
        plural="s"	      
    msg="\n%s file%s written." % ((count-1), plural)
    print msg
    outputMessage.append(msg)
    return outputMessage


class NAContentCollector(NACore):
    """
    Class to build a NASA Ames File object from a set of 
    CDMS variables and global attributes (optional).
    """
    
    def __init__(self, vars, global_attributes={}, cdmsfile=None, rule=None):
        """
        Sets up instance variables and calls appropriate methods to
        generate sections of NASA Ames file object.
        """
        self.rule=rule
        self.cdmsfile=cdmsfile
	self.outputMessage=[]
        self.na_dict={}
        self.vars=vars
        self.varIDs=None
        self.globals=global_attributes	
	self.rankZeroVars=[]
	self.rankZeroVarIDs=[]
        (self.orderedVars, auxVars)=self.analyseVariables()
	if self.orderedVars==None:
	    self.varBin=[]
	else:
	    #print "NAMELISTS:", [var.id for var in self.orderedVars],[var.id for var in auxVars]
	    self.varIDs=[[var.id for var in self.orderedVars],[var.id for var in auxVars], self.rankZeroVarIDs]
	
            self.na_dict["NLHEAD"]="-999"
	
	    #print [var.id for var in self.orderedVars]
	    #print [var.rank() for var in self.orderedVars]	
            self.defineNAVars(self.orderedVars)
            self.defineNAAuxVars(auxVars)
            self.defineNAGlobals()
            self.defineNAComments()
            self.defineGeneralHeader()
            # Quick fudge
            if self.na_dict["FFI"]==1001: self.na_dict["X"]=self.na_dict["X"][0]


    def analyseVariables(self):
        """
	Method to examine the content of CDMS variables to return
	a tuple of two lists containing variables and auxiliary variables
	for the NASA Ames file object.
	Variables not compatible with the first file are binned to be used next.
	"""
	# Need to group the variables together in bins
	self.varBin=[]
	# Get largest ranked variable as the one we use as standard
	highrank=-1
        bestVar=None
	count=0
	for var in self.vars:
	    msg="Analysing: %s" % var.id
	    print msg
	    self.outputMessage.append(msg)
	    count=count+1

	    # get rank
	    rank=var.rank()

            # Deal with specific datasets with special rules
            if self.rule!=None and self.rule[0]=="aircraft":
                var=self._useLocalRule(var, self.rule)
                if type(var)==type(None): 
                    continue 
                rank=1

            # Deal with singleton variables
	    if rank==0: 
	        self.rankZeroVars.append(var)
		self.rankZeroVarIDs.append(var.id)
		continue
	    
	    if rank>highrank:
                highrank=rank
		bestVar=var
		bestVarIndex=count
            elif rank==highrank:
	        if len(var.flat)>len(bestVar.flat):
		    bestVar=var
		    bestVarIndex=count
	
	if len(self.rankZeroVars)==len(self.vars):  return (None, None)
	if not bestVar:  
            print "No variables produced"
            return (None, None)

        vars4NA=[bestVar]
        auxVars4NA=[]
        shape=bestVar.shape
        ndims=len(shape)
        self.na_dict["NIV"]=ndims

        # Work out which File Format Index is appropriate 
        if ndims in (2,3,4):
            self.na_dict["FFI"]=10+(ndims*1000)
        elif ndims>4:
            raise "Cannot write variables defined against greater than 4 axes in NASA Ames format."
        else:
            if len(auxVars4NA)>0 or (self.na_dict.has_key("NAUXV") and self.na_dict["NAUXV"]>0):
                self.na_dict["FFI"]=1010
            else:
                self.na_dict["FFI"]=1001
        #print self.na_dict["FFI"]
        axes=bestVar.getAxisList()
        
        # Get other variable info
	#print [v.id for v in self.vars], bestVarIndex
	#print [v.id for v in self.vars[:bestVarIndex-1]+self.vars[bestVarIndex:]]
        for var in self.vars[:bestVarIndex-1]+self.vars[bestVarIndex:]:
            # Deal with specific datasets with special rules
            if self.rule!=None and self.rule[0]=="aircraft":
                if var.rank()==2:
                    var=self._useLocalRule(var, self.rule)
                    if type(var)==type(None): continue

	    #print self.rankZeroVars
	    #for rzv in self.rankZeroVars:  
	    #    if var.id==rzv.id and var[0]==rzv[0]: continue
	    #print [v.id for v in self.rankZeroVars]
	    if var.id in self.rankZeroVarIDs: continue
	    #print var.id, ndims, shape, len(var.shape), var.shape
            if len(var.shape)!=ndims or var.shape!=shape: 
                # Could it be an auxiliary variable 
                if len(var.shape)!=1: 
		    self.varBin.append(var)
		    continue
                caxis=var.getAxis(0)
                if compareAxes(axes[0], caxis)==0: 
		    self.varBin.append(var)
		    continue
                # I think it is an auxiliary variable
                auxVars4NA.append(var) 
		# Also put it in var bin because auxiliary vars might be useful
		self.varBin.append(var)
            else:
                caxes=var.getAxisList()
		#print var.id, "here"
                for i in range(ndims):            
                    if compareAxes(axes[i], caxes[i])==0:
		        self.varBin.append(var)
                        continue
                # OK, I think they are compatible
                vars4NA.append(var)
		
        # Re-order if they previously came from NASA Ames files (i.e. including 
	# the attribute 'nasa_ames_var_number')
	orderedVars=[None]*1000
	otherVars=[]
	for var in vars4NA:
	    if hasattr(var, "nasa_ames_var_number"):
	        orderedVars[var.nasa_ames_var_number[0]]=var
            else:
	        otherVars.append(var)
	# Remake vars4NA now in order
	vars4NA=[]
	for var in orderedVars:
	    if var!=None: vars4NA.append(var)
        vars4NA=vars4NA+otherVars

        # Now re-order the Auxiliary variables if they previously came from NASA 
	# Ames files (i.e. including the attribute 'nasa_ames_aux_var_number')

	orderedAuxVars=[None]*1000
	otherAuxVars=[]
	for var in auxVars4NA:
	    if hasattr(var, "nasa_ames_aux_var_number"):
	        orderedAuxVars[var.nasa_ames_aux_var_number[0]]=var
            else:
	        otherAuxVars.append(var)
	# Remake auxVars4NA now in order
	auxVars4NA=[]
	for var in orderedAuxVars:
	    if var!=None: auxVars4NA.append(var)
        auxVars4NA=auxVars4NA+otherAuxVars	
        return (vars4NA, auxVars4NA)


    def defineNAVars(self, vars):
        """
	Method to define NASA Ames file object variables and their
	associated metadata.
	"""
        self.na_dict["NV"]=len(vars)
        self.na_dict["VNAME"]=[]
        self.na_dict["VMISS"]=[]
        self.na_dict["VSCAL"]=[]
        self.na_dict["V"]=[]
        for var in vars:
            name=getBestName(var)
            self.na_dict["VNAME"].append(name)
            miss=getMissingValue(var)
            if type(miss) not in (float, int, long):  miss=miss[0]
            self.na_dict["VMISS"].append(miss)
            #print self.na_dict["VMISS"]
            self.na_dict["VSCAL"].append(1)
            # AND THE ARRAY
            # Populate the variable list  
            ######## NOTE - might not have to do this #####
            ######## It  might handle writing from a Numeric array ########
            self.na_dict["V"].append(var._data)
            #listOfListsCreator(inlist, var.shape)
            #arrayToList(var, inlist)

            if not self.na_dict.has_key("X"):
                self.na_dict["NXDEF"]=[]
                self.na_dict["NX"]=[]
                # Create independent variable information
		#print var.id, var.getAxis(0)
                self.ax0=var.getAxis(0)
                self.na_dict["X"]=[list(self.ax0._data_)]
                self.na_dict["XNAME"]=[getBestName(self.ax0)]
                if len(self.ax0)==1:
                    self.na_dict["DX"]=[0]
                else:
                    incr=self.ax0[1]-self.ax0[0]
		    # Set default increment as gap between first two
		    self.na_dict["DX"]=[incr]
		    # Now overwrite it as zero if non-uniform interval in axis
                    for i in range(1, len(self.ax0)):
                        if (self.ax0[i]-self.ax0[i-1])!=incr:
                            self.na_dict["DX"]=[0]
                            break

                # Now sort the rest of the axes
                for axis in var.getAxisList()[1:]:
                    self.getAxisDefinition(axis)


    def defineNAAuxVars(self, auxVars):
        """
	Method to define NASA Ames file object auxiliary variables and their
	associated metadata.
	"""
        self.na_dict["NAUXV"]=len(auxVars)
        self.na_dict["ANAME"]=[]
        self.na_dict["AMISS"]=[]
        self.na_dict["ASCAL"]=[]
        self.na_dict["A"]=[]
        for var in auxVars:
            name=getBestName(var)
            self.na_dict["ANAME"].append(name)
            miss=getMissingValue(var)
            if type(miss)!=float:  miss=miss[0]
            self.na_dict["AMISS"].append(miss)
            self.na_dict["ASCAL"].append(1)
            # AND THE ARRAY
            # Populate the variable list  
            ######## NOTE - might not have to do this #####
            ######## It  might handle writing from a Numeric array ########
            self.na_dict["A"].append(var._data)
            #listOfListsCreator(inlist, var.shape)
            #arrayToList(var, inlist)     


    def getAxisDefinition(self, axis):
        """
	Method to create the appropriate NASA Ames file object 
	items associated with an axis (independent variable in 
	NASA Ames).
	"""
	length=len(axis)
        self.na_dict["NX"].append(length)
        self.na_dict["XNAME"].append(getBestName(axis))
        # If only one item in axis values
        if length<2:
            self.na_dict["DX"].append(0)
            self.na_dict["NXDEF"].append(length)
            self.na_dict["X"].append(list(axis._data_))        
            return
   
        incr=axis[1]-axis[0]
        for i in range(1, length):
            if (axis[i]-axis[i-1])!=incr:
                self.na_dict["DX"].append(0)
                self.na_dict["NXDEF"].append(length)
                self.na_dict["X"].append(list(axis._data_))
                break
        else:
	    maxLength=length
	    if length>3: maxLength=3
            self.na_dict["DX"].append(incr)
            self.na_dict["NXDEF"].append(maxLength)
            self.na_dict["X"].append(axis[:maxLength])
        return


    def defineNAGlobals(self):
        """
	Maps CDMS (NetCDF) global attributes into NASA Ames Header fields.
	"""
	# Get the global mapping dictionary
        globalmap=cdmsMap.toNA
	# Check if we should add to it with locally set rules
	locGlobs=localRules.localGlobalAttributes
        for att in locGlobs.keys():
	    if not globalmap.has_key(att):
	        globalmap[key]=locGlobs[key]

        self.extra_comments=[[],[],[]]  # Normal comments, special comments, other comments
	conventionOrReferenceComments=[]
        for key in self.globals.keys():
            if key!="first_valid_date_of_data" and type(self.globals[key]) not in (str, float, int): continue
            if key in globalmap.keys():
                if key=="history":
                    timestring=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    history="History:\t%s - Converted to NASA Ames format using nappy-%s.\n\t%s" % (timestring, version.version, self.globals[key])
                    history=history.split("\n") 
                    self.history=[]
                    for h in history:
                        if h[:8]!="History:" and h[:1]!="\t": h="\t"+h
                        self.history.append(h) 
                    
                elif key=="institution":
		    # If fields came from NA then extract appropriate fields.
		    match=re.match(r"(.*)\s+\(ONAME from NASA Ames file\);\s+(.*)\s+\(ORG from NASA Ames file\)\.", self.globals[key])
		    if match:
		        self.na_dict["ONAME"]=match.groups()[0]
			self.na_dict["ORG"]=match.groups()[1]
		    else:
                        self.na_dict["ONAME"]=self.globals[key]
                        self.na_dict["ORG"]=self.globals[key]		    
		    
		    # NOte: should probably do the following search and replace on all string lines
		    self.na_dict["ONAME"]=self.na_dict["ONAME"].replace("\n", "  ")
		    self.na_dict["ORG"]=self.na_dict["ORG"].replace("\n", "  ")
		    		    
                elif key=="comment":
		    # Need to work out if they are actually comments from NASA Ames in the first place
                    #self.ncom=[self.globals[key]]
		    comLines=self.globals[key].split("\n")
		    normComms=[]
		    normCommFlag=None
		    specComms=[]
		    specCommFlag=None
		    for line in comLines:
		        if line.find("###NASA Ames Special Comments follow###")>-1:
			    specCommFlag=1
			elif line.find("###NASA Ames Special Comments end###")>-1:
			    specCommFlag=None
		        elif line.find("###NASA Ames Normal Comments follow###")>-1:
			    normCommFlag=1
			elif line.find("###NASA Ames Normal Comments end###")>-1:
			    normCommFlag=None	
			elif specCommFlag==1:
			    specComms.append(line)
			elif normCommFlag==1:
			    normComms.append(line)
			elif line.find("###Data Section begins on the next line###")>-1:
			    pass
			else:
			    normComms.append(line)	    
		    
		    self.extra_comments=[specComms, normComms, []]		    
		   		    
		elif key=="first_valid_date_of_data":
		    self.na_dict["DATE"]=self.globals[key]
		
                elif key in ("Conventions", "references"):
                    #conventionOrReferenceComments.append("%s:   %s" % (key, self.globals[key]))
		    self.extra_comments[2].append("%s:   %s" % (key, self.globals[key]))
                else:
                    self.na_dict[globalmap[key]]=self.globals[key]
            else:
                self.extra_comments[2].append("%s:   %s" % (key, self.globals[key]))
	#self.extra_comments
        return


    def defineNAComments(self, normal_comments=[], special_comments=[]):
        """
	Defines the Special and Normal comments sections in the NASA Ames file 
	object - including information gathered from the defineNAGlobals method.
	"""
	
        if hasattr(self, "ncom"):  normal_comments=self.ncom+normal_comments
	NCOM=[]
        for ncom in normal_comments:
            NCOM.append(ncom)
        if len(NCOM)>0:   NCOM.append("")
	
	if len(self.extra_comments[2])>0:
	    for excom in self.extra_comments[2]:
	        NCOM.append(excom)
	
        if len(self.extra_comments[1])>0:  
	    NCOM.append("Additional Global Attributes defined in the source file and not translated elsewhere:")
            for excom in self.extra_comments[1]:
                NCOM.append(excom)

        if hasattr(self, "history"):
            for h in self.history:
                NCOM.append(h)
        
	if len(NCOM)>0:
	    NCOM.insert(0, "###NASA Ames Normal Comments follow###")
	    NCOM.append("")
	    NCOM.append("###NASA Ames Normal Comments end###")
        NCOM.append("###Data Section begins on the next line###")

        specCommentsFlag=None
	SCOM=[]
	special_comments=self.extra_comments[0]
	if len(special_comments)>0: 
	    SCOM=["###NASA Ames Special Comments follow###"]
	    specCommentsFlag=1
        for scom in special_comments:
            SCOM.append(scom)


        #used_var_atts=("name", "long_name", "standard_name", "id", 
	    #    "missing_value", "fill_value", "units", 
		#"nasa_ames_var_number", "nasa_ames_aux_var_number")
        used_var_atts=("id",  "missing_value", "fill_value", "units", 
                   "nasa_ames_var_number", "nasa_ames_aux_var_number")
        varCommentsFlag=None

        # Create a string for the Special comments to hold rank-zero vars
	rankZeroVarsString=[]
	for var in self.rankZeroVars:
	    rankZeroVarsString.append("\tVariable %s: %s" % (var.id, getBestName(var)))
	    for att in var.attributes.keys():
	        value=var.attributes[att]
		if type(value) in (str, float, int):
		    rankZeroVarsString.append("\t\t%s = %s" % (att, var.attributes[att]))
	    #print "VALUES", dir(var), var._data ; rankZeroVarsString.append("\t\tvalue = %s" % var._data)
	
	if len(rankZeroVarsString)>0:
	    rankZeroVarsString.insert(0, "###Singleton Variables defined in the source file follow###")
	    rankZeroVarsString.append("###Singleton Variables defined in the source file end###")

        for var in self.orderedVars:
            varflag="unused"
            name=getBestName(var)
            for scom,value in var.attributes.items():
                if type(value) in (type([]), type(Numeric.array([0]))) and len(value)==1:
                    value=value[0]
                if type(value) in (str, float, int) and scom not in used_var_atts:
                    if varflag=="unused":
                        if varCommentsFlag==None:
                            varCommentsFlag=1
			    if specCommentsFlag==None:
			        SCOM=["###NASA Ames Special Comments follow###"]+rankZeroVarsString
                            SCOM.append("Additional Variable Attributes defined in the source file and not translated elsewhere:")
                            SCOM.append("###Variable attributes from source (NetCDF) file follow###")
                        varflag="using" 
                        SCOM.append("\tVariable %s: %s" % (var.id, name))
                    SCOM.append("\t\t%s = %s" % (scom, value))

        if varCommentsFlag==1:  SCOM.append("###Variable attributes from source (NetCDF) file end###")
        if specCommentsFlag==1:
	    SCOM.append("###NASA Ames Special Comments end###")

        """used_var_atts=("name", "long_name", "standard_name", "id", "missing_value", "fill_value", "units")
        for var in self.vars:
            for scom,value in var.attributes.items():
                name=getBestName(var)
                if type(value) in (str, float, int) and scom not in used_var_atts:
                    SCOM.append("\t%s: %s - %s" % (name, scom, value))"""

        # Strip out empty lines (or returns)
	NCOM_cleaned=[]
	SCOM_cleaned=[]
	#hiddenNewLineCount1=0
	for c in NCOM:
	    if c.strip() not in ("", " ", "  "):
	        #hiddenNewLineCount1=hiddenNewLineCount1+c.count("\n")
		# Replace new lines within one attribute with a newline and tab so easier to read
		lines=c.split("\n")
		for line in lines:
		    if line!=lines[0]: line="\t"+line
		    NCOM_cleaned.append(line)
		
	#hiddenNewLineCount2=0	
	for c in SCOM:
	    if c.strip() not in ("", " ", "  "): 	        
	        #hiddenNewLineCount2=hiddenNewLineCount2+c.count("\n")
		# Replace new lines within one attribute with a newline and tab so easier to read
	        #c=c.replace("\n", "\n\t")
		#SCOM_cleaned.append(c)
		lines=c.split("\n")
		for line in lines:
		    if line!=lines[0]: line="\t"+line
		    SCOM_cleaned.append(line)
		    
        self.na_dict["NCOM"]=NCOM_cleaned
        self.na_dict["NNCOML"]=len(self.na_dict["NCOM"])#+hiddenNewLineCount1
        self.na_dict["SCOM"]=SCOM_cleaned
        self.na_dict["NSCOML"]=len(self.na_dict["SCOM"])#+hiddenNewLineCount2
        return


    def defineGeneralHeader(self, header_items={}):
        """
	Defines known header items and overwrites any with header_items 
	key/value pairs.
	"""
	# Check if DATE field previously known in NASA Ames file
	time_now=time.strftime("%Y %m %d", time.localtime(time.time())).split()
	if not self.na_dict.has_key("RDATE"):
	    self.na_dict["RDATE"]=time_now
	
        if self.ax0.isTime():
            # Get first date in list
	    try:
                (unit, start_date)=re.match("(\w+)\s+?since\s+?(\d+-\d+-\d+)", self.ax0.units).groups()            
                comptime=cdtime.s2c(start_date)
                first_day=comptime.add(self.na_dict["X"][0][0], getattr(cdtime, unit.capitalize()))
                self.na_dict["DATE"]=string.replace(str(first_day).split(" ")[0], "-", " ").split()
	    except:
	        msg="Nappy Warning: Could not get the first date in the file. You will need to manually edit the output file."
		print msg
		self.outputMessage.append(msg)
		self.na_dict["DATE"]=("DATE", "NOT", "KNOWN")
        else: 
            if not self.na_dict.has_key("DATE"):
	        msg="Nappy Warning: Could not get the first date in the file. You will need to manually edit the output file."
		print msg
		self.outputMessage.append(msg)
	        self.na_dict["DATE"]=("DATE", "NOT", "KNOWN")
        self.na_dict["IVOL"]=1
        self.na_dict["NVOL"]=1
        for key in header_items.keys():
             self.na_dict[key]=header_items[key]
        return


    def _useLocalRule(self, var, ruleArgs):
        """
        Applies some logic based on a local rule.
        """
        ruleName=ruleArgs[0]
        rule=ruleArgs
        if ruleName=="aircraft":
            # Fixes aircraft data 2D time axis, missing values and does sub-selection by default
            flagVar=None

            # return if variable is time
            if var.id=="Time":
                return None

            if len(rule)<2: rule.append("av")
            if len(rule)<3: rule.append("flag")
            if rule[2]=="flag":
                # Only use flag var for processing real variable
                if var.id.strip()[-4:]=="FLAG": 
                    print "Ignore flag: %s" % var.id
                    return None 

                flagID=var.id.strip()+"FLAG"
                try:
                    flagVar=self.cdmsfile(flagID)
                except:
                    raise "Cannot get flag variable for '%s'" % var.id
            elif rule[2]=="noflag":
                flagVar=None

            timeVar=self.cdmsfile("Time")
            import localRules.aircraftData
            ruleArgs=[rule[1]]+rule[3:]
            fixedVar=localRules.aircraftData.AircraftData(var, timeVar, flagVar, ruleArgs).subSampledVar
            return fixedVar
        else:
            raise "Rule '%s' not yet defined." % ruleName
                

usenc2nainstead="""if __name__=="__main__":

    args=sys.argv[1:]
    if len(args)<4:
        print helpMessage
        print "Incorrect number of arguments used."
        sys.exit()
	
    for arg in args:
        if arg=="-i":
	    infile=args[args.index(arg)+1]
	elif arg=="-o":
	    outfile=args[args.index(arg)+1]

    cdms2na(infile, outfile) """
