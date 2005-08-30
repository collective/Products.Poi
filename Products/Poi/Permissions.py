# Permissions used by Poi

from Products.CMFCore import CMFCorePermissions

View                      = CMFCorePermissions.View
ModifyPortalContent       = CMFCorePermissions.ModifyPortalContent
AccessContentsInformatino = CMFCorePermissions.AccessContentsInformation

ModifySeverity        = "Poi: Modify issue severity"
ModifyIssueAssignment = "Poi: Modify issue assignment"
ModifyIssueState      = "Poi: Modify issue state"

CMFCorePermissions.setDefaultRoles(ModifySeverity, ['Manager'])
CMFCorePermissions.setDefaultRoles(ModifyIssueAssignment, ['Manager'])
CMFCorePermissions.setDefaultRoles(ModifyIssueState, ['Manager'])
