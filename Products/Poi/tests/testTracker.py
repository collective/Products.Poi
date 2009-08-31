# -*- coding: utf-8 -*-
from Testing import ZopeTestCase
from Products.Poi.tests import ptc
from Products.CMFCore.utils import getToolByName
from Products.Poi.events import sendResponseNotificationMail

default_user = ZopeTestCase.user_name


class _MockState:
    pass


class TestTracker(ptc.PoiTestCase):
    """Test tracker functionality"""

    def afterSetUp(self):
        self.tracker = self.createTracker(self.folder, 'issue-tracker')
        self.addMember('member1', 'Member One', 'member1@member.com',
                       ['Member'], '2005-01-01')
        self.addMember('member2', 'Member Two', 'member2@member.com',
                       ['Member'], '2005-01-01')

    def testEditTracker(self):
        self.tracker.setTitle('title')
        self.tracker.setDescription('description')
        self.tracker.setHelpText('help text')
        self.tracker.setAvailableAreas(
            ({'id': 'area', 'title': 'Area', 'description': 'Issue area'}, ))
        self.tracker.setAvailableIssueTypes(
            ({'id': 'type', 'title': 'Type', 'description': 'Issue type'}, ))
        self.tracker.setAvailableSeverities(('one', 'two'))
        self.tracker.setDefaultSeverity('two')
        self.tracker.setAvailableReleases(('1.0', '2.0'))
        self.tracker.setManagers(('member1', 'member2'))
        self.tracker.setSendNotificationEmails(False)
        self.tracker.setMailingList('list@list.com')

        self.assertEqual(self.tracker.Title(), 'title')
        self.assertEqual(self.tracker.Description(), 'description')
        self.assertEqual(self.tracker.getHelpText(), '<p>help text</p>')
        self.assertEqual(
            self.tracker.getAvailableAreas(),
            ({'id': 'area', 'title': 'Area', 'description': 'Issue area'}, ))
        self.assertEqual(
            self.tracker.getAvailableIssueTypes(),
            ({'id': 'type', 'title': 'Type', 'description': 'Issue type'}, ))
        self.assertEqual(self.tracker.getAvailableSeverities(), ('one', 'two'))
        self.assertEqual(self.tracker.getDefaultSeverity(), 'two')
        self.assertEqual(self.tracker.getAvailableReleases(), ('1.0', '2.0'))
        self.assertEqual(self.tracker.getManagers(), ('member1', 'member2'))
        self.assertEqual(self.tracker.getSendNotificationEmails(), False)
        self.assertEqual(self.tracker.getMailingList(), 'list@list.com')

    def testDataGridFields(self):
        """
        The DataGridFields should have at least one entry, as they are
        required.  We get problems when adding an Issue if we are not
        careful.  See http://plone.org/products/poi/issues/139

        """
        # When adding/editing through the web we always have a hidden
        # entry:
        hidden_entry = {'description': '',
                        'id': '', 'orderindex_':
                        'template_row_marker', 'title': ''}
        # This is what a real entry looks like:
        real_entry = {'description': 'Something nice.',
                      'id': 'something',
                      'orderindex_': '1',
                      'title': 'Something'},

        # Test the availableAreas field.
        field = self.tracker.getField('availableAreas')
        input = [hidden_entry]
        self.assertEqual(
            field.validate(input, self.tracker),
            'Validation failed(isDataGridFilled): Need at least one entry.')
        input = [real_entry, hidden_entry]
        self.assertEqual(field.validate(input, self.tracker), None)

        # Test the availableIssueTypes field.
        field = self.tracker.getField('availableIssueTypes')
        input = [hidden_entry]
        self.assertEqual(
            field.validate(input, self.tracker),
            'Validation failed(isDataGridFilled): Need at least one entry.')
        input = [real_entry, hidden_entry]
        self.assertEqual(field.validate(input, self.tracker), None)

    def testValidateTrackerManagers(self):
        self.failUnless(self.tracker.validate_managers(('member1', )) is None)
        self.failIf(self.tracker.validate_managers(('memberX', )) is None)
        self.failIf(
            self.tracker.validate_managers(('member1', 'memberX')) is None)

    def testManagersGetLocalRole(self):
        roles = self.tracker.get_local_roles_for_userid
        self.failIf('Manager' in roles('member1'))
        self.tracker.setManagers(('member1', ))
        self.failUnless('Manager' in roles('member1'))
        self.tracker.setManagers(('member2', ))
        self.failIf('Manager' in roles('member1'))
        self.failUnless('Manager' in roles('member2'))
        # Now we mess with local roles and see if setting the tracker
        # managers fixes it.
        self.tracker.manage_delLocalRoles(['member2'])
        self.tracker.setManagers(('member2', ))
        self.failUnless('Manager' in roles('member2'))
        self.tracker.manage_setLocalRoles('member2', ['Owner', 'Manager'])
        self.tracker.manage_setLocalRoles('member1', ['Reviewer'])
        self.tracker.setManagers(('member1', 'member2'))
        self.failUnless('Manager' in roles('member2'))
        self.failUnless('Manager' in roles('member1'))
        self.failUnless('Owner' in roles('member2'))
        self.failUnless('Reviewer' in roles('member1'))
        self.tracker.setManagers(('member2', ))
        self.failUnless('Reviewer' in roles('member1'))

    def testIsUsingReleases(self):
        self.tracker.setAvailableReleases(())
        self.failIf(self.tracker.isUsingReleases())
        self.tracker.setAvailableReleases(('1.0', '2.0'))
        self.failUnless(self.tracker.isUsingReleases())


