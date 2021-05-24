#!/usr/bin/env python

"""
right_strip.py
==============

Holds the rightStripCurlyBraces() function used to right strip any curly braces 
annotations from lines in a text file.

E.g.:

In:  36   1001                              {NLHEAD  FFI}
Out: 36   1001

In:  Tout (C)            {Out-boarding air temperature}
Out: Tout (C) 

"""

import re

rstrip_regex = re.compile(r"^(.+)\{[^{^}]*\}\s*$")


def rightStripCurlyBraces(line):
    """
    Returns line but with curly braces right stripped off.
    """
    match = rstrip_regex.match(line)
    if not match: return line

    return match.groups()[0]


if __name__ == "__main__":

    test_lines = """
    36   1001                              {NLHEAD  FFI}
    MDB {remove me}
    34,56,23 {ddfsd {remove me now}
    {h3lo} {world}    {IVOL NVOL}   	 
    1 1 1 1 1 1 1 1 1  {lots of }  2 2 2 2 2 2      {NUMBERS}
    trouble { { sdfsd } } } {} eat food {...} {...}
    fairy god {mother} 						{hello
    traffic 2k  2.71  5.32  -14.22 6.55   204.85  -0.41   67.8305 {{{don't worry}}}
    will this {erase}}
    21                                    {NV}
    1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
    Tout (C)            {Out-boarding air temperature}
    Uwind (m/s)         {Absolute value of wind velocity}
    1                                      {NNCOML}
    """.split("\n")

    for line in test_lines:
        print("INPUT:  %s" % line)
        print("OUTPUT: %s" % rightStripCurlyBraces(line))


