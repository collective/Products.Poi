# -*- coding: utf-8 -*-
from Testing import ZopeTestCase
from collective.watcherlist.interfaces import IWatcherList
from plone.app.textfield.value import RichTextValue
from zope.schema import getFields

from Products.Poi.events import sendResponseNotificationMail
from Products.Poi.interfaces import ITracker
from Products.Poi.tests import ptc
from Products.Poi.utils import link_bugs
from Products.Poi.utils import link_repo

default_user = ZopeTestCase.user_name


class TestTracker(ptc.PoiTestCase):
    """Test tracker functionality"""

    def afterSetUp(self):
        self.tracker = self.createTracker(self.folder, 'issue-tracker')
        self.addMember('member1', 'Member One', 'member1@example.com',
                       ['Member'], '2005-01-01')
        self.addMember('member2', 'Member Two', 'member2@example.com',
                       ['Member'], '2005-01-01')

    def testEditTracker(self):
        self.tracker.title = u'title'
        self.tracker.description = u'description'
        self.tracker.help_text = ptc.rich_text(u'help text')
        self.tracker.available_areas = [
            {'id': u'area', 'title': u'Area', 'description': u'Issue area'}
        ]
        self.tracker.available_issue_types = [
            {'id': u'type', 'title': u'Type', 'description': u'Issue type'}
        ]
        self.tracker.available_severities = [u'one', u'two']
        self.tracker.default_severity = u'two'
        self.tracker.available_releases = [u'1.0', u'2.0']
        self.tracker.assignees = [u'member1', u'member2']
        self.tracker.notification_emails = False
        self.tracker.mailing_list = u'list@example.com'

        self.assertEqual(self.tracker.title, u'title')
        self.assertEqual(self.tracker.description, u'description')
        self.assertEqual(self.tracker.help_text.output, u'<p>help text</p>')
        self.assertEqual(
            self.tracker.available_areas,
            [{'id': u'area', 'title': u'Area', 'description': u'Issue area'}]
        )
        self.assertEqual(
            self.tracker.available_issue_types,
            [{'id': u'type', 'title': u'Type', 'description': u'Issue type'}]
        )
        self.assertEqual(self.tracker.available_severities, [u'one', u'two'])
        self.assertEqual(self.tracker.default_severity, u'two')
        self.assertEqual(self.tracker.available_releases, [u'1.0', u'2.0'])
        self.assertEqual(self.tracker.assignees, [u'member1', u'member2'])
        self.assertEqual(self.tracker.notification_emails, False)
        self.assertEqual(self.tracker.mailing_list, u'list@example.com')

    def testDataGridFields(self):
        """
        The DataGridFields should have at least one entry, as they are
        required.  We get problems when adding an Issue if we are not
        careful.  See http://plone.org/products/poi/issues/139

        """
        # This is what a real entry looks like:
        real_entry = {'description': u'Something nice.',
                      'short_name': u'something',
                      'orderindex_': u'1',
                      'title': u'Something'}

        fields = getFields(ITracker)
        # Test the availableAreas field.
        field = fields['available_areas']
        input = [real_entry]
        self.assertEqual(field.validate(input), None)

        # Test the availableIssueTypes field.
        field = fields['available_issue_types']
        input = [real_entry]
        self.assertEqual(field.validate(input), None)

    def testIsUsingReleases(self):
        self.tracker.available_releases = []
        self.failIf(self.tracker.isUsingReleases())
        self.tracker.available_releases = [u'1.0', u'2.0']
        self.failUnless(self.tracker.isUsingReleases())


