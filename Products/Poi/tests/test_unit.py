import unittest

import doctest

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return unittest.TestSuite([
        doctest.DocTestSuite(module='Products.Poi.browser.response',
                             optionflags=OPTIONFLAGS),
        doctest.DocFileSuite('responses.txt',
                             package='Products.Poi.tests',
                             optionflags=OPTIONFLAGS),
        doctest.DocFileSuite('linkdetection.txt',
                             package='Products.Poi.tests',
                             optionflags=OPTIONFLAGS),
    ])
