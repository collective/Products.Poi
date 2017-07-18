from Testing import ZopeTestCase

from Products.Poi.tests import ptc

default_user = unicode(ZopeTestCase.user_name)


class TestFeeds(ptc.PoiTestCase):
    """Test RSS feed functionality"""

    def afterSetUp(self):
        self.workflow = self.portal.portal_workflow
        self.membership = self.portal.portal_membership
        self.addMember(u'member1', u'Member One', u'member1@example.com',
                       ['Technician'], '2005-01-01')
        self.addMember(u'member2', u'Member Two', u'member2@example.com',
                       ['Member'], '2005-01-01')
        self.addMember(u'member3', u'Member Three', u'member3@example.com',
                       ['Member'], '2005-01-01')
        self.tracker = self.createTracker(
            self.folder, 'issue-tracker',
            assignees=(u'member1', u'member2', default_user))
        self.issues = []

    def addIssue(self, title, responsible=None,
                 transition='accept-unconfirmed'):
        issue = self.createIssue(self.tracker, title,
                                 assignee=responsible)
        userId = self.membership.getAuthenticatedMember().getId()
        self.login(self.tracker.assignees[0])
        self.workflow.doActionFor(issue, transition)
        self.login(userId)
        issue.reindexObject()
        self.issues.append(issue)

    def testGetMyIssues(self):
        # Creator = default_user
        # 1: owned by default_user, assigned to member1
        self.addIssue(u'A:member1', u'member1')
        # 2: owned by default_user, not assigned to member1
        self.addIssue(u'A:member2', u'member2')

        # Creator = member1
        self.login('member1')
        # 3: owned by member1, not assigned to anyone
        self.addIssue(u'C:member1')
        # 4: owned by member1, assigned to default_user
        self.addIssue(u'A:default', default_user)

        # Creator = member 3 (not in tracker)
        self.login('member3')
        # 5: owned by member3, not assigned to anyone
        self.addIssue(u'C:member3')

        self.login(default_user)

        # Wrong state
        # 6: owned by and assigned to default_user, rejected
        self.addIssue(u'S:rejected', default_user, 'reject-unconfirmed')

        issuefolder = self.tracker.restrictedTraverse('@@issuefolder')
        myIssues = issuefolder.getMyIssues(memberId=default_user)
        ids = sorted([int(i.getId) for i in myIssues])
        self.assertEqual([4], ids)

        myIssues = issuefolder.getMyIssues(memberId='member1')
        ids = [int(i.getId) for i in myIssues]
        ids.sort()
        self.assertEqual([1], ids)

        myIssues = issuefolder.getMyIssues(openStates=['closed'],
                                           memberId=default_user)
        self.assertEqual(len(myIssues), 0)

        myIssues = issuefolder.getMyIssues(memberId='member3')
        self.assertEqual(len(myIssues), 0)
        # self.assertEqual(myIssues[0].getId, '5')

        myIssues = issuefolder.getMyIssues(openStates=['rejected'])
        self.assertEqual(len(myIssues), 1)
        self.assertEqual(myIssues[0].getId, '6')

    def testGetMySubmittedIssues(self):
        # Creator = default_user
        # 1: owned by default_user, assigned to member1
        self.addIssue(u'A:member1', u'member1')
        # 2: owned by default_user, not assigned to member1
        self.addIssue(u'A:member2', u'member2')

        # Creator = member1
        self.login('member1')
        # 3: owned by member1, not assigned to anyone
        self.addIssue(u'C:member1')
        # 4: owned by member1, assigned to default_user
        self.addIssue(u'A:default', default_user)

        # Creator = member 3 (not in tracker)
        self.login('member3')
        # 5: owned by member3, not assigned to anyone
        self.addIssue(u'C:member3')

        self.login(default_user)

        # Wrong state
        # 6: owned by and assigned to default_user, rejected
        self.addIssue(u'S:rejected', default_user, 'reject-unconfirmed')

        issuefolder = self.tracker.restrictedTraverse('@@issuefolder')
        myIssues = issuefolder.getMySubmitted(memberId=default_user)
        ids = sorted([int(i.getId) for i in myIssues])
        self.assertEqual([1, 2], ids)

        myIssues = issuefolder.getMySubmitted(memberId='member1')
        ids = [int(i.getId) for i in myIssues]
        ids.sort()
        self.assertEqual([3, 4], ids)

        myIssues = issuefolder.getMySubmitted(openStates=['closed'],
                                              memberId=default_user)
        self.assertEqual(len(myIssues), 0)

        myIssues = issuefolder.getMySubmitted(memberId='member3')
        self.assertEqual(len(myIssues), 1)
        self.assertEqual(myIssues[0].getId, '5')

        myIssues = issuefolder.getMySubmitted(openStates=['rejected'])
        self.assertEqual(len(myIssues), 1)
        self.assertEqual(myIssues[0].getId, '6')

    def testGetOrphanedIssues(self):
        # Creator = default_user
        # 1: owned by default_user, assigned to member1
        self.addIssue(u'A:member1', u'member1')
        # 2: owned by default_user, not assigned to member1
        self.addIssue(u'A:member2', u'member2')

        # Creator = member1
        self.login('member1')
        # 3: owned by member1, not assigned to anyone
        self.addIssue(u'C:member1')
        # 4: owned by member1, assigned to default_user
        self.addIssue(u'A:default', default_user)

        # Creator = member 3 (not in tracker)
        self.login('member3')
        # 5: owned by member3, not assigned to anyone
        self.addIssue(u'C:member3')

        self.login(default_user)

        # Wrong state
        # 6: owned by and assigned to default_user, rejected
        self.addIssue(u'S:rejected', default_user, 'reject-unconfirmed')

        issuefolder = self.tracker.restrictedTraverse('@@issuefolder')
        myIssues = issuefolder.getOrphanedIssues(memberId=default_user)
        ids = sorted([int(i.getId) for i in myIssues])
        self.assertEqual([3, 5], ids)

        myIssues = issuefolder.getOrphanedIssues(memberId='member1')
        ids = [int(i.getId) for i in myIssues]
        ids.sort()
        self.assertEqual([3, 5], ids)

        myIssues = issuefolder.getOrphanedIssues(openStates=['closed'],
                                                 memberId=default_user)
        self.assertEqual(len(myIssues), 0)

        myIssues = issuefolder.getOrphanedIssues(memberId='member3')
        self.assertEqual(len(myIssues), 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFeeds))
    return suite
