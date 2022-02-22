"""
test_var_units.py
===============

Tests for the var_and_units_callback option
"""

import os
import re
import pytest

import nappy

from .common import data_files



infile = os.path.join(data_files, "2010b.na")

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


# Expected output without custom parser - PV units incorrect
expected1 = [('Geopotential height', 'gpm'),
             ('Temperature', 'K'),
             ('Potential vorticity (K m**2/ )', 'kg s')]

# Expected output with custom parser - PV units correct
expected2 = expected1.copy()
expected2[2] = ('Potential vorticity', 'K m**2/(kg s)')


@pytest.mark.parametrize(
    "parser,expected",
    [(None, expected1),
     (custom_parser, expected2)])
def test_var_units_callback(parser, expected):
    """test the callback function for parsing VNAMEs"""
    fin = nappy.openNAFile(infile, var_and_units_callback=parser)
    variables = [(v[0], v[1]) for v in fin.getVariables()]
    assert variables == expected


def test_var_units_pattern():
    """test the possibility to set the regex that is used by default to parse VNAMEs"""
    fin = nappy.openNAFile(infile)
    default_re = re.compile(r"^\s*(.*)\((.+?)\)(.*)\s*$")
    assert fin.var_and_units_pattern == default_re
    new_re = re.compile(r'(?P<name>.*)\;\ (?P<description>.*)\;\ (?P<unit>.*)', re.UNICODE)
    fin.var_and_units_pattern = new_re
    assert fin.var_and_units_pattern == new_re

    invalid = ("a string", 555, 3.142, lambda x: x*2)
    for i in invalid:
        with pytest.raises(TypeError):
            fin.var_and_units_pattern = i
