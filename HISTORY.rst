Version History
===============

v2.0.3 (06/02/2024)
-------------------

Bug Fixes
^^^^^^^^^
* Fixed problem with `pip install` failing (by moving `import numpy` line).

v2.0.2 (10/03/2022)
-------------------

Bug Fixes
^^^^^^^^^
* Fixed bugs in `getAuxVariable()` and `getAuxVariables()`

New Features
^^^^^^^^^^^^
* Option to supply a custom parser function to split variable names from units:
  * Implemented using ``var_and_units_pattern`` as an attribute with a ``@setter`` which can 
    be modified after creating the ``NAFile`` object with ``openNAFile``.

Breaking Changes
^^^^^^^^^^^^^^^^
* Removed support for Python3.6.

v2.0.1 (28/09/2021)
-------------------
Bug Fixes
^^^^^^^^^
* Added ``requirements_dev.txt`` to manifest file because it is read by ``setup.py``.

v2.0.0 (27/09/2021)
-------------------
Bug Fixes
^^^^^^^^^
N/A

Breaking Changes
^^^^^^^^^^^^^^^^
* Changed ``nc_interface`` sub-package to rely on ``xarray`` instead of ``cdms2``.

New Features
^^^^^^^^^^^^
* Changed ``nc_interface`` sub-package to rely on ``xarray`` instead of ``cdms2``.
* Added unit tests for all new code in ``tests``
  * Run tests with: ``pytest tests``

v1.1.4 (2017-10-13)
-------------------

Overview
^^^^^^^^

* includes unit tests
* includes ``nc_interface`` to netCDF - using `cdms2` library

