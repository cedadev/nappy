# BSD Licence
# Copyright (c) 2010, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

import io
import os
from setuptools import setup, find_packages

from nappy import __version__


def read(filename, encoding='utf-8'):
    """read file contents"""
    full_path = os.path.join(os.path.dirname(__file__), filename)
    with io.open(full_path, encoding=encoding) as fh:
        contents = fh.read().strip()
    return contents


def license():
    return read('LICENSE')


if os.path.exists('MANIFEST'):
    os.unlink('MANIFEST')

try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError, OSError):
    LONG_DESCRIPTION='A python package for reading/writing NASA Ames files, writing NASA Ames-style CSV files and converting to/from NetCDF'

setup(
    name='nappy',
    version=__version__,
    description='NASA Ames Processing in Python',
    long_description=LONG_DESCRIPTION,
    keywords='Python CSV NASA Ames NetCDF convert xarray',
    author='Ag Stephens',
    author_email='ag.stephens@stfc.ac.uk',
    url='https://github.com/cedadev/nappy',
    license=license(),
    platforms='all',

    # We make the package non-zip_safe so that we don't need to
    # change the way ini files are read too much.
    packages=find_packages(),
    package_data={
        'nappy': [
            'config/*.ini'
        ]
    },

    include_package_data=True,
    zip_safe=False,
    install_requires=read('requirements.txt').splitlines(),
    extras_require={
        'netcdf_conversion': ['xarray']
    },
    tests_require=read('requirements_dev.txt').splitlines(),
    test_suite='nose.collector',

    entry_points={
        'console_scripts': [
            'na2nc=nappy.script.na2nc:na2nc',
            'nc2na=nappy.script.nc2na:nc2na',
            'nc2csv=nappy.script.nc2csv:nc2csv'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
],
)
