import os
import pytest

from .common import data_files, test_outputs

import nappy.nc_interface.na_to_nc
import nappy.nc_interface.nc_to_na
import xarray as xr


@pytest.mark.xfail(reason="Not sure if this should work at all.")
def test_convert_nafile_to_nc_file_1010():
    "Converting NAFile to NC file 1010.na"
    ncfile = os.path.join(test_outputs, "1010.nc")
    nafile = os.path.join(data_files, "1010.na")
    ncOutFile = os.path.join(test_outputs, "1010_edited_for_1020.nc")

    n = nappy.nc_interface.na_to_nc.NAToNC(nafile)
    n.writeNCFile(ncfile)

    # Writing a 1020 file from 1010 already converted to NetCDF...
    f = xr.open_dataset(ncfile)
    p_new = f['pressure'].sel(altitude=(10,85))
    o_new = f['ozone_concentration'].sel(altitude=slice(0,16,4))

    ds = xr.Dataset({p_new.name: p_new, o_new.name: o_new}, attrs=f.attrs.copy())
    ds.to_netcdf(ncOutFile)

    ffi_in, ffi_out = (1010, 1020)

    infile = os.path.join(test_outputs, f"{ffi_in}_edited_for_{ffi_out}.nc")
    outfile = os.path.join(test_outputs, f"{ffi_out}_from_nc_{ffi_in}.na")

    # Reading infile
    x = nappy.nc_interface.nc_to_na.NCToNA(infile, requested_ffi=ffi_out)

    # Writing outfile
    x.writeNAFiles(outfile)

