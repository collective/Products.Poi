# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from Products.Poi.tests.base import TestBase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone import api


class TestFeeds(TestBase):
    """Test RSS feed functionality"""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.workflow = self.portal.portal_workflow
        self.membership = self.portal.portal_membership
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        api.user.create(email="member1@example.com", username="member1")
        api.user.grant_roles(username="member1", roles=["Technician"])

        api.user.create(email="member2@example.com", username="member2")
        api.user.grant_roles(username="member2", roles=["Member"])

        api.user.create(email="member3@example.com", username="member3")
        api.user.grant_roles(username="member3", roles=["Member"])

        api.user.create(email="member4@example.com", username="member4")
        api.user.grant_roles(username="member4", roles=["Member"])

        self.tracker = self.createTracker(
            self.portal, "issue-tracker", assignees=(u"member1", u"member2", "member4")
        )
        self.issues = []

    def addIssue(self, title, responsible=None, transition="accept-unconfirmed"):
        issue = self.createIssue(self.tracker, title, assignee=responsible)
        userId = api.user.get_current().getId()
        login(self.portal, self.tracker.assignees[0])
        self.workflow.doActionFor(issue, transition)
        login(self.portal, userId)
        issue.reindexObject()
        self.issues.append(issue)

    def testGetMyIssues(self):
        # Creator = member4
        login(self.portal, "member4")
        # 1: owned by member4, assigned to member1
        self.addIssue(u"A:member1", u"member1")
        # 2: owned by member4, not assigned to member1
        self.addIssue(u"A:member2", u"member2")

        # Creator = member1
        login(self.portal, "member1")
        # 3: owned by member1, not assigned to anyone
        self.addIssue(u"C:member1")
        # 4: owned by member1, assigned to member4
        self.addIssue(u"A:default", "member4")

        # Creator = member 3 (not in tracker)
        login(self.portal, "member3")
        # 5: owned by member3, not assigned to anyone
        self.addIssue(u"C:member3")

        login(self.portal, "member4")

        # Wrong state
        # 6: owned by and assigned to member4, rejected
        self.addIssue(u"S:rejected", "member4", "reject-unconfirmed")

        issuefolder = self.tracker.restrictedTraverse("@@issuefolder")
        myIssues = issuefolder.getMyIssues(memberId="member4")
        ids = sorted([int(i.getId) for i in myIssues])
        self.assertEqual([4], ids)

        myIssues = issuefolder.getMyIssues(memberId="member1")
        ids = [int(i.getId) for i in myIssues]
        ids.sort()
        self.assertEqual([1], ids)

        myIssues = issuefolder.getMyIssues(openStates=["closed"], memberId="member4")
        self.assertEqual(len(myIssues), 0)

        myIssues = issuefolder.getMyIssues(memberId="member3")
        self.assertEqual(len(myIssues), 0)
        # self.assertEqual(myIssues[0].getId, '5')

        myIssues = issuefolder.getMyIssues(openStates=["rejected"])
        self.assertEqual(len(myIssues), 1)
        self.assertEqual(myIssues[0].getId, "6")

    def testGetMySubmittedIssues(self):
        # Creator = member4
        login(self.portal, "member4")
        # 1: owned by member4, assigned to member1
        self.addIssue(u"A:member1", u"member1")
        # 2: owned by member4, not assigned to member1
        self.addIssue(u"A:member2", u"member2")

        # Creator = member1
        login(self.portal, "member1")
        # 3: owned by member1, not assigned to anyone
        self.addIssue(u"C:member1")
        # 4: owned by member1, assigned to member4
        self.addIssue(u"A:default", "member4")

        # Creator = member 3 (not in tracker)
        login(self.portal, "member3")
        # 5: owned by member3, not assigned to anyone
        self.addIssue(u"C:member3")

        login(self.portal, "member4")

        # Wrong state
        # 6: owned by and assigned to member4, rejected
        self.addIssue(u"S:rejected", "member4", "reject-unconfirmed")

        issuefolder = self.tracker.restrictedTraverse("@@issuefolder")
        myIssues = issuefolder.getMySubmitted(memberId="member4")
        ids = sorted([int(i.getId) for i in myIssues])
        self.assertEqual([1, 2], ids)

        myIssues = issuefolder.getMySubmitted(memberId="member1")
        ids = [int(i.getId) for i in myIssues]
        ids.sort()
        self.assertEqual([3, 4], ids)

        myIssues = issuefolder.getMySubmitted(openStates=["closed"], memberId="member4")
        self.assertEqual(len(myIssues), 0)

        myIssues = issuefolder.getMySubmitted(memberId="member3")
        self.assertEqual(len(myIssues), 1)
        self.assertEqual(myIssues[0].getId, "5")

        myIssues = issuefolder.getMySubmitted(openStates=["rejected"])
        self.assertEqual(len(myIssues), 1)
        self.assertEqual(myIssues[0].getId, "6")

    def testGetOrphanedIssues(self):
        # Creator = member4
        login(self.portal, "member4")
        # 1: owned by member4, assigned to member1
        self.addIssue(u"A:member1", u"member1")
        # 2: owned by member4, not assigned to member1
        self.addIssue(u"A:member2", u"member2")

        # Creator = member1
        login(self.portal, "member1")
        # 3: owned by member1, not assigned to anyone
        self.addIssue(u"C:member1")
        # 4: owned by member1, assigned to member4
        self.addIssue(u"A:default", "member4")

        # Creator = member 3 (not in tracker)
        login(self.portal, "member3")
        # 5: owned by member3, not assigned to anyone
        self.addIssue(u"C:member3")

        login(self.portal, "member4")

        # Wrong state
        # 6: owned by and assigned to member4, rejected
        self.addIssue(u"S:rejected", "member4", "reject-unconfirmed")

        issuefolder = self.tracker.restrictedTraverse("@@issuefolder")
        myIssues = issuefolder.getOrphanedIssues(memberId="member4")
        ids = sorted([int(i.getId) for i in myIssues])
        self.assertEqual([3, 5], ids)

        myIssues = issuefolder.getOrphanedIssues(memberId="member1")
        ids = [int(i.getId) for i in myIssues]
        ids.sort()
        self.assertEqual([3, 5], ids)

        myIssues = issuefolder.getOrphanedIssues(
            openStates=["closed"], memberId="member4"
        )
        self.assertEqual(len(myIssues), 0)

        myIssues = issuefolder.getOrphanedIssues(memberId="member3")
        self.assertEqual(len(myIssues), 0)
