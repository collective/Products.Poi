from Products.Poi.tests import ptc


class TestInstallation(ptc.PoiTestCase):
    """Ensure product is properly installed"""

    def afterSetUp(self):
        self.skins = self.portal.portal_skins
        self.types = self.portal.portal_types
        self.factory = self.portal.portal_factory
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.properties = self.portal.portal_properties
        self.transforms = self.portal.portal_transforms
        self.form_controller = self.portal.portal_form_controller

        self.poiTypes = {'PoiTracker': 'poi_tracker_workflow',
                         'PoiPscTracker': 'poi_tracker_workflow',
                         'PoiIssue': 'poi_issue_workflow'}

    def testDataGridFieldInstalled(self):
        self.failUnless('DataGridWidget' in self.skins.objectIds())

    def testAddRemoveWidgetInstalled(self):
        self.failUnless('AddRemoveWidget' in self.skins.objectIds())

    def testPoiInstalled(self):
        self.failUnless('Poi' in self.skins.objectIds())
        for t in self.poiTypes.keys():
            self.failUnless(t in self.types.objectIds())

    def testWorkflowsInstalled(self):
        for k, v in self.poiTypes.items():
            self.failUnless(v in self.workflow.objectIds())
            self.failUnless(self.workflow.getChainForPortalType(k) == (v, ))

    def testIntelligentTextInstalled(self):
        self.failUnless('web_intelligent_plain_text_to_html' in
                        self.transforms.objectIds())

    def testPortalFactorySetup(self):
        for t in self.poiTypes.keys():
            self.failUnless(t in self.factory.getFactoryTypes())

    def testCatalogMetadataInstalled(self):
        self.failUnless('UID' in self.catalog.schema())

    def testParentMetaTypesNotToQuery(self):
        p = self.properties.navtree_properties
        for t in ('PoiTracker', 'PoiPscTracker', 'PoiIssue'):
            self.failUnless(t in p.getProperty('parentMetaTypesNotToQuery'))

    def testReinstall(self):
        """Reinstalling should not empty our indexes.
        """
        # First of all, we want a few indexes in the catalog.
        wanted = ("getRelease", "getArea", "getIssueType", "getSeverity",
                  "getTargetRelease", "getResponsibleManager")
        indexes = self.catalog.indexes()
        for idx in wanted:
            self.failUnless(idx in indexes)

        self.addMember('member1', 'Member One', 'member1@example.com',
                       ['Member'], '2005-01-01')
        self.tracker = self.createTracker(self.folder, 'issue-tracker',
                                          managers=('member1', ))

        def results(**kwargs):
            # Small helper function.
            return len(self.catalog.searchResults(**kwargs))

        # self.createIssue fills in some default already.
        # First check that we have no match in the getArea index.
        self.assertEquals(results(getArea='ui'), 0)
        self.issue = self.createIssue(
            self.tracker, 'an-issue', release='0.1',
            targetRelease='1.0', responsibleManager='member1')

        # After adding we should have a match.
        self.assertEquals(results(getArea='ui'), 1)
        # Same for the other indexes.
        self.assertEquals(results(getIssueType='bug'), 1)
        self.assertEquals(results(getSeverity='Medium'), 1)
        self.assertEquals(results(getRelease='0.1'), 1)
        self.assertEquals(results(getTargetRelease='1.0'), 1)
        self.assertEquals(results(getResponsibleManager='member1'), 1)

        # We should also be able to access the metadata of the brain.
        brain = self.catalog.searchResults(getResponsibleManager='member1')[0]
        self.assertEquals(brain.getArea, 'ui')
        self.assertEquals(brain.getIssueType, 'bug')
        self.assertEquals(brain.getSeverity, 'Medium')
        self.assertEquals(brain.getRelease, '0.1')
        self.assertEquals(brain.getTargetRelease, '1.0')
        self.assertEquals(brain.getResponsibleManager, 'member1')

        # Now we reinstall Poi.
        quickinstaller = self.portal.portal_quickinstaller
        quickinstaller.reinstallProducts(['Poi'])

        # Now we should still have a match.
        self.assertEquals(results(getArea='ui'), 1)
        self.assertEquals(results(getIssueType='bug'), 1)
        self.assertEquals(results(getSeverity='Medium'), 1)
        self.assertEquals(results(getRelease='0.1'), 1)
        self.assertEquals(results(getTargetRelease='1.0'), 1)
        self.assertEquals(results(getResponsibleManager='member1'), 1)

        # We should also still be able to access the metadata of the brain.
        brain = self.catalog.searchResults(getResponsibleManager='member1')[0]
        self.assertEquals(brain.getArea, 'ui')
        self.assertEquals(brain.getIssueType, 'bug')
        self.assertEquals(brain.getSeverity, 'Medium')
        self.assertEquals(brain.getRelease, '0.1')
        self.assertEquals(brain.getTargetRelease, '1.0')
        self.assertEquals(brain.getResponsibleManager, 'member1')


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
