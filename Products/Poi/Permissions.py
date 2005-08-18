# Permissions used by Poi

from Products.CMFCore import CMFCorePermissions

View                      = CMFCorePermissions.View
ModifyPortalContent       = CMFCorePermissions.ModifyPortalContent
AccessContentsInformatino = CMFCorePermissions.AccessContentsInformation

AddIssue    = 'Add Poi Issues'
AddResponse = 'Add Poi Responses'

ModifySeverity        = "Poi: Modify issue severity"
ModifyIssueAssignment = "Poi: Modify issue assignment"

CMFCorePermissions.setDefaultRoles(ModifySeverity, ['Manager'])
CMFCorePermissions.setDefaultRoles(ModifyIssueAssignment, ['Manager'])

# Factory bug workaround
CMFCorePermissions.setDefaultRoles(AddIssue, ['Member', 'Manager', 'Owner'])
CMFCorePermissions.setDefaultRoles(AddResponse, ['Manager', 'Owner'])
