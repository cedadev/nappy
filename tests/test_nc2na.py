import os

import xarray as xr
import numpy as np

from nappy.nappy_api import openNAFile
from nappy.nc_interface.nc_to_na import NCToNA
import nappy.utils

from .common import data_files, test_outputs, cached_outputs, MINI_BADC_DIR

wet_nc = os.path.join(MINI_BADC_DIR, "cru/data/cru_ts/cru_ts_4.04/data/wet/cru_ts4.04.1901.2019.wet.dat.nc")
groundfrost_nc = os.path.join(MINI_BADC_DIR, "ukmo-hadobs/data/insitu/MOHC/HadOBS/HadUK-Grid/v1.0.3.0/1km/"
                               "groundfrost/mon/v20210712/groundfrost_hadukgrid_uk_1km_mon_196101-196112.nc")


DELIMITER = nappy.utils.getDefault("default_delimiter") 
EXTENSION = "na"


def _get_paths(ffi, label="", extension=EXTENSION):
    infile = os.path.join(cached_outputs, f"{ffi}.nc")

    if label:
        outfilename = f"{ffi}-{label}.nc.{extension}"
    else:
        outfilename = f"{ffi}.nc.{extension}"

    outfile = os.path.join(test_outputs, outfilename)

    return infile, outfile
    

def _generic_nc_to_na_test(ffi, delimiter=DELIMITER, extension=EXTENSION):
    """
    Command-line equivalent:
      $ nc2na.py -i test_outputs/${ffi}.nc -o test_outputs/${ffi}-from-nc.na

    """
    infile, outfile = _get_paths(ffi, extension=extension)

    na = NCToNA(infile)
    na.writeNAFiles(outfile, float_format="%g", delimiter=delimiter)

    assert os.path.getsize(outfile) > 100


def test_nc_to_na_1001():
    _generic_nc_to_na_test(1001)


def test_nc_to_na_1010():
    _generic_nc_to_na_test(1010)


def test_nc_to_na_2010():
    _generic_nc_to_na_test(2010)


def test_nc_to_na_3010():
    _generic_nc_to_na_test(3010)


def test_nc_to_na_4010():
    _generic_nc_to_na_test(4010)


def test_nc_to_na_1001_exclude():
    # nc2na.py -i test_outputs/1001.nc -o test_outputs/1001-from-nc-excludes.na -e "Ascent Rate"
    infile, outfile = _get_paths(1001, label="exclude")

    na = NCToNA(infile, exclude_vars=["Ascent Rate"])

    assert "ascent_rate" not in [v.name for v in na.xr_variables]

    na.writeNAFiles(outfile, float_format="%g", delimiter=DELIMITER)

    assert os.path.getsize(outfile) > 100

    n = openNAFile(outfile)
    assert not any([vname.lower().startswith('ascent') for vname in n["VNAME"]])


def test_nc_to_na_1001_overwrite_metadata():
    # nc2na.py -i test_outputs/1001.nc -o test_outputs/1001-from-nc-overwrite.na --overwrite-metadata=ONAME,"See line 2 - my favourite org."
    infile, outfile = _get_paths(1001, label="overwrite-metadata")

    override = {"ONAME": "See line 2 - my favourite org."}
    na = NCToNA(infile, na_items_to_override=override)
    na.writeNAFiles(outfile, float_format="%g", delimiter=DELIMITER)

    n = openNAFile(outfile)
    assert n["ONAME"] == "See line 2 - my favourite org."
 

def test_nc_to_na_1001_with_padded_ints():
    # nc2na.py -i test_outputs/1001.nc -o test_outputs/1001-from-nc-as-padded-ints.na -f "%03d"
    infile, outfile = _get_paths(1001, label="padded-ints")

    na = NCToNA(infile)
    na.writeNAFiles(outfile, float_format="%03d", delimiter=DELIMITER)

    assert open(outfile).readlines()[-3].strip() == "79200    000    030    1017"


def test_nc_to_na_1001_no_header():
    # nc2na.py -i test_outputs/1001.nc -o test_outputs/1001-from-nc-no-header.na --no-header
    infile, outfile = _get_paths(1001, label="no-header")

    na = NCToNA(infile)
    na.writeNAFiles(outfile, delimiter=DELIMITER, no_header=True)

    assert open(outfile).readlines()[0].strip() == "79200    0    30    1017.6"


