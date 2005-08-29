#
# Skeleton ContextHelpTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Poi.tests import ptc


class TestPscTracker(ptc.PoiTestCase):
    """Test psc tracker functionality"""

    def afterSetUp(self):
        pass

    def testTrackedAllowedInProject(self):
        pass

    def testNoReleasesInSchema(self):
        pass

    def testReleasesVocab(self):
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPscTracker))
    return suite

if __name__ == '__main__':
    framework()
