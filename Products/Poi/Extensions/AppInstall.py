from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.fti import DynamicViewTypeInformation
from Products.CMFDynamicViewFTI.migrate import migrateFTI

from StringIO import StringIO


def addCatalogMetadata(self, out, catalog, column):
    """Add the given column to the catalog's metadata schema"""
    if column not in catalog.schema():
        catalog.addColumn(column)
        print >> out, "Added", column, "to catalog metadata"
    else:
        print >> out, column, "already in catalog metadata"

def addPortalFactoryType(self, out, factory, metaType):
    """Add the given type to the list of types used by PortalFactory"""

    types = factory.getFactoryTypes().keys()
    types.append(metaType)
    factory.manage_setPortalFactoryTypes(listOfTypeIds = types)

    print >> out, "Added %s to portal_factory" % (metaType,)

def addToListProperty(self, out, propertySheet, property, value):
    """Add the given value to the list in the given property"""
    current = list(propertySheet.getProperty(property))
    if value not in current:
        current.append(value)
        propertySheet.manage_changeProperties(**{property : current})

    print >> out, "Added %s to %s" % (value, property)

def addFormControllerAction(self, out, controller, template, status, 
                                contentType, button, actionType, action):
    """Add the given action to the portalFormController"""
    controller.addFormAction(template, status, contentType,
                                button, actionType, action)
    print >> out, "Added action %s to %s" % (action, template)

def install(self):

    out = StringIO()

    # Migrate Tracker FTIs to CMFDynamicViewFTI

    migrateFTI(self, 'PoiTracker', 'Poi: PoiTracker (PoiTracker)', DynamicViewTypeInformation.meta_type)
    migrateFTI(self, 'PoiPscTracker', 'Poi: PoiPscTracker (PoiPscTracker)', DynamicViewTypeInformation.meta_type)

    # Add additional workflow mapings
    wftool = getToolByName(self, 'portal_workflow')
    wftool.setChainForPortalTypes(['PoiPscTracker'], 'poi_tracker_workflow')
    wftool.setChainForPortalTypes(['PoiPscIssue'], 'poi_issue_workflow')

    print >> out, "Set additional workflows for types"

    # Add UID to catalog metadata
    catalog = getToolByName(self, 'portal_catalog')
    addCatalogMetadata(self, out, catalog, 'UID')

    print >> out, "Added UID to catalog metadata"

    # Add to portal_factory
    factory = getToolByName(self, 'portal_factory')
    addPortalFactoryType(self, out, factory, 'PoiTracker')
    addPortalFactoryType(self, out, factory, 'PoiIssue')
    addPortalFactoryType(self, out, factory, 'PoiResponse')

    addPortalFactoryType(self, out, factory, 'PoiPscTracker')
    addPortalFactoryType(self, out, factory, 'PoiPscIssue')

    # Set parentMetaTypesNotToQuery
    portalProperties = getToolByName(self, 'portal_properties')
    navtreeProps = getattr(portalProperties, 'navtree_properties')
    addToListProperty(self, out, navtreeProps, 'parentMetaTypesNotToQuery', 'PoiTracker')
    addToListProperty(self, out, navtreeProps, 'parentMetaTypesNotToQuery', 'PoiIssue')
    addToListProperty(self, out, navtreeProps, 'parentMetaTypesNotToQuery', 'PoiPscTracker')
    addToListProperty(self, out, navtreeProps, 'parentMetaTypesNotToQuery', 'PoiPscIssue')

    # Set types_not_searched
    siteProps = getattr(portalProperties, 'site_properties')
    addToListProperty(self, out, siteProps, 'types_not_searched', 'PoiTracker')
    addToListProperty(self, out, siteProps, 'types_not_searched', 'PoiIssue')
    addToListProperty(self, out, siteProps, 'types_not_searched', 'PoiResponse')
    addToListProperty(self, out, siteProps, 'types_not_searched', 'PoiPscTracker')
    addToListProperty(self, out, siteProps, 'types_not_searched', 'PoiPscIssue')

    # Give the response types a "save" target to take the use back to the
    # issue itself, after updating the parent issue
    controller = getToolByName(self, 'portal_form_controller')
    addFormControllerAction(self, out, controller, 'validate_integrity',
                            'success', 'PoiResponse', None, 'traverse_to', 'string:poi_response_update_issue')

    return out.getvalue()