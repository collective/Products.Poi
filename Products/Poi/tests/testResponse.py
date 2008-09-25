from Products.Poi.tests import ptc


class TestResponse(ptc.PoiTestCase):
    """Test response functionality"""

    def afterSetUp(self):
        self.addMember('member1', 'Member One', 'member1@member.com',
                       ['Member'], '2005-01-01')
        self.tracker = self.createTracker(self.folder, 'issue-tracker',
                                          managers=('member1', ))
        self.issue = self.createIssue(self.tracker, 'an-issue')
        self.response = self.createResponse(self.issue, 'a-response')
        self.workflow = self.portal.portal_workflow

    def testAccentedCharacters(self):
        encoding = 'iso-8859-1'
        catalog = self.portal.portal_catalog
        issue = self.createIssue(
            self.tracker,
            title=u"été est belle.".encode(encoding),
            details=u"C'est plus belle à Café René.".encode(encoding))
        found = len(catalog.searchResults(
                portal_type = 'PoiIssue',
                SearchableText = u"été".encode(encoding))) >= 1
        self.failUnless(found)
        found = len(catalog.searchResults(
                portal_type = 'PoiIssue',
                SearchableText = u"René".encode(encoding))) >= 1
        self.failUnless(found)

        response = self.createResponse(
            issue, u"In Dutch 'seas' is 'zeeën'".encode(encoding))
        # That should show up in the issue.
        found = len(catalog.searchResults(
                portal_type = 'PoiIssue',
                SearchableText = u"zeeën".encode(encoding))) >= 1
        self.failUnless(found)


class TestKnownIssues(ptc.PoiTestCase):
    """Test bugs with responses"""

    def afterSetUp(self):
        self.addMember('member1', 'Member One', 'member1@member.com',
                       ['Member'], '2005-01-01')
        self.tracker = self.createTracker(self.folder, 'issue-tracker',
                                          managers=('member1', ))
        self.issue = self.createIssue(self.tracker, 'an-issue')
        self.response = self.createResponse(self.issue, 'a-response')
        self.catalog = self.portal.portal_catalog

    def testDeleteResponseLeavesStaleDescription(self):
        found = len(self.catalog.searchResults(
                portal_type = 'PoiIssue', SearchableText = 'a-response')) >= 1
        self.failUnless(found)

        from Products.Poi.adapters import IResponseContainer
        container = IResponseContainer(self.issue)
        container.delete('0')
        self.failIf('a-response' in self.issue.SearchableText())
        found = len(self.catalog.searchResults(
                portal_type = 'PoiIssue', SearchableText = 'a-response')) >= 1
        self.failIf(found, 'OLD ISSUE RAISING ITS HEAD AGAIN: Deleted response causes stale issue SearchableText')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestResponse))
    suite.addTest(makeSuite(TestKnownIssues))
    return suite
