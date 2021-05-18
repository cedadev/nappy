import os

from .common import data_files, test_outputs, cached_outputs

from nappy.nc_interface.nc_to_na import NCToNA


def _generic_nc_to_na_test(ffi):
    """
    Command-line equivalent:
      $ nc2na.py -i test_outputs/${ffi}.nc -o test_outputs/${ffi}-from-nc.na

    """
    infile = os.path.join(cached_outputs, f"{ffi}.nc")
    outfile = os.path.join(test_outputs, f"{ffi}.nc.na")

    # Reading: infile
    na = NCToNA(infile)

    # Writing: outfile
    na.writeNAFiles(outfile, float_format="%g")

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



"""
    # nc2na.py -i test_outputs/1001.nc -o test_outputs/1001-from-nc-excludes.na -e "Ascent Rate"
    # nc2na.py -i test_outputs/1001.nc -o test_outputs/1001-from-nc-overwrite.na --overwrite-metadata=ONAME,"See line 2 - my favourite org."
    # nc2na.py -i test_outputs/1001.nc -o test_outputs/1001-from-nc-as-padded-ints.na -f "%03d"
    # nc2na.py -i test_outputs/1001.nc -o test_outputs/1001-from-nc-csv.na -d ,
    # nc2na.py -i test_outputs/1001.nc -o test_outputs/1001-from-nc-no-header.na --no-header
nc2na.py -i test_outputs/1001.nc -o test_outputs/1001-from-nc-annotated.na --annotated
nc2na.py -i test_outputs/1001.nc --names-only

"""
