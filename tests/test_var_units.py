"""
test_var_units.py
===============

Tests for the var_and_units_callback option
"""

import os
import re
import pytest

from .common import data_files
import nappy


def custom_parser(string):
    """Custom parser for separating variable name from units
       Name = Non-greedy match until opening parenthesis +
              remainder after closing parenthesis
       Units = Greedy match inside parentheses
    """
    match = re.match(r'(?P<name>.*?)\((?P<units>.*)\)(?P<remainder>.*)', string)
    if match:
        return (match['name']+match['remainder'], match['units'])
    else:
        return string, ''


# Expected output without custom parser
expected1 = [('Geopotential height', 'gpm'),
             ('Temperature', 'K'),
             ('Potential vorticity (K m**2/ )', 'kg s')]

# Expected output with custom parser
expected2 = expected1.copy()
expected2[2] = ('Potential vorticity', 'K m**2/(kg s)')


@pytest.mark.parametrize(
    "parser,expected",
    [(None, expected1),
     (custom_parser, expected2)])
def test_var_units(parser, expected):

    infile = os.path.join(data_files, "2010b.na")
    fin = nappy.openNAFile(infile, var_and_units_callback=parser)
    vars = [(v[0], v[1]) for v in fin.getVariables()]
    assert vars == expected
