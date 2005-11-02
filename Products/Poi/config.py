#
# Product configuration. This contents of this module will be imported into
# __init__.py and every content type module.
#
# If you wish to perform custom configuration, you may put a file AppConfig.py
# in your product's root directory. This will be included in this file if
# found.
#
from Products.CMFCore.CMFCorePermissions import setDefaultRoles

PROJECTNAME = "Poi"

# Check for Plone 2.1
try:
    from Products.CMFPlone.migrations import v2_1
except ImportError:
    HAS_PLONE21 = False
else:
    HAS_PLONE21 = True
# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
ADD_CONTENT_PERMISSIONS = {
    'PoiTracker': 'Poi: Add Tracker',
    'PoiIssue': 'Poi: Add Issue',
    'PoiResponse': 'Poi: Add Response',
}

setDefaultRoles('Poi: Add Tracker', ('Manager',))
setDefaultRoles('Poi: Add Issue', ('Anonymous', 'Manager', 'Member', 'Owner',))
setDefaultRoles('Poi: Add Response', ('Anonymous', 'Manager', 'Member', 'Owner',))

product_globals=globals()

##code-section config-bottom #fill in your manual code here
DEPENDENCIES = ['ArchAddOn', 'AddRemoveWidget']
##/code-section config-bottom


# load custom configuration not managed by ArchGenXML
try:
    from Products.Poi.AppConfig import *
except ImportError:
    pass

# End of config.py
# Things you can do in an AppConfig.py:
# STYLESHEETS = [{'id': 'my_global_stylesheet.css'},
#                {'id': 'my_contenttype.css',
#                 'expression': 'python:object.getTypeInfo().getId() == "MyType"}]
# You can do the same with JAVASCRIPTS.
