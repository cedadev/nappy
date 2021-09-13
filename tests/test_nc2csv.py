import os
import xarray as xr

from .test_nc2na import _generic_nc_to_na_test
from .common import MINI_BADC_DIR
from nappy.nc_interface.xarray_to_na import XarrayDatasetToNA


haduk_grid_nc = MINI_BADC_DIR / ("ukmo-hadobs/data/insitu/MOHC/HadOBS/HadUK-Grid/v1.0.3.0/1km/"
                     "snowLying/mon/v20210712/snowLying_hadukgrid_uk_1km_mon_197101-197112.nc")

DELIMITER = ","
EXTENSION = "csv"


def test_nc_to_csv_1001():
    _generic_nc_to_na_test(1001, delimiter=DELIMITER, extension=EXTENSION)


def test_nc_to_csv_1010():
    _generic_nc_to_na_test(1010, delimiter=DELIMITER, extension=EXTENSION)


def test_nc_to_csv_2010():
    _generic_nc_to_na_test(2010, delimiter=DELIMITER, extension=EXTENSION)


def test_nc_to_csv_3010():
    _generic_nc_to_na_test(3010, delimiter=DELIMITER, extension=EXTENSION)


def test_nc_to_csv_4010():
    _generic_nc_to_na_test(4010, delimiter=DELIMITER, extension=EXTENSION)


def test_auxiliary_vars_converted(load_ceda_test_data):
    ds = xr.open_dataset(haduk_grid_nc, use_cftime=True)

    output_dir = "."
    output_file_paths = []

    xr_to_na = XarrayDatasetToNA(ds)
    xr_to_na.convert()

    output_file = os.path.join(output_dir, f"output_01.csv")
    xr_to_na.writeNAFiles(output_file, delimiter=",")
    output_file_paths.extend(xr_to_na.output_files_written)

    expected_var_names = ['projection_x_coordinate_bnds', 'projection_y_coordinate_bnds',
                          'snowLying', 'time_bnds', 'transverse_mercator',
                          'surface_snow_area_fraction', 'month_number', 'season_year',
                          'longitude', 'latitude']

    content = ""

    for output_file in output_file_paths:
        content += open(output_file).read()

    not_found = []
    for var_name in expected_var_names:
        if var_name not in content:
            not_found.append(var_name)

    if not_found:
        raise Exception(f"Expected variables {not_found} not found in CSV files.")

    # Check time bounds are correct and not expontent formatted (requires "%.10g" format)
    last_file = output_file_paths[-1]
    lines = [l.strip() for l in open(last_file).readlines() if l.strip()]
    assert [line.startswith("time_bnds") for line in lines]
    assert "1498953,1499673" == lines[-1].strip()
