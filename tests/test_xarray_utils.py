import os
import numpy as np
import xarray as xr

from .common import MINI_BADC_DIR
from nappy.nc_interface.xarray_to_na import XarrayDatasetToNA

from nappy.nc_interface.xarray_utils import (getBestName, getMissingValue, isUniformlySpaced,
                                             areAxesIdentical, isAxisRegularlySpacedSubsetOf)

temp_nc = MINI_BADC_DIR / "cru/data/cru_ts/cru_ts_4.04/data/tmp/cru_ts4.04.1901.2019.tmp.dat.nc"
wet_nc = MINI_BADC_DIR / "cru/data/cru_ts/cru_ts_4.04/data/wet/cru_ts4.04.1901.2019.wet.dat.nc"


def test_getBestName(load_ceda_test_data):
    ds = xr.open_dataset(temp_nc)
    name = getBestName(ds['tmp'])

    assert name == "near-surface temperature (degrees Celsius)"


def test_getMissingValue(load_ceda_test_data):
    ds = xr.open_dataset(temp_nc)
    miss = getMissingValue(ds['tmp'])

    assert np.isclose(miss, 9.96921e+36)


def test_isUniformlySpaced(load_ceda_test_data):
    ds = xr.open_dataset(temp_nc)
    assert isUniformlySpaced(ds['lon'])


def test_areAxesIdentical(load_ceda_test_data):
    temp = xr.open_dataset(temp_nc)
    wet = xr.open_dataset(wet_nc) 

    for dim in ('time', 'lat', 'lon'):
        assert areAxesIdentical(temp.coords[dim], wet.coords[dim])

    assert areAxesIdentical(temp.lon, temp.lat) == False
    

def test_isAxisRegularlySpacedSubsetOf(load_ceda_test_data):
    temp = xr.open_dataset(temp_nc)

    ax1, ax2 = temp.lon, temp.lon[::2]
    assert isAxisRegularlySpacedSubsetOf(ax2, ax1)

    ax1, ax2 = temp.lat, temp.lat[::2]
    assert isAxisRegularlySpacedSubsetOf(ax2, ax1)

    ax1, ax2 = temp.time, temp.time[::2]
    assert isAxisRegularlySpacedSubsetOf(ax2, ax1)

    ax1, ax2 = temp.lon, temp.lon[:-2]
    assert isAxisRegularlySpacedSubsetOf(ax2, ax1) == False