def test_nc_to_na_1001_annotated():
    # nc2na.py -i test_outputs/1001.nc -o test_outputs/1001-from-nc-annotated.na --annotated
    infile, outfile = _get_paths(1001, label="annotated")

    na = NCToNA(infile)
    na.writeNAFiles(outfile, delimiter=DELIMITER, annotation=True)

    assert open(outfile).readlines()[0].startswith("Number of header lines;")


def test_nc_to_na_1001_names_only():
    # nc2na.py -i test_outputs/1001.nc --names-only
    infile, _ = _get_paths(1001)

    na = NCToNA(infile, only_return_file_names=True)
    file_names = na.constructNAFileNames()
    assert os.path.basename(file_names[0]) == "1001.na"


def test_nc_to_na_convert_cru_ts_wet(load_ceda_test_data):
    """
    The "wet" variable has units "days". Unless `xr.open_dataset` uses `decode_timedelta=False` the 
    variable will be decoded into datatype `np.timedelta[ns]` - which we do not want.
    This test checks the nasa ames converted version is correctly converted. 
    """
    infile, outfile = wet_nc, os.path.join(test_outputs, "1001-cru-ts-wet.nc.na")

    na = NCToNA(infile)
    na.writeNAFiles(outfile, float_format="%g", delimiter=",")

    # Now test the max value has been correctly cast to the NA array
    na_dict = na.na_dict_list[0][0]
    arr = np.ma.masked_values(na_dict['V'][0], na_dict['VMISS'][0])
    
    assert np.isclose(np.ma.max(arr), 26.579, atol=0.01)
 

def test_nc_to_na_all_global_attributes_correct(load_ceda_test_data):
    """
    Checks that the resulting NA files has all the right stuff in
    the right places.
    """
    infile = wet_nc
    na_output_file = os.path.join(test_outputs, "cru-ts-wet-from-nc.na")

    converter = NCToNA(infile, na_items_to_override={}) 
    converter.writeNAFiles(na_output_file, float_format="%g")

    # Re-open the file and check the outputs
    na = nappy.openNAFile(na_output_file)
    na.readData()

    # Check global attributes match NASA Ames content
    assert na.ONAME == "Data held at British Atmospheric Data Centre, RAL, UK."
    assert na.MNAME == "CRU TS4.04 Rain Days"
    assert na.SNAME == "Run ID = 2004151855. Data generated from:wet.2004011744.dtb, pre.2004011744.dtb"

    assert "Conventions:   CF-1.4" in na.NCOM
    assert "references:   Information on the data is available at http://badc.nerc.ac.uk/data/cru/" in na.NCOM
    assert "contact:   support@ceda.ac.uk" in na.NCOM
    assert "NCO:   netCDF Operators version 4.9.2 (Homepage = http://nco.sf.net, Code = http://github.com/nco/nco)" in na.NCOM

    assert "Access to these data is available to any registered CEDA user." in na.NCOM
    assert "Tue Nov 24 15:46:02 2020: ncks -d lat,,,100 -d lon,,,100 --variable wet /badc/cru/data/cru_ts/cru_ts_4.04/data/wet/cru_ts4.04.1901.2019.wet.dat.nc ./archive/badc/cru/data/cru_ts/cru_ts_4.04/data/wet/cru_ts4.04.1901.2019.wet.dat.nc" in na.NCOM
    assert "Thu 16 Apr 2020 01:19:04 BST : User ianharris : Program makegridsauto.for called by update.for" in na.NCOM

    # Check variable attributes match NASA Ames content
    assert "Variable wet: wet day frequency (days)" in na.SCOM
    assert "long_name = wet day frequency" in na.SCOM
    assert "correlation_decay_distance = 450.0" in na.SCOM
    assert np.isclose(na.VMISS[0], 9.96921e+36)


def test_convert_data_with_string_variable(load_ceda_test_data):
    """
    Checks that a string variable gets converted properly.
    """
    infile = groundfrost_nc
    na_output_file = os.path.join(test_outputs, "haduk-grid-groundfrost-from-nc.na")

    converter = NCToNA(infile) 
    converter.writeNAFiles(na_output_file, float_format="%g")

    # Re-open the file and check the outputs
    na = nappy.openNAFile(na_output_file[:-3] + "_1.na")
    na.readData()

    assert "value = natural_grasses" in na.SCOM 
    assert "value = 0.0" in na.SCOM
