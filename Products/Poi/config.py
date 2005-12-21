"""config.py, product configuration.

The contents of this module will be imported into __init__.py, the
workflow configuration and every content type module.

If you wish to perform custom configuration, you may put a file
AppConfig.py in your product's root directory. This will be included
in this file if found.
"""

# Copyright (c) 2005 by Copyright (c) 2004 Martin Aspeli
#
# Generator: ArchGenXML Version 1.4.1 svn/devel
#            http://plone.org/products/archgenxml

from Products.CMFCore.CMFCorePermissions import setDefaultRoles
##code-section config-head #fill in your manual code here
##/code-section config-head


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

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

# You can overwrite these two in an AppConfig.py:
# STYLESHEETS = [{'id': 'my_global_stylesheet.css'},
#                {'id': 'my_contenttype.css',
#                 'expression': 'python:object.getTypeInfo().getId() == "MyType"}]
# You can do the same with JAVASCRIPTS.
STYLESHEETS = []
JAVASCRIPTS = []

##code-section config-bottom #fill in your manual code here
DEPENDENCIES = ['DataGridField', 'AddRemoveWidget']
##/code-section config-bottom


# load custom configuration not managed by ArchGenXML
try:
    from Products.Poi.AppConfig import *
except ImportError:
    pass

# End of config.py
