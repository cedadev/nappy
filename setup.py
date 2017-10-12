# BSD Licence
# Copyright (c) 2010, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

from setuptools import setup, find_packages

setup(
      name='nappy',
      version='1.1.2',

      description = 'NASA Ames Processing in Python',
      long_description = "A python package for reading/writing NASA Ames files, writing NASA Ames-style CSV files and converting to/from NetCDF (if CDMS enabled).",
      keywords = 'Python CSV NASA Ames NetCDF convert CDMS',
      author = 'Ag Stephens',
      author_email = 'ag.stephens@stfc.ac.uk',
      url = 'http://proj.badc.rl.ac.uk/cows/wiki/CowsSupport/Nappy',
      #classifiers = [],

      # We make the package non-zip_safe so that we don't need to
      # change the way ini files are read too much.
      packages = find_packages('lib', exclude=['tests', 'tests.*']),
      package_dir={'': 'lib'},

      include_package_data = True,
      zip_safe = False,

      tests_require = ['nose'],
      test_suite = 'nose.collector',

      entry_points = '''
      [console_scripts]
      na2nc = nappy.script.na2nc:na2nc
      nc2na = nappy.script.nc2na:nc2na
      nc2csv = nappy.script.nc2csv:nc2csv
      ''',
      
)
