# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from Products.Poi.tests.base import TestBase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import login, logout
from plone import api


class TestIssue(TestBase):
    """Test issue functionality"""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        api.user.create(email="member1@example.com", username="member1")
        api.user.grant_roles(username="member1", roles=["Member"])

        api.user.create(email="member2@example.com", username="member2")
        api.user.grant_roles(username="member2", roles=["Member"])

        api.user.create(email="member3@example.com", username="member3")
        api.user.grant_roles(username="member3", roles=["Member"])

        self.tracker = self.createTracker(
            self.portal, "issue-tracker", assignees=[u"member1", u"member2"]
        )

        self.issue = self.createIssue(self.tracker, assignee=u"member1")

    def testEditIssue(self):
        self.issue.title = "title"
        self.issue.release = "2.0"
        self.issue.area = "functionality"
        self.issue.issue_type = "feature"
        self.issue.severity = "Critical"
        self.issue.target_release = "2.0"
        self.issue.details = self.rich_text(u"details")
        self.issue.steps = self.rich_text(u"step1\nstep2")
        # self.issue.attachment = None
        self.issue.contact_email = "member1@example.com"
        self.issue.watchers = [u"member1", u"member2"]
        self.issue.assignee = u"member2"

        self.assertEqual(self.issue.Title(), "title")
        self.assertEqual(self.issue.release, "2.0")
        self.assertEqual(self.issue.area, "functionality")
        self.assertEqual(self.issue.issue_type, "feature")
        self.assertEqual(self.issue.severity, "Critical")
        self.assertEqual(self.issue.target_release, "2.0")
        self.assertEqual(self.issue.details.output, u"details")
        self.assertEqual(self.issue.steps.output, u"step1\nstep2")
        # self.assertEqual(self.issue.attachment, None)
        self.assertEqual(self.issue.contact_email, "member1@example.com")
        self.assertEqual(self.issue.watchers, [u"member1", u"member2"])
        self.assertEqual(self.issue.assignee, u"member2")

    def testIsValid(self):
        self.failUnless(self.issue.isValid())

    def testRenameAfterCreation(self):
        self.failUnless(self.issue.getId() == "1")
        self.createIssue(self.tracker, assignee=u"member1")
        self.failUnless(len(self.tracker.objectIds()) == 2)
        self.failUnless("1" in self.tracker.objectIds())
        self.failUnless("2" in self.tracker.objectIds())

    def testSearchableText(self):
        catalog = self.portal.portal_catalog
        matches = catalog(SearchableText="Response-text")
        self.failIf(len(matches) >= 1 and matches[0].getObject() == self.issue)
        self.createResponse(self.issue, text="Response-text")
        matches = catalog(SearchableText="Response-text")
        self.failUnless(len(matches) >= 1 and matches[0].getObject() == self.issue)

    def testIsWatching(self):
        self.issue.watchers = []
        self.failIf(self.issue.isWatching())
        self.issue.watchers = ["member3"]
        login(self.portal, "member3")
        self.failUnless(self.issue.isWatching())
        logout()

    def testExplicitDescription(self):
        self.issue.description = "A description"
        self.assertEqual(self.issue.description, "A description")

    def testImplicitDescription(self):
        text = "A short details section with a link http://test.com"
        self.issue.details = self.rich_text(text)
        self.assertEqual(
            self.issue.details.raw,
            "A short details section with a link http://test.com",
        )

    def testReadableDescription(self):
        text = (
            "When pasting html you can get:\r\n    - ugly line breaks,\r\n"
            "- non-breaking spaces.\r\n"
        ) * 20
        self.issue.details = self.rich_text(text)
        self.failUnless(
            self.issue.details.raw.startswith(
                "When pasting html you can get:\r\n    - ugly line breaks"
            )
        )
        self.failIf("&nbsp;" in self.issue.details.raw)
        self.failIf("<br />" in self.issue.details.raw)

    def testUnicodeDescription(self):
        text = (
            u"The Japanese call their country Nippon or in their own "
            u"characters (I think): \xe6\x97\xa5\xe6\x9c\xac"
        )
        self.issue.details = self.rich_text(text)
        self.failUnless(self.issue.details.raw == text)
