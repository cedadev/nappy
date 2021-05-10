import os

from .common import data_files, test_outputs

import nappy.nc_interface.na_to_nc
import nappy.nc_interface.nc_to_na
import cdms2 as cdms


def test_convert_nafile_to_nc_file_1010():
    "Converting NAFile to NC file 1010.na"
    ncfile = os.path.join(os.path.dirname(__file__), "../test_outputs/1010.nc")
    nafile = os.path.join(os.path.dirname(__file__), "../data_files/1010.na")
    ncOutFile = os.path.join(os.path.dirname(__file__), "../test_outputs/1010_edited_for_1020.nc")

    n = nappy.nc_interface.na_to_nc.NAToNC(nafile)
    n.writeNCFile(ncfile)

    # Writing a 1020 file from 1010 already converted to NetCDF...
    f = cdms.open(ncfile)
    p_new = f('pressure', altitude=(10,85))
    o_new = f('ozone_concentration', altitude=slice(0,16,4))

    out_file = cdms.open(ncOutFile, "w")
    out_file.write(p_new)
    out_file.write(o_new)

    for att, value in f.attributes.items():
        setattr(out_file, att, value)

    out_file.close()

    out_dir = os.path.join(os.path.dirname(__file__), '../test_outputs')

    ffi_in, ffi_out = (1010, 1020)

    infile = os.path.join(out_dir, "%s_edited_for_%s.nc" % (ffi_in, ffi_out))
    outfile = os.path.join(out_dir, "%s_from_nc_%s.na" % (ffi_out, ffi_in))

    # Reading infile
    x = nappy.nc_interface.nc_to_na.NCToNA(infile, requested_ffi=ffi_out)

    # Writing outfile
    x.writeNAFiles(outfile)

