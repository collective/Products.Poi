import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Poi.tests import ptc

default_user = ZopeTestCase.user_name

class _MockState:
    pass

class TestTracker(ptc.PoiTestCase):
    """Test tracker functionality"""

    def afterSetUp(self):
        self.tracker = self.createTracker(self.folder, 'issue-tracker')
        self.addMember('member1', 'Member One', 'member1@member.com', ['Member'], '2005-01-01')
        self.addMember('member2', 'Member Two', 'member2@member.com', ['Member'], '2005-01-01')

    def testEditTracker(self):
        self.tracker.setTitle('title')
        self.tracker.setDescription('description')
        self.tracker.setAvailableAreas(({'id' : 'area', 'title' : 'Area', 'description' : 'Issue area'},))
        self.tracker.setAvailableIssueTypes(({'id' : 'type', 'title' : 'Type', 'description' : 'Issue type'},))
        self.tracker.setAvailableSeverities(('one', 'two',))
        self.tracker.setDefaultSeverity('two')
        self.tracker.setAvailableReleases(('1.0', '2.0',))
        self.tracker.setManagers(('member1', 'member2'))
        self.tracker.setSendNotificationEmails(False)
        self.tracker.setMailingList('list@list.com')
        
        self.assertEqual(self.tracker.Title(), 'title')
        self.assertEqual(self.tracker.Description(), 'description')
        self.assertEqual(self.tracker.getAvailableAreas(), ({'id' : 'area', 'title' : 'Area', 'description' : 'Issue area'},))
        self.assertEqual(self.tracker.getAvailableIssueTypes(), ({'id' : 'type', 'title' : 'Type', 'description' : 'Issue type'},))
        self.assertEqual(self.tracker.getAvailableSeverities(), ('one', 'two',))
        self.assertEqual(self.tracker.getDefaultSeverity(), 'two')
        self.assertEqual(self.tracker.getAvailableReleases(), ('1.0', '2.0',))
        self.assertEqual(self.tracker.getManagers(), ('member1', 'member2',))
        self.assertEqual(self.tracker.getSendNotificationEmails(), False)
        self.assertEqual(self.tracker.getMailingList(), 'list@list.com')

    def testValidateTrackerManagers(self):
        self.failUnless(self.tracker.validate_managers(('member1',)) is None)
        self.failIf(self.tracker.validate_managers(('memberX',)) is None)
        self.failIf(self.tracker.validate_managers(('member1','memberX',)) is None)

    def testManagersGetLocalRole(self):
        self.failIf('Manager' in self.tracker.get_local_roles_for_userid('member1'))
        self.tracker.setManagers(('member1',))
        self.failUnless('Manager' in self.tracker.get_local_roles_for_userid('member1'))
        self.tracker.setManagers(('member2',))
        self.failIf('Manager' in self.tracker.get_local_roles_for_userid('member1'))

    def testIsUsingReleases(self):
        self.tracker.setAvailableReleases(())
        self.failIf(self.tracker.isUsingReleases())
        self.tracker.setAvailableReleases(('1.0', '2.0'))
        self.failUnless(self.tracker.isUsingReleases())

