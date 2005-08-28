from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.fti import DynamicViewTypeInformation
from Products.CMFDynamicViewFTI.migrate import migrateFTIs

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

def addAllowedContentType(self, out, typesTool, metaType, allowedType):
    """Add the given type to the list of allowed content types for the given
    meta type to portal_types. Fails gracefully if metaType does not exist
    """
    fti = getattr(typesTool, metaType, None)
    if fti is None:
        print >> out, "Could not add %s to allowed content types of %s - %s not found" % (allowedType, metaType, metaType)
        return
    allowedTypes = list(fti.allowed_content_types)
    if allowedType not in allowedTypes:
        allowedTypes.append(allowedType)
        fti.allowed_content_types = tuple(allowedTypes)
        print >> out, "Added %s to allowed content types of %s" % (allowedType, metaType)
    else:
        print >> out, "%s is already in allowed content types of %s" % (allowedType, metaType)

def install(self):

    out = StringIO()

    # Migrate FTIs to use CMFDynamicViewFTI
    migrateFTIs(self, 'Poi')

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

    # Set parentMetaTypesNotToQuery
    portalProperties = getToolByName(self, 'portal_properties')
    navtreeProps = getattr(portalProperties, 'navtree_properties')
    addToListProperty(self, out, navtreeProps, 'parentMetaTypesNotToQuery', 'PoiTracker')
    addToListProperty(self, out, navtreeProps, 'parentMetaTypesNotToQuery', 'PoiIssue')
    addToListProperty(self, out, navtreeProps, 'parentMetaTypesNotToQuery', 'PoiPscTracker')

    # Set types_not_searched
    siteProps = getattr(portalProperties, 'site_properties')
    addToListProperty(self, out, siteProps, 'types_not_searched', 'PoiTracker')
    addToListProperty(self, out, siteProps, 'types_not_searched', 'PoiIssue')
    addToListProperty(self, out, siteProps, 'types_not_searched', 'PoiResponse')
    addToListProperty(self, out, siteProps, 'types_not_searched', 'PoiPscTracker')

    # Add PoiPscTracker to allowed types in PSCProject
    typesTool = getToolByName(self, 'portal_types')
    addAllowedContentType(self, out, typesTool, 'PSCProject', 'PoiPscTracker')

    # Give the response types a "save" target to take the use back to the
    # issue itself, after updating the parent issue
    controller = getToolByName(self, 'portal_form_controller')
    addFormControllerAction(self, out, controller, 'validate_integrity',
                            'success', 'PoiResponse', None, 'traverse_to', 'string:poi_response_update_issue')

    return out.getvalue()