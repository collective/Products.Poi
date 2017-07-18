from plone import api
from Products.Poi.tests import ptc


class TestInstallation(ptc.PoiTestCase):
    """Ensure product is properly installed"""

    def afterSetUp(self):
        self.installer = self.portal.portal_quickinstaller
        self.types = self.portal.portal_types
        self.factory = self.portal.portal_factory
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.properties = self.portal.portal_properties
        self.transforms = self.portal.portal_transforms
        self.form_controller = self.portal.portal_form_controller

        self.poiTypes = {'Tracker': 'poi_tracker_workflow',
                         'Issue': 'poi_issue_workflow'}

    def testDataGridFieldInstalled(self):
        self.failUnless(
            'collective.z3cform.datagridfield' in self.installer.objectIds()
        )

    def testPoiInstalled(self):
        self.failUnless('Poi' in self.installer.objectIds())
        for t in self.poiTypes.keys():
            self.failUnless(t in self.types.objectIds())

    def testWorkflowsInstalled(self):
        for k, v in self.poiTypes.items():
            self.failUnless(v in self.workflow.objectIds())
            self.failUnless(self.workflow.getChainForPortalType(k) == (v, ))

    def testIntelligentTextInstalled(self):
        self.failUnless('web_intelligent_plain_text_to_html' in
                        self.transforms.objectIds())

    def testCatalogMetadataInstalled(self):
        self.failUnless('UID' in self.catalog.schema())

    def testParentMetaTypesNotToQuery(self):
        qtypes = api.portal.get_registry_record('plone.parent_types_not_to_query')
        for t in self.poiTypes.keys():
            self.assertIn(t, qtypes)

    def testReinstall(self):
        """Reinstalling should not empty our indexes.
        """
        # First of all, we want a few indexes in the catalog.
        wanted = ("release", "area", "issue_type", "severity",
                  "target_release")
        indexes = self.catalog.indexes()
        for idx in wanted:
            self.failUnless(idx in indexes)

        self.addMember('member1', 'Member One', 'member1@example.com',
                       ['Member'], '2005-01-01')
        self.tracker = self.createTracker(self.folder, 'issue-tracker',
                                          assignees=('member1', ))

        def results(**kwargs):
            # Small helper function.
            return len(self.catalog.searchResults(**kwargs))

        # self.createIssue fills in some default already.
        # First check that we have no match in the getArea index.
        self.assertEquals(results(area='ui'), 0)
        self.issue = self.createIssue(
            self.tracker, 'an-issue', release=u'1.0',
            targetRelease=u'2.0', assignee=u'member1')

        # After adding we should have a match.
        self.assertEquals(results(area='ui'), 1)
        # Same for the other indexes.
        self.assertEquals(results(issue_type='bug'), 1)
        self.assertEquals(results(severity='Medium'), 1)
        self.assertEquals(results(release=u'1.0'), 1)
        self.assertEquals(results(target_release=u'2.0'), 1)
        self.assertEquals(results(assignee='member1'), 1)

        # We should also be able to access the metadata of the brain.
        brain = self.catalog.searchResults(assignee='member1')[0]
        self.assertEquals(brain.area, 'ui')
        self.assertEquals(brain.issue_type, 'bug')
        self.assertEquals(brain.severity, 'Medium')
        self.assertEquals(brain.release, u'1.0')
        self.assertEquals(brain.target_release, u'2.0')
        self.assertEquals(brain.assignee, 'member1')

        # Now we reinstall Poi.
        self.installer.reinstallProducts(['Poi'])

        # Now we should still have a match.
        self.assertEquals(results(area='ui'), 1)
        self.assertEquals(results(issue_type='bug'), 1)
        self.assertEquals(results(severity='Medium'), 1)
        self.assertEquals(results(release=u'1.0'), 1)
        self.assertEquals(results(target_release=u'2.0'), 1)
        self.assertEquals(results(assignee='member1'), 1)

        # We should also still be able to access the metadata of the brain.
        brain = self.catalog.searchResults(assignee='member1')[0]
        self.assertEquals(brain.area, 'ui')
        self.assertEquals(brain.issue_type, 'bug')
        self.assertEquals(brain.severity, 'Medium')
        self.assertEquals(brain.release, u'1.0')
        self.assertEquals(brain.target_release, u'2.0')
        self.assertEquals(brain.assignee, 'member1')


class TestContentCreation(ptc.PoiTestCase):
    """Ensure content types can be created"""

    def testCreateTracker(self):
        self.createTracker(self.folder, 'tracker')

    def testCreateIssue(self):
        self.createTracker(self.folder, 'tracker')
        self.createIssue(self.folder.tracker)

    def testCreateResponse(self):
        self.createTracker(self.folder, 'tracker')
        self.createIssue(self.folder.tracker)
        self.createResponse(self.folder.tracker['1'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstallation))
    suite.addTest(makeSuite(TestContentCreation))
    return suite