class TestEmailNotifications(ptc.PoiTestCase):
    """Test getting email addresses and sending email notifications"""

    def afterSetUp(self):
        self.addMember('member1', 'Member One', 'member1@example.com',
                       ['Member'], '2005-01-01')
        self.addMember('member2', 'Member Two', 'member2@example.com',
                       ['Member'], '2005-01-01')
        self.addMember('member3', 'Member Three', 'member3@example.com',
                       ['Member'], '2005-01-01')
        self.tracker = self.createTracker(
            self.folder, 'issue-tracker', assignees=('member1', 'member2'),
            sendNotificationEmails=True)

    def testGetAddressesWithNotificationsOff(self):
        self.tracker.notification_emails = False
        issue = self.createIssue(
            self.tracker, contactEmail='submitter@example.com',
            watchers=[u'member2', u'member3'], assignee=u'member2')
        watcherlist = IWatcherList(issue)
        # We have two watchers directly on this issue, plus the submitter:
        watchers = watcherlist.watchers
        self.assertEqual(len(watchers), 3)
        # But since emails are not sent, we have zero addresses:
        addresses = watcherlist.addresses
        self.assertEqual(len(addresses), 0)

    def testGetAddressesOnNewIssue(self):
        self.tracker.mailing_list = None
        assignees = self.tracker.assignees
        self.assertEqual(len(assignees), 2)
        self.failUnless('member1' in assignees)
        self.failUnless('member2' in assignees)
        # issue creator should be a watcher
        issue = self.createIssue(
            self.tracker, contactEmail='submitter@example.com',
            watchers=None, assignee=u'member2')
        addresses = IWatcherList(issue).addresses
        self.failUnless('member2@example.com' in addresses)
        self.failUnless('submitter@example.com' in addresses)

    def testGetAddressesOnNewIssueWithList(self):
        self.tracker.mailing_list = 'list@example.com'
        addresses = IWatcherList(self.tracker).addresses
        # Addresses are the mailing list and the tracker assignees.
        self.assertEqual(len(addresses), 1)
        self.failUnless('list@example.com' in addresses)

    def testGetAddressesOnNewResponse(self):
        issue = self.createIssue(
            self.tracker, contactEmail='submitter@example.com',
            watchers=[u'member1', u'member3'], assignee=u'member2')
        addresses = IWatcherList(issue).addresses
        self.assertEqual(len(addresses), 5)
        self.failUnless('member1@example.com' in addresses)
        self.failUnless('member2@example.com' in addresses)
        self.failUnless('member3@example.com' in addresses)
        self.failUnless('submitter@example.com' in addresses)

    def testGetAddressesOnNewResponseWithList(self):
        self.tracker.mailing_list = 'list@example.com'
        issue = self.createIssue(
            self.tracker, contactEmail='submitter@example.com',
            watchers=[u'member1', u'member3'], assignee=u'member2')
        addresses = IWatcherList(issue).addresses
        self.assertEqual(len(addresses), 5)
        # mailing list:
        self.failUnless('list@example.com' in addresses)
        # submitter:
        self.failUnless('submitter@example.com' in addresses)
        # tracker assignee:
        self.failUnless('member1@example.com' in addresses)
        # direct subscribers:
        self.failUnless('member2@example.com' in addresses)
        self.failUnless('member3@example.com' in addresses)

    def testGetTagsInUse(self):
        self.createIssue(self.tracker, tags=('A', 'B'), assignee=u'member2')
        self.createIssue(self.tracker, tags=('B', 'C'), assignee=u'member2')
        self.createIssue(self.tracker, tags=('A', 'D'), assignee=u'member2')
        self.assertEqual(self.tracker.getAllTags(), ['A', 'B', 'C', 'D'])
        self.assertEqual(self.tracker.getTagsInUse(),
                         [('A', 2), ('B', 2), ('C', 1), ('D', 1)])

    # The following tests don't map directly to functional methods but are
    # meant to make sure no errors arise from sending emails
    # -- begin email tests

    def testNewIssueEmail(self):
        self.tracker.notification_emails = True
        self.tracker.title = 'Random Tracker'
        # Just creating it should be enough to send an email.
        self.createIssue(self.tracker,
                         contactEmail='submitter@example.com',
                         watchers=[u'member1', u'member2'], assignee=u'member2')
        # A mail is sent immediately on creation of this issue.
        self.assertEqual(len(self.portal.MailHost.messages), 3)

    def testSpecialCharacterIssueEmail(self):
        self.tracker.notification_emails = True
        self.tracker.update(title='Random Tracker')
        issue = self.createIssue(
            self.tracker,
            title="accented vowels: à è ì",
            contactEmail='submitter@example.com',
            watchers=[u'member1', u'member2'])
        self.createResponse(
            issue, text="more accented vowels: ò ù")
        sendResponseNotificationMail(issue)

        # Now try a different charset
        self.portal.email_charset = 'iso-8859-1'
        issue = self.createIssue(
            self.tracker,
            title=u"accented vowels: à è ì ò ù".encode('utf-8'),
            contactEmail='submitter@example.com',
            watchers=[u'member1', u'member2'])
        self.createResponse(
            issue, text=u"more accented vowels: ò ù".encode('iso-8859-1'))
        sendResponseNotificationMail(issue)

    def testNewResponseEmail(self):
        self.tracker.notification_emails = True
        self.tracker.update(title='Random Tracker')
        issue = self.createIssue(self.tracker,
                                 contactEmail='submitter@example.com',
                                 watchers=[u'member1', u'member2'])
        self.createResponse(issue)
        sendResponseNotificationMail(issue)

    def testResolvedEmail(self):
        self.tracker.notification_emails = True
        self.tracker.update(title='Random Tracker')

        issue = self.createIssue(self.tracker,
                                 contactEmail='submitter@example.com',
                                 watchers=[u'member1', u'member2'])
        self.loginAsPortalOwner()
        workflow = self.portal.portal_workflow
        workflow.doActionFor(issue, 'resolve-unconfirmed')

    # -- end email tests