class TestEmailNotifications(ptc.PoiTestCase):
    """Test getting email addresses and sending email notifications"""
    
    def afterSetUp(self):
        self.addMember('member1', 'Member One', 'member1@member.com', ['Member'], '2005-01-01')
        self.addMember('member2', 'Member Two', 'member2@member.com', ['Member'], '2005-01-01')
        self.addMember('member3', 'Member Three', 'member3@member.com', ['Member'], '2005-01-01')
        self.tracker = self.createTracker(self.folder, 'issue-tracker', managers = ('member1', 'member2'), sendNotificationEmails = True)

    def testGetAddressesWithNotificationsOff(self):
        self.tracker.setSendNotificationEmails(False)
        issue = self.createIssue(self.tracker, contactEmail='submitter@domain.com', watchers=('member2', 'member3',))
        addresses = self.tracker.getNotificationEmailAddresses(issue)
        self.failUnless(len(addresses) == 0)

    def testGetAddressesOnNewIssue(self):
        addresses = self.tracker.getNotificationEmailAddresses()
        self.failUnless(len(addresses) == 2)
        self.failUnless('member1@member.com' in addresses)
        self.failUnless('member2@member.com' in addresses)
        
    def testGetAddressesOnNewIssueWithList(self):
        self.tracker.setMailingList('list@list.com')
        addresses = self.tracker.getNotificationEmailAddresses()
        self.failUnless(len(addresses) == 1)
        self.failUnless('list@list.com' in addresses)

    def testGetAddressesOnNewResponse(self):
        issue = self.createIssue(self.tracker, contactEmail='submitter@domain.com', watchers=('member2', 'member3',))
        addresses = self.tracker.getNotificationEmailAddresses(issue)
        self.failUnless(len(addresses) == 4)
        self.failUnless('member1@member.com' in addresses)
        self.failUnless('member2@member.com' in addresses)
        self.failUnless('member3@member.com' in addresses)
        self.failUnless('submitter@domain.com' in addresses)

    def testGetAddressesOnNewResponseWithList(self):
        self.tracker.setMailingList('list@list.com')
        issue = self.createIssue(self.tracker, contactEmail='submitter@domain.com', watchers=('member2', 'member3',))
        addresses = self.tracker.getNotificationEmailAddresses(issue)
        self.failUnless(len(addresses) == 4)
        self.failUnless('list@list.com' in addresses)
        self.failUnless('submitter@domain.com' in addresses)
        self.failUnless('member2@member.com' in addresses)
        self.failUnless('member3@member.com' in addresses)

    def testGetTagsInUse(self):
        self.createIssue(self.tracker, tags=('A', 'B',))
        self.createIssue(self.tracker, tags=('B', 'C',))
        self.createIssue(self.tracker, tags=('A', 'D',))
        self.assertEqual(self.tracker.getTagsInUse(), ['A', 'B', 'C', 'D'])

    
    # The following tests don't map directly to functional methods but are
    # meant to make sure no errors arise from sending emails
    # -- begin email tests
    # TODO: re-enable these tests as soon as the Mailhost mock object is put
    # in place

#    def testNewIssueEmail(self):
#        self.tracker.setSendNotificationEmails(True)
#        self.tracker.update(title='Random Tracker')
#        issue = self.createIssue(self.tracker,
#                                 contactEmail='submitter@domain.com', 
#                                 watchers=('member1', 'member2',))
#        issue.sendNotificationMail()
#
#    def testNewResponseEmail(self):
#        self.tracker.setSendNotificationEmails(True)
#        self.tracker.update(title='Random Tracker')
#        issue = self.createIssue(self.tracker, 
#                                 contactEmail='submitter@domain.com', 
#                                 watchers=('member1', 'member2',))
#        response = self.createResponse(issue)
#        response.sendNotificationMail()
#
#    def testResolvedEmail(self):
#        self.tracker.setSendNotificationEmails(True)
#        self.tracker.update(title='Random Tracker')
#        
#        issue = self.createIssue(self.tracker, 
#                                 contactEmail='submitter@domain.com', 
#                                 watchers=('member1', 'member2',))
#
#        from Products.Poi.Extensions import poi_issue_workflow_scripts as wfScripts
#        state = _MockState()
#        state.object = issue
#        wfScripts.sendResolvedMail(self.portal, state)
    
    # -- end email tests


