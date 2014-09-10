import unittest

import doctest
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

from Products.Poi.tests.ptc import PoiFunctionalTestCase

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    suites = [
        Suite('browser.txt',
              package='Products.Poi.tests',
              optionflags=OPTIONFLAGS,
              test_class=PoiFunctionalTestCase),
    ]
    return unittest.TestSuite(suites)
