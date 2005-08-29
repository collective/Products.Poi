#
# Skeleton ContextHelpTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Poi.tests import ptc


class TestResponse(ptc.PoiTestCase):
    """Test response functionality"""

    def afterSetUp(self):
        self.folder.invokeFactory('PoiTracker', 'tracker')
        self.tracker = self.folder.tracker
        self.tracker.invokeFactory('PoiIssue', '1')
        self.issue = self.tracker['1']
        self.issue.invokeFactory('PoiResponse', '1')
        self.response = self.issue['1']

    def testEditResponse(self):
        pass

    def testTitleIsId(self):
        pass

    def testIsValid(self):
        pass

    def testRenameAfterCreation(self):
        pass

    def testSetNewIssueState(self):
        pass

    def testGetIssueStateBefore(self):
        pass

    def testGetIssueStateAfter(self):
        pass

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestResponse))
    return suite

if __name__ == '__main__':
    framework()
