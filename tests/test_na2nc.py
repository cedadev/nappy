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

    c = NAToNC(infile, time_warning=False)
    c.convert() 
    c.writeNCFile(outfile)

    assert os.path.getsize(outfile) > 100


def test_na2nc_1001():
    # na2nc.py -i testdata/1001.na -o test_outputs/1001.nc -n 
    _generic_na_to_nc_test(1001)


def test_na2nc_2010():
    # na2nc.py -i testdata/2010.na -o test_outputs/2010.nc -n
    _generic_na_to_nc_test(2010)


def test_na2nc_3010():
    # na2nc.py -i testdata/3010.na -o test_outputs/3010.nc -n
    _generic_na_to_nc_test(3010)


def test_na2nc_4010():
    # na2nc.py -i testdata/4010.na -o test_outputs/4010.nc -n
    _generic_na_to_nc_test(4010)


def test_na2nc_1001_with_time_units():
    # na2nc.py -i testdata/1001.na -o test_outputs/1001.nc -n -t "seconds since 2000-09-20"
    infile, outfile = _get_paths(1001, label="time-units")

    c = NAToNC(infile, time_units="seconds since 2000-09-20 00:00:00")
    c.convert()
    c.writeNCFile(outfile)

    assert os.path.getsize(outfile) > 100


def test_na2nc_4010_with_time_units():
    # na2nc.py -i testdata/4010.na -o test_outputs/4010.nc -n -t "days since 2008-01-01 00:00:00"
    infile, outfile = _get_paths(4010, label="time-units")

    c = NAToNC(infile, time_units="days since 2008-01-01 00:00:00")
    c.convert()
    c.writeNCFile(outfile)

    assert os.path.getsize(outfile) > 100


def test_na2nc_1001_rename_var():
    # na2nc.py -i testdata/1001.na -o test_outputs/1001-renamed.nc -n -r pressure,measurep
    infile, outfile = _get_paths(1001, label="rename-var")

    c = NAToNC(infile, rename_variables={'pressure': 'measurep'}, time_warning=False)
    c.convert()
    c.writeNCFile(outfile)

    ds = xr.open_dataset(outfile)
    assert "measurep" in ds


def test_na2nc_1001_global_attrs():
    # na2nc.py -i testdata/1001.na -o test_outputs/1001-global-atts.nc -n -g "useful_info","happy days"
    infile, outfile = _get_paths(1001, label="global-attrs")

    c = NAToNC(infile, global_attributes=[("useful_info", "happy_days")], time_warning=False)
    c.convert()
    c.writeNCFile(outfile)

    ds = xr.open_dataset(outfile)
    assert ds.attrs["useful_info"] == "happy_days"


def test_na2nc_1010():
    # na2nc.py -i testdata/1010.na -o test_outputs/1010.nc -n 
    ffi = 1010
    _, outfile = _get_paths(ffi)
    _generic_na_to_nc_test(ffi)

    ds = xr.open_dataset(outfile)
    assert "o_3p_concentration" in ds


def test_na2nc_1001_v0_only():
    # na2nc.py -i testdata/1001.na -o test_outputs/1001-v0-only.nc -n -v 0
    infile, outfile = _get_paths(1001, label="v0-only")

    c = NAToNC(infile, variables=[0], time_warning=False)
    c.convert()
    c.writeNCFile(outfile)

    ds = xr.open_dataset(outfile)
    assert {"ascent_rate"} == {*list(ds.variables.keys())} - {*list(ds.coords.keys())}


def test_na2nc_4010_rename_var():
    # na2nc.py -i testdata/4010.na -o test_outputs/4010-renamed.nc -n -r Temperature,testvar1
    infile, outfile = _get_paths(4010, label="rename-var")

    c = NAToNC(infile, rename_variables={'Temperature': 'testvar1'}, time_warning=False)
    c.convert()
    c.writeNCFile(outfile)

    ds = xr.open_dataset(outfile)
    assert "testvar1" in ds

