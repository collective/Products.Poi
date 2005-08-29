#
# Skeleton ContextHelpTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Poi.tests import ptc


class TestInstallation(ptc.PoiTestCase):
    """Ensure product is properly installed"""

    def afterSetUp(self):
        self.skins           = self.portal.portal_skins
        self.types           = self.portal.portal_types
        self.factory         = self.portal.portal_factory
        self.catalog         = self.portal.portal_catalog
        self.workflow        = self.portal.portal_workflow
        self.properties      = self.portal.portal_properties
        self.form_controller = self.portal.portal_form_controller

        self.poiTypes = {'PoiTracker'    : 'poi_tracker_workflow',
                         'PoiPscTracker' : 'poi_tracker_workflow',
                         'PoiIssue'      : 'poi_issue_workflow',
                         'PoiResponse'   : 'poi_response_workflow'}

    def testArchAddOnInstalled(self):
        self.failUnless('archaddon' in self.skins.objectIds())

    def testPoiInstalled(self):
        self.failUnless('Poi' in self.skins.objectIds())
        for t in self.poiTypes.keys():
            self.failUnless(t in self.types.objectIds())

    def testWorkflowsInstalled(self):
        for k, v in self.poiTypes.items():
            self.failUnless(v in self.workflow.objectIds())
            self.failUnless(self.workflow.getChainForPortalType(k) == (v,))

    def testPortalFactorySetup(self):
        for t in self.poiTypes.keys():
            self.failUnless(t in self.factory.getFactoryTypes())

    def testCatalogMetadataInstalled(self):
        self.failUnless('UID' in self.catalog.schema())

    def testParentMetaTypesNotToQuery(self):
        for t in ('PoiTracker', 'PoiPscTracker', 'PoiIssue',):
            self.failUnless(t in self.properties.navtree_properties.getProperty('parentMetaTypesNotToQuery'))

    def testTypesNotSearched(self):
        for t in self.poiTypes.keys():
            self.failUnless(t in self.properties.site_properties.getProperty('types_not_searched'))

class TestContentCreation(ptc.PoiTestCase):
    """Ensure content types can be created"""

    def testCreateTracker(self):
        pass

    def testCreateIssue(self):
        pass

    def testCreateResponse(self):
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstallation))
    suite.addTest(makeSuite(TestContentCreation))
    return suite

if __name__ == '__main__':
    framework()
