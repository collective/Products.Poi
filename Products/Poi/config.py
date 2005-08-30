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

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner', 'Member'))
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
DEPENDENCIES = ['ArchAddOn']
##/code-section config-bottom


# load custom configuration not managed by ArchGenXML
try:
    from Products.Poi.AppConfig import *
except ImportError:
    pass

# End of config.py