class TestTrackerSearch(ptc.PoiTestCase):
    """Test tracker search functionality"""

    def afterSetUp(self):
        self.tracker = self.createTracker(
            self.folder,
            'issue-tracker',
            assignees=[
                u'member1', u'member2', u'member3',
                u'manager1', u'manager2', u'manager3'
            ],
        )
        self.workflow = self.portal.portal_workflow
        self.issuefolder = self.tracker.restrictedTraverse('@@issuefolder')

    def testGetFilteredIssuesById(self):
        self.createIssue(self.tracker, assignee=u'member2')
        self.createIssue(self.tracker, assignee=u'member2')
        self.createIssue(self.tracker, assignee=u'member2')
        issues = [b.getId for b in self.issuefolder.getFilteredIssues(id='1')]
        self.assertEqual(issues, [u'1'])
        issues = [b.getId for b in self.issuefolder.getFilteredIssues(id='2')]
        self.assertEqual(issues, [u'2'])

    def testGetFilteredIssesByRelease(self):
        self.createIssue(self.tracker, release=u'2.0', assignee=u'member2')
        self.createIssue(self.tracker, release=u'2.0', assignee=u'member2')
        self.createIssue(self.tracker, release=u'1.0', assignee=u'member2')
        issues = sorted([b.getId
                         for b in self.issuefolder.getFilteredIssues(release=u'2.0')])
        self.assertEqual(issues, [u'1', u'2'])
        issues = [b.getId
                  for b in self.issuefolder.getFilteredIssues(release=u'1.0')]
        issues.sort()
        self.assertEqual(issues, [u'3'])

    def testGetFilteredIssesByArea(self):
        self.createIssue(self.tracker, assignee=u'member2', area=u'ui')
        self.createIssue(self.tracker, assignee=u'member2', area=u'ui')
        self.createIssue(self.tracker, assignee=u'member2', area=u'functionality')
        issues = sorted([b.getId
                         for b in self.issuefolder.getFilteredIssues(area=u'ui')])
        self.assertEqual(issues, [u'1', u'2'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(area=u'functionality')]
        issues.sort()
        self.assertEqual(issues, [u'3'])

    def testGetFilteredIssesByIssueType(self):
        self.createIssue(self.tracker, issueType=u'bug', assignee=u'member2')
        self.createIssue(self.tracker, issueType=u'bug', assignee=u'member2')
        self.createIssue(self.tracker, issueType=u'feature', assignee=u'member2')
        issues = sorted([b.getId for b in
                         self.issuefolder.getFilteredIssues(issueType=u'bug')])
        self.assertEqual(issues, [u'1', u'2'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(issueType=u'feature')]
        issues.sort()
        self.assertEqual(issues, [u'3'])

    def testGetFilteredIssesBySeverity(self):
        self.createIssue(self.tracker, severity=u'Medium', assignee=u'member2')
        self.createIssue(self.tracker, severity=u'Medium', assignee=u'member2')
        self.createIssue(self.tracker, severity=u'Critical', assignee=u'member2')
        issues = sorted([b.getId for b in
                         self.issuefolder.getFilteredIssues(severity=u'Medium')])
        self.assertEqual(issues, [u'1', u'2'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(severity=u'Critical')]
        issues.sort()
        self.assertEqual(issues, [u'3'])

    def testGetFilteredIssesByTargetRelease(self):
        self.createIssue(self.tracker, targetRelease=u'2.0', assignee=u'member2')
        self.createIssue(self.tracker, targetRelease=u'2.0', assignee=u'member2')
        self.createIssue(self.tracker, targetRelease=u'1.0', assignee=u'member2')
        issues = sorted([b.getId for b in
                         self.issuefolder.getFilteredIssues(targetRelease=u'2.0')])
        self.assertEqual(issues, [u'1', u'2'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(targetRelease=u'1.0')]
        issues.sort()
        self.assertEqual(issues, [u'3'])

    def testGetFilteredIssesByState(self):
        self.createIssue(self.tracker, assignee=u'member2')
        self.createIssue(self.tracker, assignee=u'member2')
        self.createIssue(self.tracker, assignee=u'member2')
        self.setRoles(['TrackerManager'])
        self.workflow.doActionFor(self.tracker['3'], 'accept-unconfirmed')
        self.setRoles(['Member'])
        issues = sorted([b.getId for b in
                         self.issuefolder.getFilteredIssues(state='unconfirmed')])
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(state='open')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByCreator(self):
        self.createIssue(self.tracker, assignee=u'member2')
        self.createIssue(self.tracker, assignee=u'member2')
        self.createIssue(self.tracker, assignee=u'member2')
        self.tracker['1'].setCreators(('some_member', ))
        self.tracker['1'].reindexObject()
        self.tracker['2'].setCreators(('some_member', ))
        self.tracker['2'].reindexObject()
        self.tracker['3'].setCreators(('another_member', ))
        self.tracker['3'].reindexObject()

        issues = sorted([b.getId for b in
                         self.issuefolder.getFilteredIssues(creator='some_member')])
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(creator='another_member')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByResponsible(self):
        self.createIssue(self.tracker, assignee=u'manager1')
        self.createIssue(self.tracker, assignee=u'manager1')
        self.createIssue(self.tracker, assignee=u'manager2')
        issues = sorted([b.getId for b in
                         self.issuefolder.getFilteredIssues(responsible='manager1')])
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(responsible='manager2')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByTags(self):
        self.createIssue(self.tracker, tags=('A', 'B'), assignee=u'member2')
        self.createIssue(self.tracker, tags=('B', 'C'), assignee=u'member2')
        self.createIssue(self.tracker, tags=('A', 'D'), assignee=u'member2')
        issues = sorted([b.getId for b in
                         self.issuefolder.getFilteredIssues(tags='B')])
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(tags=('A', 'D'))]
        issues.sort()
        self.assertEqual(issues, ['1', '3'])
        # Operator is 'or' by default, so this should give the same results.
        issues = [b.getId for b in self.issuefolder.getFilteredIssues(
            tags=dict(query=('A', 'D'), operator='or'))]
        issues.sort()
        self.assertEqual(issues, ['1', '3'])
        # Now try with 'and'
        issues = [b.getId for b in self.issuefolder.getFilteredIssues(
            tags=dict(query=('A', 'D'), operator='and'))]
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByIssueText(self):
        self.createIssue(self.tracker, details="foo", assignee=u'member2')
        issues = sorted([b.getId
                         for b in self.issuefolder.getFilteredIssues(text='foo')])
        self.assertEqual(issues, ['1'])
        issues = [b.getId
                  for b in self.issuefolder.getFilteredIssues(text='bar')]
        self.assertEqual(len(issues), 0)

    def testGetFilteredIssesByResponseText(self):
        self.createIssue(self.tracker, details="foo", assignee=u'member2')
        self.createIssue(self.tracker, assignee=u'member2')
        self.createIssue(self.tracker, assignee=u'member2')

        self.createResponse(self.tracker['2'], text='foo')
        self.createResponse(self.tracker['3'], text='bar')

        issues = sorted(
            [b.getId for b in self.issuefolder.getFilteredIssues(text='foo')]
        )
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId
                  for b in self.issuefolder.getFilteredIssues(text='bar')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesComplex(self):
        self.createIssue(
            self.tracker,
            details="foo",
            area="ui",
            issueType='feature',
            assignee=u'member2',
        )
        self.createIssue(self.tracker, area="ui", issueType="bug", assignee=u'member2')
        self.createIssue(
            self.tracker, area="functionality", details="foo", issueType='bug', assignee=u'member2')

        issues = sorted([b.getId for b in
                         self.issuefolder.getFilteredIssues(text='foo', area='ui')])
        self.assertEqual(issues, ['1'])

        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(area='ui',
                                                     issueType='feature')]
        issues.sort()
        self.assertEqual(issues, ['1'])

        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(area='ui',
                                                     issueType=['feature', 'bug'])]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])

    def testSubjectTolerance(self):
        self.createIssue(self.tracker, details="foo", area="ui",
                         issueType='feature', tags=('A'), assignee=u'member2')
        issues = [
            b.getId for b in
            self.issuefolder.getFilteredIssues(tags=dict(operator='and'))]
        self.assertEqual(issues, ['1'])

        issues = [
            b.getId for b in
            self.issuefolder.getFilteredIssues(Subject=dict(operator='or'))]
        self.assertEqual(issues, ['1'])

        class FakeQuery:
            """Fake query for use in the poi_issue_search_form.

            When filling in the poi_issue_search_form you do not get a
            dict, but an InstanceType, so an old style class.  That
            can give problems, so we fake it here.
            """

            def __init__(self, operator=None, query=None):
                if operator is not None:
                    self.operator = operator
                if query is not None:
                    self.query = query

            def __getitem__(self, key):
                return self.__dict__[key]

        # We repeat the previous two tests but now with FakeOperators
        # instead of dicts.
        tags = FakeQuery(operator='and')
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(tags=tags)]
        self.assertEqual(issues, ['1'])
        tags = FakeQuery(operator='or')
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(tags=tags)]
        self.assertEqual(issues, ['1'])

        # Might as well throw in a few more tests, as we do not yet
        # catch all errors.

        tags = FakeQuery(query=['A'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(tags=tags)]
        self.assertEqual(issues, ['1'])
        tags = FakeQuery(operator='and', query=['A'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(tags=tags)]
        self.assertEqual(issues, ['1'])
        tags = FakeQuery(operator='and', query=['A', 'B'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(tags=tags)]
        self.assertEqual(issues, [])
        tags = FakeQuery(operator='or', query=['A', 'B'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(tags=tags)]
        self.assertEqual(issues, ['1'])


class TestLinkDetection(ptc.PoiTestCase):
    """Test link detection functionality"""

    def afterSetUp(self):
        self.tracker = self.createTracker(self.folder, 'issue-tracker')

    def testLinksInIssues(self):
        """These are more tests for issues really,
        but they also test the tracker indirectly.
        """

        # Create an issue.
        self.createIssue(self.tracker)

        # Link to that existing issue.
        issue = self.createIssue(self.tracker, details="#1")
        linked = self.tracker.linkDetection(issue.details.output)
        self.assertEqual(
            linked,
            u'<p><a href="http://nohost/plone/Members/test_user_1_/issue-tracker/1">#1</a></p>'
        )

        # Issue #3 does not exist.
        new_details = RichTextValue(
            u'#3',
            issue.details.mimeType,
            issue.details.outputMimeType,
        )
        issue.details = new_details
        linked = self.tracker.linkDetection(self.tracker['2'].details.output)
        self.assertEqual(linked, u'<p>#3</p>')

        # Link to an existing issue in the steps
        new_steps = RichTextValue(
            u'#1',
            issue.steps.mimeType,
            issue.steps.outputMimeType,
        )
        issue.steps = new_steps
        linked = self.tracker.linkDetection(self.tracker['2'].steps.output)
        self.assertEqual(
            linked,
            u'<p><a href="http://nohost/plone/Members/test_user_1_/issue-tracker/1">#1</a></p>'
        )

    def testLinksToIssues(self):
        tracker = self.tracker

        # Text without anything special will simply be returned
        # unchanged:
        self.assertEqual(
            tracker.linkDetection("We are the knights who say 'Ni'!"),
            "We are the knights who say 'Ni'!")

        # Unicode should not give problems:
        self.assertEqual(
            tracker.linkDetection(u'\xfanicode'),
            u'\xfanicode')

        # We can ask this tracker to detect issues.  But it does
        # nothing with non existing issues:
        self.assertEqual(tracker.linkDetection("#1"), '#1')

        # Now we add an issue.  The link detection code searches for
        # issues in the portal catalog.  So we add issues there:
        self.createIssue(self.tracker, title="1")
        self.createIssue(self.tracker, title="2")

        # Now we should get html back when we ask for an issue number:
        self.assertEqual(
            tracker.linkDetection("#1"),
            '<a href="http://nohost/plone/Members/test_user_1_/issue-tracker/1">#1</a>')
        self.assertEqual(
            tracker.linkDetection("Links to #1 and #2."),
            'Links to <a href="http://nohost/plone/Members/test_user_1_/issue-tracker/1">#1</a> and <a href="http://nohost/plone/Members/test_user_1_/issue-tracker/2">#2</a>.')

        # We are not fooled by a non existing issue:
        self.assertEqual(
            tracker.linkDetection("Issue #1 and non-issue #3."),
            'Issue <a href="http://nohost/plone/Members/test_user_1_/issue-tracker/1">#1</a> and non-issue #3.')

        # Issues that are added to a different tracker only show up
        # for that tracker:
        tracker2 = self.createTracker(self.folder, 'tracker2')
        self.assertEqual(
            tracker2.linkDetection("#1"),
            '#1')
        self.createIssue(tracker2, title="1")
        self.assertEqual(
            tracker2.linkDetection("#1"),
            '<a href="http://nohost/plone/Members/test_user_1_/tracker2/1">#1</a>')

        # A combination of unicode and a link number should be possible::
        self.assertEqual(
            tracker.linkDetection(u'\xfanicode text with a link to #1'),
            u'\xfanicode text with a link to <a href="http://nohost/plone/Members/test_user_1_/issue-tracker/1">#1</a>')

    def testLinksToRevisions(self):
        tracker = self.tracker

        # We can link to revisions or changesets.  By default nothing
        # happens:

        self.assertEqual(tracker.linkDetection('r42'), 'r42')

        # We need to specify in the tracker where those links should
        # point to.  We could point to something silly:

        tracker.repo_url = 'silly'
        self.assertEqual(
            tracker.linkDetection('r42'),
            '<a href="silly">r42</a>')

        # This is not very useful, as this is not really a link
        # (unless this is a relative link to some content with the id
        # 'silly') and it does nothing with the revision number.  The
        # *real* idea here is to specify a string with "%(rev)s" in
        # it.  At that point the revision number will be filled in.

        # You could point to revisions, for example the collective
        # Trac for Poi:

        tracker.repo_url = "http://dev.plone.org/collective/browser/Poi?%(rev)s"
        self.assertEqual(
            tracker.linkDetection('r42'),
            '<a href="http://dev.plone.org/collective/browser/Poi?42">r42</a>')

        # I myself like to point to the changesets:

        tracker.repo_url = "https://github.com/collective/Products.Poi/commit/%(rev)s"
        self.assertEqual(
            tracker.linkDetection('r42'),
            '<a href="https://github.com/collective/Products.Poi/commit/42">r42</a>')

        # test just a hex number 7 or more characters:
        self.assertEqual(
            tracker.linkDetection('r55bfd6c'),
            '<a href="https://github.com/collective/Products.Poi/commit/55bfd6c">r55bfd6c</a>')
        self.assertEqual(
            tracker.linkDetection('[55bfd6c]'),
            '<a href="https://github.com/collective/Products.Poi/commit/55bfd6c">[55bfd6c]</a>')
        self.assertEqual(
            tracker.linkDetection('changeset:55bfd6c'),
            '<a href="https://github.com/collective/Products.Poi/commit/55bfd6c">changeset:55bfd6c</a>')

        # test a hex number less than 7 characters
        self.assertEqual(tracker.linkDetection('55bfd6'), '55bfd6')

        # Of course it is fine to combine issues and revisions:
        self.createIssue(tracker, title="1")
        self.assertEqual(
            tracker.linkDetection('Issue #1 is fixed in r42.'),
            'Issue <a href="http://nohost/plone/Members/test_user_1_/issue-tracker/1">#1</a> is fixed in <'
            'a href="https://github.com/collective/Products.Poi/commit/42">r42</a>.')

    def testLinkBugs(self):
        ids = [str(i) for i in range(12)]
        text = "issue:1 #2 r3 [4] ticket:5."
        self.assertEqual(
            link_bugs(text, ids),
            '<a href="../1">issue:1</a> <a href="../2">#2</a> r3 '
            '[4] <a href="../5">ticket:5</a>.'
        )
        # no know issues (text should not change)
        self.assertEqual(link_bugs(text, []), text)
        # with a base URL defined
        self.assertEqual(
            link_bugs("#1", ['1'], base_url='http://example.org/issues'),
            '<a href="http://example.org/issues/1">#1</a>'
        )

    def testLinkRepo(self):
        text = "r1 r1e2b5 #22 changeset:333 [4444]"
        repo_url = "someurl?rev=%(rev)s"
        self.assertEqual(
            link_repo(text, repo_url),
            '<a href="someurl?rev=1">r1</a> <a href="someurl?rev=1e2b5">r1e2b5</a> '
            '#22 <a href="someurl?rev=333">changeset:333</a> '
            '<a href="someurl?rev=4444">[4444]</a>'
        )
        self.assertEqual(
            link_repo(text, "here"),
            '<a href="here">r1</a> <a href="here">r1e2b5</a> #22 '
            '<a href="here">changeset:333</a> <a href="here">[4444]</a>'
        )
        text = "r1 r2 norevisionr3 r4nope (r5) r6."
        self.assertEqual(
            link_repo(text, repo_url),
            '<a href="someurl?rev=1">r1</a> <a href="someurl?rev=2">r2</a> '
            'norevisionr3 r4nope (<a href="someurl?rev=5">r5</a>) <a '
            'href="someurl?rev=6">r6</a>.'
        )
        text = "[1] link[2] [3]."
        self.assertEqual(
            link_repo(text, repo_url),
            '<a href="someurl?rev=1">[1]</a> link[2] <a '
            'href="someurl?rev=3">[3]</a>.'
        )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTracker))
    suite.addTest(makeSuite(TestTrackerSearch))
    suite.addTest(makeSuite(TestEmailNotifications))
    suite.addTest(makeSuite(TestLinkDetection))
    return suite
