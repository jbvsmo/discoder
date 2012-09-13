#!/usr/bin/python
# coding: utf-8
#
# Run this file to execute all the tests
#

import glob
import unittest
import sys
import os

__author__ = 'JB'

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
sys.path.insert(0, root)

tests = [
    'libtests',
    ''
]

def find(dir):
    tests = glob.glob(os.path.join(here, dir, 'test*.py'))
    if dir:
        dir += '.'
    return [dir + os.path.splitext(os.path.basename(x))[0] for x in tests]

tests = [el for t in tests for el in find(t)]

suite = unittest.TestSuite()

for t in tests:
    try:
        # If the module defines a suite() function, call it to get the suite.
        mod = __import__(t, globals(), locals(), ['suite'])
        suitefn = getattr(mod, 'suite')
        suite.addTest(suitefn)
    except (ImportError, AttributeError):
        # else, just load all the test cases from the module.
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))


unittest.TextTestRunner(verbosity=2).run(suite)