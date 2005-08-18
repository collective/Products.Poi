from Products.CMFCore.utils import getToolByName
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

    # Add additional workflow mapings
    wftool = getToolByName(self, 'portal_workflow')
    wftool.setChainForPortalTypes(['PoiPscTracker'], 'poi_tracker_workflow')
    wftool.setChainForPortalTypes(['PoiPscIssue'], 'poi_issue_workflow')
    wftool.setChainForPortalTypes(['PoiResponse', 'PoiPscResponse'], '')

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
    addPortalFactoryType(self, out, factory, 'PoiPscResponse')

    # Set parentMetaTypesNotToQuery
    portalProperties = getToolByName(self, 'portal_properties')
    navtreeProps = getattr(portalProperties, 'navtree_properties')
    addToListProperty(self, out, navtreeProps, 'parentMetaTypesNotToQuery', 'PoiTracker')
    addToListProperty(self, out, navtreeProps, 'parentMetaTypesNotToQuery', 'PoiIssue')
    addToListProperty(self, out, navtreeProps, 'parentMetaTypesNotToQuery', 'PoiPscTracker')
    addToListProperty(self, out, navtreeProps, 'parentMetaTypesNotToQuery', 'PoiPscIssue')

    # Give the response types a "save" target to take the use back to the
    # issue itself
    controller = getToolByName(self, 'portal_form_controller')
    addFormControllerAction(self, out, controller, 'validate_integrity',
                            'success', 'PoiResponse', None, 'redirect_to', 'string:../')
    addFormControllerAction(self, out, controller, 'validate_integrity',
                            'success', 'PoiPscResponse', None, 'redirect_to', 'string:../')

    return out.getvalue()