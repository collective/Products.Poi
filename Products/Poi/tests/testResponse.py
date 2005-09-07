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
        self.tracker = self.createTracker(self.folder, 'issue-tracker')
        self.issue = self.createIssue(self.tracker)
        self.response = self.createResponse(self.issue)
        self.workflow = self.portal.portal_workflow

    def testEditResponse(self):
        self.response.setResponse('<p>Response-text</p>')
        # self.response.setAttachment(None)
        
        self.assertEqual(self.response.getResponse(), '<p>Response-text</p>')
        # self.assertEqual(self.response.getAttachment(), None)

    def testTitleIsId(self):
        self.assertEqual(self.response.Title(), self.response.getId())

    def testIsValid(self):
        self.failUnless(self.response.isValid())
        self.response.setResponse(None)
        self.failIf(self.response.isValid())

    def testRenameAfterCreation(self):
        self.failUnless(self.response.getId() == '1')
        self.createResponse(self.issue)
        self.failUnless(len(self.issue.objectIds()) == 2)
        self.failUnless('1' in self.issue.objectIds())
        self.failUnless('2' in self.issue.objectIds())

    def testSetNewIssueState(self):
        self.assertEqual(self.workflow.getInfoFor(self.issue, 'review_state'), 'unconfirmed')
        self.setRoles(['Manager'])
        self.response.setNewIssueState('accept-unconfirmed')
        self.assertEqual(self.workflow.getInfoFor(self.issue, 'review_state'), 'open')

    def testGetIssueStateBefore(self):
        self.setRoles(['Manager'])
        self.response.setNewIssueState('accept-unconfirmed')
        self.assertEqual(self.response.getIssueStateBefore(), 'unconfirmed')

    def testGetIssueStateAfter(self):
        self.setRoles(['Manager'])
        self.response.setNewIssueState('accept-unconfirmed')
        self.assertEqual(self.response.getIssueStateAfter(), 'open')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestResponse))
    return suite

if __name__ == '__main__':
    framework()
