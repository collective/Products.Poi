import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

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
        self.response.setResponse('Response-text', mimetype='text/x-web-intelligent')
        self.assertEqual(self.response.getResponse(), 'Response-text')

    def testTitleIsId(self):
        self.assertEqual(self.response.Title(), self.response.getId())

    def testIsValid(self):
        self.failUnless(self.response.isValid())

        self.response.setResponse(None, mimetype='text/x-web-intelligent')
        self.failIf(self.response.isValid())

        self.response.setResponse('some text', mimetype='text/x-web-intelligent')
        self.failUnless(self.response.isValid())
        
        self.response.setResponse(None, mimetype='text/x-web-intelligent')
        self.response.setNewSeverity('Critical')
        self.failUnless(self.response.isValid())
        
        
    def testIsValidWithTransition(self):
        self.failUnless(self.response.isValid())

        self.response.setResponse(None, mimetype='text/x-web-intelligent')
        self.failIf(self.response.isValid())
        
        # The vocabulary function is picky about roles and such
        self.setRoles(('Manager',)) 
        self.response.setNewIssueState('accept-unconfirmed')
        self.failUnless(self.response.isValid())

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

    def testSetNewTargetRelease(self):
        self.assertEqual(self.issue.getTargetRelease(), '(UNASSIGNED)')
        self.response.setNewTargetRelease('2.0')
        self.assertEqual(self.issue.getTargetRelease(), '2.0')

        
    def testGetIssueChanges(self):
        changes = self.response.getIssueChanges()
        self.assertEqual(changes, ())
        self.setRoles(['Manager'])
        self.response.setNewIssueState('accept-unconfirmed')
        self.response.setNewResponsibleManager('member1')
        self.response.setNewSeverity('Important')
        self.response.setNewTargetRelease('2.0')
        changes = changes = self.response.getIssueChanges()
        self.assertEqual(changes[0], {'id' : 'review_state', 'name' : 'Issue state', 'before' : 'unconfirmed', 'after' : 'open'})
        self.assertEqual(changes[1], {'id' : 'responsible_manager', 'name' : 'Responsible manager', 'before' : '(UNASSIGNED)', 'after' : 'member1'})
        self.assertEqual(changes[2], {'id' : 'severity', 'name' : 'Severity', 'before' : 'Medium', 'after' : 'Important'})
        self.assertEqual(changes[3], {'id' : 'target_release', 'name' : 'Target release', 'before' : 'None', 'after' : '2.0'})

    def testTransform(self):
        self.response.setResponse('Make this a link http://test.com', mimetype='text/x-web-intelligent')
        self.assertEqual(self.response.getResponse(), 'Make this a link <a href="http://test.com" rel="nofollow">http://test.com</a>')

    def testAccentedCharacters(self):
        catalog = self.portal.portal_catalog
        issue = self.createIssue(self.tracker,
                                 title=u"été est belle.",
                                 details=u"C'est plus belle à Café René.")
        found = len(catalog.searchResults(portal_type = 'PoiIssue',
                                          SearchableText = u"été")) >= 1
        self.failUnless(found)
        found = len(catalog.searchResults(portal_type = 'PoiIssue',
                                          SearchableText = u"René")) >= 1
        self.failUnless(found)

        response = self.createResponse(issue, u"In Dutch 'seas' is 'zeeën'")
        # That should show up in both the response and the issue.
        found = len(catalog.searchResults(portal_type = 'PoiResponse',
                                          SearchableText = u"zeeën")) >= 1
        self.failUnless(found)
        found = len(catalog.searchResults(portal_type = 'PoiIssue',
                                          SearchableText = u"zeeën")) >= 1
        self.failUnless(found)


class TestKnownIssues(ptc.PoiTestCase):
    """Test bugs with responses"""

    def afterSetUp(self):
        self.addMember('member1', 'Member One', 'member1@member.com', ['Member'], '2005-01-01')
        self.tracker = self.createTracker(self.folder, 'issue-tracker', managers=('member1',))
        self.issue = self.createIssue(self.tracker, 'an-issue')
        self.response = self.createResponse(self.issue, 'a-response')
        self.catalog = self.portal.portal_catalog
        
    def testDeleteResponseLeavesStaleDescription(self):
        found = len(self.catalog.searchResults(portal_type = 'PoiIssue', SearchableText = 'a-response')) >= 1
        self.failUnless(found)
        self.issue._delObject('1')
        self.failIf('a-response' in self.issue.SearchableText())
        found = len(self.catalog.searchResults(portal_type = 'PoiIssue', SearchableText = 'a-response')) >= 1
        self.failIf(found, 'KNOWN ISSUE: Deleted response causes stale issue SearchableText')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestResponse))
    suite.addTest(makeSuite(TestKnownIssues))
    return suite

if __name__ == '__main__':
    framework()