class TestEmailNotifications(ptc.PoiTestCase):
    """Test getting email addresses and sending email notifications"""

    def afterSetUp(self):
        self.addMember('member1', 'Member One', 'member1@member.com',
                       ['Member'], '2005-01-01')
        self.addMember('member2', 'Member Two', 'member2@member.com',
                       ['Member'], '2005-01-01')
        self.addMember('member3', 'Member Three', 'member3@member.com',
                       ['Member'], '2005-01-01')
        self.tracker = self.createTracker(
            self.folder, 'issue-tracker', managers = ('member1', 'member2'),
            sendNotificationEmails = True)

    def testGetAddressesWithNotificationsOff(self):
        self.tracker.setSendNotificationEmails(False)
        issue = self.createIssue(
            self.tracker, contactEmail='submitter@domain.com',
            watchers=('member2', 'member3'))
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
        issue = self.createIssue(
            self.tracker, contactEmail='submitter@domain.com',
            watchers=('member2', 'member3'))
        addresses = self.tracker.getNotificationEmailAddresses(issue)
        self.failUnless(len(addresses) == 4)
        self.failUnless('member1@member.com' in addresses)
        self.failUnless('member2@member.com' in addresses)
        self.failUnless('member3@member.com' in addresses)
        self.failUnless('submitter@domain.com' in addresses)

    def testGetAddressesOnNewResponseWithList(self):
        self.tracker.setMailingList('list@list.com')
        issue = self.createIssue(
            self.tracker, contactEmail='submitter@domain.com',
            watchers=('member2', 'member3'))
        addresses = self.tracker.getNotificationEmailAddresses(issue)
        self.failUnless(len(addresses) == 4)
        self.failUnless('list@list.com' in addresses)
        self.failUnless('submitter@domain.com' in addresses)
        self.failUnless('member2@member.com' in addresses)
        self.failUnless('member3@member.com' in addresses)

    def testGetTagsInUse(self):
        self.createIssue(self.tracker, tags=('A', 'B'))
        self.createIssue(self.tracker, tags=('B', 'C'))
        self.createIssue(self.tracker, tags=('A', 'D'))
        self.assertEqual(self.tracker.getTagsInUse(), ['A', 'B', 'C', 'D'])


    # The following tests don't map directly to functional methods but are
    # meant to make sure no errors arise from sending emails
    # -- begin email tests

    def testNewIssueEmail(self):
        self.tracker.setSendNotificationEmails(True)
        self.tracker.update(title='Random Tracker')
        issue = self.createIssue(self.tracker,
                                 contactEmail='submitter@domain.com',
                                 watchers=('member1', 'member2'))
        issue.sendNotificationMail()

    def testSpecialCharacterIssueEmail(self):
        self.tracker.setSendNotificationEmails(True)
        self.tracker.update(title='Random Tracker')
        issue = self.createIssue(
            self.tracker,
            title="accented vocals: à è ì",
            contactEmail='submitter@domain.com',
            watchers=('member1', 'member2'))
        issue.sendNotificationMail()
        response = self.createResponse(
            issue, text="more accented vocals: ò ù")
        sendResponseNotificationMail(issue, response)

        # Now try a different charset
        pprop = getToolByName(self.portal, 'portal_properties')
        site_props = getToolByName(pprop, 'site_properties')
        site_props.default_charset = 'iso-8859-1'
        self.portal.email_charset = 'iso-8859-1'
        issue = self.createIssue(
            self.tracker,
            title=u"accented vocals: à è ì ò ù".encode('iso-8859-1'),
            contactEmail='submitter@domain.com',
            watchers=('member1', 'member2'))
        issue.sendNotificationMail()
        response = self.createResponse(
            issue, text=u"more accented vocals: ò ù".encode('iso-8859-1'))
        sendResponseNotificationMail(issue, response)

    def testNewResponseEmail(self):
        self.tracker.setSendNotificationEmails(True)
        self.tracker.update(title='Random Tracker')
        issue = self.createIssue(self.tracker,
                                 contactEmail='submitter@domain.com',
                                 watchers=('member1', 'member2'))
        response = self.createResponse(issue)
        sendResponseNotificationMail(issue, response)

    def testResolvedEmail(self):
        self.tracker.setSendNotificationEmails(True)
        self.tracker.update(title='Random Tracker')

        issue = self.createIssue(self.tracker,
                                 contactEmail='submitter@domain.com',
                                 watchers=('member1', 'member2'))

        from Products.Poi.Extensions import poi_issue_workflow_scripts
        state = _MockState()
        state.object = issue
        poi_issue_workflow_scripts.sendResolvedMail(self.portal, state)

   # -- end email tests


