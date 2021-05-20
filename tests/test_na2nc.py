import os

import xarray as xr

from nappy.nc_interface.na_to_nc import NAToNC
import nappy.utils

from .common import data_files, test_outputs, cached_outputs


def _get_paths(ffi, label=""):
    infile = os.path.join(data_files, f"{ffi}.na")

    if label:
        outfilename = f"{ffi}-{label}.na.nc"
    else:
        outfilename = f"{ffi}.na.nc"

    outfile = os.path.join(test_outputs, outfilename)

    return infile, outfile


def _generic_na_to_nc_test(ffi):
    """
    Command-line equivalent:
      $ na2nc.py -i test_outputs/${ffi}.nc -o test_outputs/${ffi}-from-nc.na

    """
    infile, outfile = _get_paths(ffi)

    c = NAToNC(infile)
    c.convert() 
    c.writeNCFile(outfile)

    assert os.path.getsize(outfile) > 100


def test_na2nc_1001():
    # na2nc.py -i testdata/1001.na -o test_outputs/1001.nc -n -t "days since 2008-01-01 00:00:00"
    _generic_na_to_nc_test(1001)


def test_na2nc_2010():
    # na2nc.py -i testdata/2010.na -o test_outputs/2010.nc -n -t "days since 2008-01-01 00:00:00"
    _generic_na_to_nc_test(2010)


def test_na2nc_3010():
    # na2nc.py -i testdata/3010.na -o test_outputs/3010.nc -n -t "days since 2008-01-01 00:00:00"
    _generic_na_to_nc_test(3010)


def test_na2nc_4010():
    # na2nc.py -i testdata/4010.na -o test_outputs/4010.nc -n -t "days since 2008-01-01 00:00:00"
    _generic_na_to_nc_test(4010)


def test_na2nc_1001_rename_vars():
    # na2nc.py -i testdata/1001.na -o test_outputs/1001-renamed.nc -n -t "days since 2008-01-01 00:00:00" -r pressure,measurep
    assert False

def test_na2nc_1001_global_attrs():
    # na2nc.py -i testdata/1001.na -o test_outputs/1001-global-atts.nc -n -t "days since 2008-01-01 00:00:00" -g "useful_info","happy days"
    assert False


def test_na2nc_1010():
    # na2nc.py -i testdata/1010.na -o test_outputs/1010.nc -n -t "days since 2008-01-01 00:00:00"
    assert False


def test_na2nc_1010_v0_only():
    # na2nc.py -i testdata/1010.na -o test_outputs/1010-v0-only.nc -n -t "days since 2008-01-01 00:00:00" -v 0
    assert False


def test_na2nc_4010_rename_var():
    # na2nc.py -i testdata/4010.na -o test_outputs/4010-renamed.nc -n -t "days since 2008-01-01 00:00:00" -r temperature,testvar1
    assert False

