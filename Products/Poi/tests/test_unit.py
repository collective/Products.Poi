import unittest

import doctest
from Products.Poi.tests.ptc import PoiFunctionalTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite


OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return unittest.TestSuite([
        # Suite('linkdetection.txt',
        #                      package='Products.Poi.tests',
        #                      optionflags=OPTIONFLAGS),
    ])
