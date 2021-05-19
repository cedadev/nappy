from .test_nc2na import _generic_nc_to_na_test

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


