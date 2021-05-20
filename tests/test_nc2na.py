import os

import xarray as xr

from nappy.nappy_api import openNAFile
from nappy.nc_interface.nc_to_na import NCToNA
import nappy.utils

from .common import data_files, test_outputs, cached_outputs

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

    na = NCToNA(infile, na_items_to_override={"ONAME": "See line 2 - my favourite org."})
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