class TestTrackerSearch(ptc.PoiTestCase):
    """Test tracker search functionality"""

    def afterSetUp(self):
        self.tracker = self.createTracker(self.folder, 'issue-tracker')
        self.workflow = self.portal.portal_workflow

    def testGetFilteredIssesByRelease(self):
        self.createIssue(self.tracker, release='2.0')
        self.createIssue(self.tracker, release='2.0')
        self.createIssue(self.tracker, release='1.0')
        issues = [b.getId for b in self.tracker.getFilteredIssues(release='2.0')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in self.tracker.getFilteredIssues(release='1.0')]
        issues.sort()
        self.assertEqual(issues, ['3'])
        
    def testGetFilteredIssesByArea(self):
        self.createIssue(self.tracker, area='ui')
        self.createIssue(self.tracker, area='ui')
        self.createIssue(self.tracker, area='functionality')
        issues = [b.getId for b in self.tracker.getFilteredIssues(area='ui')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in self.tracker.getFilteredIssues(area='functionality')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByIssueType(self):
        self.createIssue(self.tracker, issueType='bug')
        self.createIssue(self.tracker, issueType='bug')
        self.createIssue(self.tracker, issueType='feature')
        issues = [b.getId for b in self.tracker.getFilteredIssues(issueType='bug')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in self.tracker.getFilteredIssues(issueType='feature')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesBySeverity(self):
        self.createIssue(self.tracker, severity='Medium')
        self.createIssue(self.tracker, severity='Medium')
        self.createIssue(self.tracker, severity='Critical')
        issues = [b.getId for b in self.tracker.getFilteredIssues(severity='Medium')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in self.tracker.getFilteredIssues(severity='Critical')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByState(self):
        self.createIssue(self.tracker)
        self.createIssue(self.tracker)
        self.createIssue(self.tracker)
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.tracker['3'], 'accept-unconfirmed')
        self.setRoles(['Member'])
        issues = [b.getId for b in self.tracker.getFilteredIssues(state='unconfirmed')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in self.tracker.getFilteredIssues(state='open')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByCreator(self):
        self.createIssue(self.tracker)
        self.createIssue(self.tracker)
        self.createIssue(self.tracker)
        self.tracker['1'].setCreators(('some_member',))
        self.tracker['1'].reindexObject()
        self.tracker['2'].setCreators(('some_member',))
        self.tracker['2'].reindexObject()
        self.tracker['3'].setCreators(('another_member',))
        self.tracker['3'].reindexObject()
        
        issues = [b.getId for b in self.tracker.getFilteredIssues(creator='some_member')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in self.tracker.getFilteredIssues(creator='another_member')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByResponsible(self):
        self.createIssue(self.tracker, responsibleManager='manager1')
        self.createIssue(self.tracker, responsibleManager='manager1')
        self.createIssue(self.tracker, responsibleManager='manager2')
        issues = [b.getId for b in self.tracker.getFilteredIssues(responsible='manager1')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in self.tracker.getFilteredIssues(responsible='manager2')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByTags(self):
        self.createIssue(self.tracker, tags=('A', 'B',))
        self.createIssue(self.tracker, tags=('B', 'C',))
        self.createIssue(self.tracker, tags=('A', 'D',))
        issues = [b.getId for b in self.tracker.getFilteredIssues(tags='B')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in self.tracker.getFilteredIssues(tags=('A', 'D',))]
        issues.sort()
        self.assertEqual(issues, ['1', '3'])

    def testGetFilteredIssesByIssueText(self):
        self.createIssue(self.tracker, overview="foo")
        self.createIssue(self.tracker, details="foo")
        self.createIssue(self.tracker, overview="bar", details="baz")
        issues = [b.getId for b in self.tracker.getFilteredIssues(text='foo')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in self.tracker.getFilteredIssues(text='bar')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByResponseText(self):
        self.createIssue(self.tracker, overview="foo")
        self.createIssue(self.tracker)
        self.createIssue(self.tracker)
        
        self.createResponse(self.tracker['2'], text='foo')
        self.createResponse(self.tracker['3'], text='bar')
        
        self.tracker['1'].updateResponses()
        self.tracker['2'].updateResponses()
        self.tracker['3'].updateResponses()
        
        issues = [b.getId for b in self.tracker.getFilteredIssues(text='foo')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in self.tracker.getFilteredIssues(text='bar')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesComplex(self):
        self.createIssue(self.tracker, overview="foo", area="ui", issueType='feature')
        self.createIssue(self.tracker, area="ui", issueType="bug")
        self.createIssue(self.tracker, area="functionality", details="foo", issueType='bug')
        
        issues = [b.getId for b in self.tracker.getFilteredIssues(text='foo', area='ui')]
        issues.sort()
        self.assertEqual(issues, ['1'])
        
        issues = [b.getId for b in self.tracker.getFilteredIssues(area='ui', issueType='feature')]
        issues.sort()
        self.assertEqual(issues, ['1'])

        issues = [b.getId for b in self.tracker.getFilteredIssues(area='ui', issueType=['feature', 'bug'])]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTracker))
    suite.addTest(makeSuite(TestTrackerSearch))
    suite.addTest(makeSuite(TestEmailNotifications))
    return suite

if __name__ == '__main__':
    framework()
