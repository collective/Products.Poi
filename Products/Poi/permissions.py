# Permissions used by Poi

from Products.CMFCore import permissions as CMFCorePermissions

AccessContentsInformation = CMFCorePermissions.AccessContentsInformation
ModifyPortalContent = CMFCorePermissions.ModifyPortalContent
View = CMFCorePermissions.View

EditResponse = "Poi: Edit response"
ManageTracker = "Poi: Manage tracker"
ModifyIssueAssignment = "Poi: Modify issue assignment"
ModifyIssueSeverity = "Poi: Modify issue severity"
ModifyIssueState = "Poi: Modify issue state"
ModifyIssueTags = "Poi: Modify issue tags"
ModifyIssueTargetRelease = "Poi: Modify issue target release"
ModifyIssueWatchers = "Poi: Modify issue watchers"
UploadAttachment = "Poi: Upload attachment"
ModifyRelatedIssues = "Poi: Modify related issues"
