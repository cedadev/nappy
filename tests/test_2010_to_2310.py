import os

from .common import cached_outputs, data_files, test_outputs

import nappy.nc_interface.na_to_nc
import nappy.nc_interface.nc_to_na


def test_convert_nc_2010_to_na_2310():
    ffi_in, ffi_out = (2010, 2310)

    infile = os.path.join(cached_outputs, f"{ffi_in}.nc")
    outfile = os.path.join(test_outputs, f"{ffi_out}_from_nc_{ffi_in}.na")

    # Reading: infile
    x = nappy.nc_interface.nc_to_na.NCToNA(infile, requested_ffi=ffi_out)

    # Writing: outfile
    x.writeNAFiles(outfile, delimiter=",", float_format="%g")


