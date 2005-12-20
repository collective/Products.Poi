import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Poi.tests import ptc


class TestResponse(ptc.PoiTestCase):
    """Test response functionality"""

    def afterSetUp(self):
        self.addMember('member1', 'Member One', 'member1@member.com', ['Member'], '2005-01-01')
        self.tracker = self.createTracker(self.folder, 'issue-tracker', managers=('member1',))
        self.issue = self.createIssue(self.tracker, 'an-issue')
        self.response = self.createResponse(self.issue, 'a-response')
        self.workflow = self.portal.portal_workflow

    def testEditResponse(self):
        self.response.setResponse('<p>Response-text</p>')
        self.assertEqual(self.response.getResponse(), '<p>Response-text</p>')

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

    def testSetNewResponsibleManager(self):
        self.assertEqual(self.issue.getResponsibleManager(), '(UNASSIGNED)')
        self.response.setNewResponsibleManager('member1')
        self.assertEqual(self.issue.getResponsibleManager(), 'member1')
        
    def testSetNewSeverity(self):
        self.assertEqual(self.issue.getSeverity(), 'Medium')
        self.response.setNewSeverity('Important')
        self.assertEqual(self.issue.getSeverity(), 'Important')
        
    def testGetIssueChanges(self):
        changes = self.response.getIssueChanges()
        self.assertEqual(changes, ())
        self.setRoles(['Manager'])
        self.response.setNewIssueState('accept-unconfirmed')
        self.response.setNewResponsibleManager('member1')
        self.response.setNewSeverity('Important')
        changes = changes = self.response.getIssueChanges()
        self.assertEqual(changes[0], {'id' : 'review_state', 'name' : 'Issue state', 'before' : 'unconfirmed', 'after' : 'open'})
        self.assertEqual(changes[1], {'id' : 'responsible_manager', 'name' : 'Responsible manager', 'before' : '(UNASSIGNED)', 'after' : 'member1'})
        self.assertEqual(changes[2], {'id' : 'severity', 'name' : 'Severity', 'before' : 'Medium', 'after' : 'Important'})
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestResponse))
    return suite

if __name__ == '__main__':
    framework()
