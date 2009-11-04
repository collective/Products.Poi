# -*- coding: utf-8 -*-

from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = "Poi"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
ADD_CONTENT_PERMISSIONS = {
    'PoiTracker': 'Poi: Add Tracker',
    'PoiIssue': 'Poi: Add Issue',
}

setDefaultRoles('Poi: Add Tracker', ('Manager', ))
setDefaultRoles('Poi: Add Issue', ('Anonymous', 'Manager', 'Member', 'Owner'))
setDefaultRoles('Poi: Add Response',
                ('Anonymous', 'Manager', 'Member', 'Owner'))

product_globals = globals()

DESCRIPTION_LENGTH = 200
PSC_TRACKER_ID = 'issues'

# Add text/html to the list of mimetypes to allow HTML/kupu
# issue/response text.
ISSUE_MIME_TYPES = ('text/x-web-intelligent', )
DEFAULT_ISSUE_MIME_TYPE = 'text/x-web-intelligent'
