# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.Poi.adapters import Response
from Products.Poi.adapters import ResponseContainer
from Products.Poi.tests import ptc


class TestResponse(ptc.PoiTestCase):
    """Test response functionality"""

    def afterSetUp(self):
        self.addMember('member1', 'Member One', 'member1@example.com',
                       ['Member'], '2005-01-01')
        self.tracker = self.createTracker(self.folder, 'issue-tracker',
                                          assignees=('member1', ))
        self.issue = self.createIssue(self.tracker, 'an-issue')
        self.response = self.createResponse(self.issue, 'a-response')
        self.workflow = self.portal.portal_workflow
        self.rc = ResponseContainer(self.issue)

    def testAccentedCharacters(self):
        catalog = self.portal.portal_catalog
        issue = self.createIssue(
            self.tracker,
            title="\xc3\xa9t\xc3\xa9 est belle.",
            details="C'est plus belle \xc3\xa0 Caf\xc3\xa9 Ren\xc3\xa9.")
        found = len(catalog.searchResults(
            portal_type='Issue',
            SearchableText="\xc3\xa9t\xc3\xa9")) >= 1
        self.failUnless(found)
        found = len(catalog.searchResults(
            portal_type='Issue',
            SearchableText="Ren\xc3\xa9")) >= 1
        self.failUnless(found)

        self.createResponse(issue, "In Dutch 'seas' is 'zee\xc3\xabn'")
        # That should show up in the issue.
        found = len(catalog.searchResults(
            portal_type='Issue',
            SearchableText="zee\xc3\xabn")) >= 1
        self.failUnless(found)

    def testResponseContainer(self):
        self.failUnless(isinstance(self.rc, ResponseContainer))

    def testResponse(self):
        self.failUnless(isinstance(self.response, Response))
        self.failUnless(isinstance(self.response.date, DateTime))
        self.assertEqual(self.response.creator, 'test_user_1_')
        self.response.add_change(
            "review_state",
            "Transition",
            "unconfirmed",
            "confirmed",
        )
        self.assertEqual(
            self.response.changes,
            [{
                'before': 'unconfirmed',
                'after': 'confirmed',
                'id': 'review_state',
                'name': 'Transition',
            }],
        )

    def testResponseAdded(self):
        self.assertEqual(len(self.rc), 1)
        self.failUnless(self.response in self.rc)

    def testBadResponse(self):
        # calls self.rc.add("Bogus response.")
        self.assertRaises(
            ValueError,
            self.rc.add,
            "Bogus response.",
        )

    def testRemoveResponses(self):
        # add more responses
        for i in range(2, 12):
            self.rc.add(Response("Response %d." % i))
        self.assertEqual(len(self.rc), 11)
        # Responses can be deleted.
        # They're not really removed, but emptied.
        self.rc.delete(7)
        self.assertEqual(len(self.rc), 11)
        self.assertIs(self.rc[7], None)
        # try removing something that doesn't exist
        # calls self.rc.delete(20)
        self.assertRaises(
            IndexError,
            self.rc.delete,
            20
        )


class TestKnownIssues(ptc.PoiTestCase):
    """Test bugs with responses"""

    def afterSetUp(self):
        self.addMember('member1', 'Member One', 'member1@example.com',
                       ['Member'], '2005-01-01')
        self.tracker = self.createTracker(self.folder, 'issue-tracker',
                                          assignees=('member1', ))
        self.issue = self.createIssue(self.tracker, 'an-issue')
        self.response = self.createResponse(self.issue, 'a-response')
        self.catalog = self.portal.portal_catalog

    def testDeleteResponseLeavesStaleDescription(self):
        found = len(self.catalog.searchResults(
            portal_type='Issue', SearchableText='a-response')) >= 1
        self.failUnless(found)

        from Products.Poi.adapters import IResponseContainer
        container = IResponseContainer(self.issue)
        container.delete('0')
        self.failIf('a-response' in self.issue.SearchableText())
        found = len(self.catalog.searchResults(
            portal_type='Issue', SearchableText='a-response')) >= 1
        self.failIf(found, ("OLD ISSUE RAISING ITS HEAD AGAIN: Deleted "
                            "response causes stale issue SearchableText"))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestResponse))
    suite.addTest(makeSuite(TestKnownIssues))
    return suite
