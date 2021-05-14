import numpy as np
import xarray as xr

from .common import MINI_BADC_DIR

from nappy.nc_interface.xarray_utils import getBestName, getMissingValue


def test_getBestName():
    fpath = MINI_BADC_DIR / "cru/data/cru_ts/cru_ts_4.04/data/tmp/cru_ts4.04.1901.2019.tmp.dat.nc"

    ds = xr.open_dataset(fpath, decode_times=False)
    name = getBestName(ds['tmp'])

    assert name == "near-surface temperature (degrees Celsius)"


def test_getMissingValue():
    fpath = MINI_BADC_DIR / "cru/data/cru_ts/cru_ts_4.04/data/tmp/cru_ts4.04.1901.2019.tmp.dat.nc"

    ds = xr.open_dataset(fpath, decode_times=False)
    miss = getMissingValue(ds['tmp'])

    assert np.isclose(miss, 9.96921e+36)

 
