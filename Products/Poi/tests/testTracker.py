#
# Skeleton ContextHelpTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Poi.tests import ptc


class TestTracker(ptc.PoiTestCase):
    """Test tracker functionality"""

    def afterSetUp(self):
        self.tracker = self.createTracker(self.folder, 'issue-tracker')

    def testEditTracker(self):
        pass

    def testValidateTrackerManagers(self):
        pass

    def testManagersGetLocalRole(self):
        pass

    def testIsUsingReleases(self):
        pass

    def testClosedTracker(self):
        pass

    def testOpenTracker(self):
        pass

class TestTrackerSearch(ptc.PoiTestCase):
    """Test tracker search functionality"""

    def afterSetUp(self):
        self.tracker = self.createTracker(self.folder, 'issue-tracker')

    def testGetFilteredIssesByRelease(self):
        pass

    def testGetFilteredIssesByArea(self):
        pass

    def testGetFilteredIssesByIssueType(self):
        pass

    def testGetFilteredIssesByState(self):
        pass

    def testGetFilteredIssesBySubmitter(self):
        pass

    def testGetFilteredIssesByResponsible(self):
        pass

    def testGetFilteredIssesByIssueText(self):
        pass

    def testGetFilteredIssesByResponseText(self):
        pass

    def testGetFilteredIssesComplex(self):
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTracker))
    suite.addTest(makeSuite(TestTrackerSearch))
    return suite

if __name__ == '__main__':
    framework()
