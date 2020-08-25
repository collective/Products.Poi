# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from Products.Poi.tests.base import TestBase
from plone.app.testing import TEST_USER_ID
from plone import api
from Products.Poi.testing import PRODUCTS_POI_INTEGRATION_TESTING

try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestInstallation(TestBase):
    """Ensure product is properly installed"""

    layer = PRODUCTS_POI_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]

        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

        self.types = self.portal.portal_types
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.properties = self.portal.portal_properties
        self.transforms = self.portal.portal_transforms
        self.form_controller = self.portal.portal_form_controller

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.poiTypes = {
            "Tracker": "poi_tracker_workflow",
            "Issue": "poi_issue_workflow",
        }

    def testDataGridFieldInstalled(self):
        self.assertTrue(
            self.installer.isProductInstalled("collective.z3cform.datagridfield")
        )

    def testPoiInstalled(self):
        self.assertTrue(self.installer.isProductInstalled("Products.Poi"))

    def testWorkflowsInstalled(self):
        for k, v in self.poiTypes.items():
            self.failUnless(v in self.workflow.objectIds())
            self.failUnless(self.workflow.getChainForPortalType(k) == (v,))

    def testIntelligentTextInstalled(self):
        self.failUnless(
            "web_intelligent_plain_text_to_html" in self.transforms.objectIds()
        )

    def testCatalogMetadataInstalled(self):
        self.failUnless("UID" in self.catalog.schema())

    def testParentMetaTypesNotToQuery(self):
        qtypes = api.portal.get_registry_record("plone.parent_types_not_to_query")
        for t in self.poiTypes.keys():
            self.assertIn(t, qtypes)

    def testReinstall(self):
        """Reinstalling should not empty our indexes.
        """
        # First of all, we want a few indexes in the catalog.
        wanted = ("release", "area", "issue_type", "severity", "target_release")
        indexes = self.catalog.indexes()
        for idx in wanted:
            self.failUnless(idx in indexes)

        self.addMember(
            "member1", "Member One", "member1@example.com", ["Member"], "2005-01-01"
        )
        self.tracker = self.createTracker(
            self.portal, "issue-tracker", assignees=("member1",)
        )

        def results(**kwargs):
            # Small helper function.
            return len(self.catalog.searchResults(**kwargs))

        # self.createIssue fills in some default already.
        # First check that we have no match in the getArea index.
        self.assertEquals(results(area="ui"), 0)
        self.issue = self.createIssue(
            self.tracker,
            "an-issue",
            release=u"1.0",
            targetRelease=u"2.0",
            assignee=u"member1",
        )

        # After adding we should have a match.
        self.assertEquals(results(area="ui"), 1)
        # Same for the other indexes.
        self.assertEquals(results(issue_type="bug"), 1)
        self.assertEquals(results(severity="Medium"), 1)
        self.assertEquals(results(release=u"1.0"), 1)
        self.assertEquals(results(target_release=u"2.0"), 1)
        self.assertEquals(results(assignee="member1"), 1)

        # We should also be able to access the metadata of the brain.
        brain = self.catalog.searchResults(assignee="member1")[0]
        self.assertEquals(brain.area, "ui")
        self.assertEquals(brain.issue_type, "bug")
        self.assertEquals(brain.severity, "Medium")
        self.assertEquals(brain.release, u"1.0")
        self.assertEquals(brain.target_release, u"2.0")
        self.assertEquals(brain.assignee, "member1")

        # Now we reinstall Poi.
        self.installer.reinstallProducts(["Poi"])

        # Now we should still have a match.
        self.assertEquals(results(area="ui"), 1)
        self.assertEquals(results(issue_type="bug"), 1)
        self.assertEquals(results(severity="Medium"), 1)
        self.assertEquals(results(release=u"1.0"), 1)
        self.assertEquals(results(target_release=u"2.0"), 1)
        self.assertEquals(results(assignee="member1"), 1)

        # We should also still be able to access the metadata of the brain.
        brain = self.catalog.searchResults(assignee="member1")[0]
        self.assertEquals(brain.area, "ui")
        self.assertEquals(brain.issue_type, "bug")
        self.assertEquals(brain.severity, "Medium")
        self.assertEquals(brain.release, u"1.0")
        self.assertEquals(brain.target_release, u"2.0")
        self.assertEquals(brain.assignee, "member1")


class TestContentCreation(TestBase):
    """Ensure content types can be created"""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def testCreateTracker(self):
        self.createTracker(self.portal, "tracker")

    def testCreateIssue(self):
        self.createTracker(self.portal, "tracker")
        self.createIssue(self.portal.tracker)

    def testCreateResponse(self):
        self.createTracker(self.portal, "tracker")
        self.createIssue(self.portal.tracker)
        self.createResponse(self.portal.tracker["1"])
