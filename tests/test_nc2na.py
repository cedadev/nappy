import os

from .common import data_files, test_outputs, cached_outputs

from nappy.nc_interface.nc_to_na import NCToNA


def test_nc_to_na_1001():
    # nc2na.py -i test_outputs/1001.nc -o test_outputs/1001-from-nc.na
    infile = os.path.join(cached_outputs, "1001.nc")
    outfile = os.path.join(test_outputs, "1001.nc.na")

    # Reading: infile
    na = NCToNA(infile)

    # Writing: outfile
    na.writeNAFiles(outfile, delimiter=",", float_format="%g")

    assert os.path.getsize(outfile) > 100

