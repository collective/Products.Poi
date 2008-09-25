from StringIO import StringIO

from Products.CMFCore.utils import getToolByName

from Products.Poi.Extensions.utils import addAction, removeAction


def addPortalFactoryType(self, out, factory, metaType):
    """Add the given type to the list of types used by PortalFactory"""

    types = factory.getFactoryTypes().keys()
    types.append(metaType)
    factory.manage_setPortalFactoryTypes(listOfTypeIds = types)

    print >> out, "Added %s to portal_factory" % (metaType, )


def addToListProperty(self, out, propertySheet, property, value):
    """Add the given value to the list in the given property"""
    current = list(propertySheet.getProperty(property))
    if value not in current:
        current.append(value)
        propertySheet.manage_changeProperties(**{property: current})

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


def addCatalogIndexes(site, out):
    """Add our indexes to the catalog.

    Doing it here instead of in profiles/default/catalog.xml means we
    do not need to reindex those indexes after every reinstall.
    """
    catalog = getToolByName(site, 'portal_catalog')
    indexes = catalog.indexes()
    wanted = ("getRelease", "getArea", "getIssueType", "getSeverity",
              "getTargetRelease", "getResponsibleManager")

    for idx in wanted:
        if idx not in indexes:
            catalog.addIndex(idx, 'FieldIndex')
            print >> out, "Added FieldIndex for %s." % idx


def install(self):

    out = StringIO()

    # Set parentMetaTypesNotToQuery
    portalProperties = getToolByName(self, 'portal_properties')
    navtreeProps = getattr(portalProperties, 'navtree_properties')
    addToListProperty(self, out, navtreeProps, 'parentMetaTypesNotToQuery',
                      'PoiTracker')
    addToListProperty(self, out, navtreeProps, 'parentMetaTypesNotToQuery',
                      'PoiIssue')
    addToListProperty(self, out, navtreeProps, 'parentMetaTypesNotToQuery',
                      'PoiPscTracker')

    # Add PoiPscTracker to allowed types in PSCProject
    typesTool = getToolByName(self, 'portal_types')
    addAllowedContentType(self, out, typesTool, 'PSCProject', 'PoiPscTracker')

    # Control what happens when posting a new issue.
    controller = getToolByName(self, 'portal_form_controller')
    addFormControllerAction(self, out, controller, 'validate_integrity',
                            'success', 'PoiIssue', None, 'traverse_to',
                            'string:poi_issue_post')

    addCatalogIndexes(self, out)

    # Add log action
    ttool = getToolByName(self, 'portal_types')
    removeAction(self, out, ttool, 'log', 'object')
    addAction(self, out, ttool, 'log', 'Log', 'string:$object_url/log',
              'nocall: object/@@log|nothing', 'View', 'object', 1)

    return out.getvalue()


def uninstall(self):
    out = StringIO()

    # Remove log action
    ttool = getToolByName(self, 'portal_types')
    removeAction(self, out, ttool, 'log', 'object')

    return out.getvalue()
