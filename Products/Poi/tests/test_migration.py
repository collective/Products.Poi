from zope.testing import doctest
import unittest
from Testing.ZopeTestCase import ZopeDocFileSuite as Suite
from Products.Poi.tests.ptc import PoiTestCase

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    suites = [
        Suite('migration.txt',
              package='Products.Poi.tests',
              optionflags=OPTIONFLAGS,
              test_class=PoiTestCase),
        ]
    return unittest.TestSuite(suites)
