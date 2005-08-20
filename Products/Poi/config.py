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

DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner', 'Member'))

product_globals=globals()

##code-section config-bottom #fill in your manual code here
DEPENDENCIES = ['ArchAddOn']
##/code-section config-bottom


try:
    from Products.Poi.AppConfig import *
except ImportError:
    pass

# End of config.py