class TestTrackerSearch(ptc.PoiTestCase):
    """Test tracker search functionality"""

    def afterSetUp(self):
        self.tracker = self.createTracker(self.folder, 'issue-tracker')
        self.workflow = self.portal.portal_workflow
        self.issuefolder = self.tracker.restrictedTraverse('@@issuefolder')

    def testGetFilteredIssuesById(self):
        self.createIssue(self.tracker)
        self.createIssue(self.tracker)
        self.createIssue(self.tracker)
        issues = [b.getId for b in self.issuefolder.getFilteredIssues(id='1')]
        self.assertEqual(issues, ['1'])
        issues = [b.getId for b in self.issuefolder.getFilteredIssues(id='2')]
        self.assertEqual(issues, ['2'])

    def testGetFilteredIssesByRelease(self):
        self.createIssue(self.tracker, release='2.0')
        self.createIssue(self.tracker, release='2.0')
        self.createIssue(self.tracker, release='1.0')
        issues = [b.getId
                  for b in self.issuefolder.getFilteredIssues(release='2.0')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId
                  for b in self.issuefolder.getFilteredIssues(release='1.0')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByArea(self):
        self.createIssue(self.tracker, area='ui')
        self.createIssue(self.tracker, area='ui')
        self.createIssue(self.tracker, area='functionality')
        issues = [b.getId
                  for b in self.issuefolder.getFilteredIssues(area='ui')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(area='functionality')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByIssueType(self):
        self.createIssue(self.tracker, issueType='bug')
        self.createIssue(self.tracker, issueType='bug')
        self.createIssue(self.tracker, issueType='feature')
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(issueType='bug')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(issueType='feature')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesBySeverity(self):
        self.createIssue(self.tracker, severity='Medium')
        self.createIssue(self.tracker, severity='Medium')
        self.createIssue(self.tracker, severity='Critical')
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(severity='Medium')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(severity='Critical')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByTargetRelease(self):
        self.createIssue(self.tracker, targetRelease='2.0')
        self.createIssue(self.tracker, targetRelease='2.0')
        self.createIssue(self.tracker, targetRelease='1.0')
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(targetRelease='2.0')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(targetRelease='1.0')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByState(self):
        self.createIssue(self.tracker)
        self.createIssue(self.tracker)
        self.createIssue(self.tracker)
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.tracker['3'], 'accept-unconfirmed')
        self.setRoles(['Member'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(state='unconfirmed')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(state='open')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByCreator(self):
        self.createIssue(self.tracker)
        self.createIssue(self.tracker)
        self.createIssue(self.tracker)
        self.tracker['1'].setCreators(('some_member', ))
        self.tracker['1'].reindexObject()
        self.tracker['2'].setCreators(('some_member', ))
        self.tracker['2'].reindexObject()
        self.tracker['3'].setCreators(('another_member', ))
        self.tracker['3'].reindexObject()

        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(creator='some_member')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(creator='another_member')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByResponsible(self):
        self.createIssue(self.tracker, responsibleManager='manager1')
        self.createIssue(self.tracker, responsibleManager='manager1')
        self.createIssue(self.tracker, responsibleManager='manager2')
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(responsible='manager1')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(responsible='manager2')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesByTags(self):
        self.createIssue(self.tracker, tags=('A', 'B'))
        self.createIssue(self.tracker, tags=('B', 'C'))
        self.createIssue(self.tracker, tags=('A', 'D'))
        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(tags='B')]
        issues.sort()
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
        self.createIssue(self.tracker, details="foo")
        issues = [b.getId
                  for b in self.issuefolder.getFilteredIssues(text='foo')]
        issues.sort()
        self.assertEqual(issues, ['1'])
        issues = [b.getId
                  for b in self.issuefolder.getFilteredIssues(text='bar')]
        self.assertEqual(len(issues), 0)

    def testGetFilteredIssesByResponseText(self):
        self.createIssue(self.tracker, details="foo")
        self.createIssue(self.tracker)
        self.createIssue(self.tracker)

        self.createResponse(self.tracker['2'], text='foo')
        self.createResponse(self.tracker['3'], text='bar')

        issues = [b.getId
                  for b in self.issuefolder.getFilteredIssues(text='foo')]
        issues.sort()
        self.assertEqual(issues, ['1', '2'])
        issues = [b.getId
                  for b in self.issuefolder.getFilteredIssues(text='bar')]
        issues.sort()
        self.assertEqual(issues, ['3'])

    def testGetFilteredIssesComplex(self):
        self.createIssue(
            self.tracker, details="foo", area="ui", issueType='feature')
        self.createIssue(self.tracker, area="ui", issueType="bug")
        self.createIssue(
            self.tracker, area="functionality", details="foo", issueType='bug')

        issues = [b.getId for b in
                  self.issuefolder.getFilteredIssues(text='foo', area='ui')]
        issues.sort()
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
                         issueType='feature', tags=('A'))
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
        self.assertEqual(issue.getTaggedDetails(),
                         '<p><a href="../1">#1</a></p>')

        # Issue #3 does not exist.
        issue.update(details="#3")
        self.assertEqual(self.tracker['2'].getTaggedDetails(),
                         '<p>#3</p>')

        # Link to an existing issue in the steps
        issue.update(steps="#1")
        self.assertEqual(self.tracker['2'].getTaggedSteps(),
                         '<p><a href="../1">#1</a></p>')

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
            '<a href="../1">#1</a>')
        self.assertEqual(
            tracker.linkDetection("Links to #1 and #2."),
            'Links to <a href="../1">#1</a> and <a href="../2">#2</a>.')

        # We are not fooled by a non existing issue:
        self.assertEqual(
            tracker.linkDetection("Issue #1 and non-issue #3."),
            'Issue <a href="../1">#1</a> and non-issue #3.')

        # Issues that are added to a different tracker only show up
        # for that tracker:
        tracker2 = self.createTracker(self.folder, 'tracker2')
        self.assertEqual(
            tracker2.linkDetection("#1"),
            '#1')
        self.createIssue(tracker2, title="1")
        self.assertEqual(
            tracker2.linkDetection("#1"),
            '<a href="../1">#1</a>')

        #A combination of unicode and a link number should be possible::
        self.assertEqual(
            tracker.linkDetection(u'\xfanicode text with a link to #1'),
            u'\xfanicode text with a link to <a href="../1">#1</a>')

    def testLinksToRevisions(self):
        tracker = self.tracker

        # We can link to revisions or changesets.  By default nothing
        # happens:

        self.assertEqual(tracker.linkDetection('r42'), 'r42')

        # We need to specify in the tracker where those links should
        # point to.  We could point to something silly:

        tracker.update(svnUrl="silly")
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

        tracker.update(
            svnUrl="http://dev.plone.org/collective/browser/Poi?%(rev)s")
        self.assertEqual(
            tracker.linkDetection('r42'),
            '<a href="http://dev.plone.org/collective/browser/Poi?42">r42</a>')

        # I myself like to point to the changesets:

        tracker.update(
            svnUrl="http://dev.plone.org/collective/changeset/%(rev)s")
        self.assertEqual(
            tracker.linkDetection('r42'),
            '<a href="http://dev.plone.org/collective/changeset/42">r42</a>')

        # Of course it is fine to combine issues and revisions:
        self.createIssue(tracker, title="1")
        self.assertEqual(
            tracker.linkDetection('Issue #1 is fixed in r42.'),
            'Issue <a href="../1">#1</a> is fixed in <a href="http://dev.plone.org/collective/changeset/42">r42</a>.')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTracker))
    suite.addTest(makeSuite(TestTrackerSearch))
    suite.addTest(makeSuite(TestEmailNotifications))
    suite.addTest(makeSuite(TestLinkDetection))
    return suite
