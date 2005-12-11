## Python Script "getMyIssues"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=openStates=['open', 'in-progress'],memberId=None
##title=Get a catalog query result set of all issues assigned to or submitted by the current user
##

from Products.CMFCore.utils import getToolByName

if not memberId:
    mtool = getToolByName(context, 'portal_membership')
    member = mtool.getAuthenticatedMember()
    memberId = member.getId()

created = context.getFilteredIssues(state=openStates, creator=memberId)
assigned = context.getFilteredIssues(state=openStates, responsible=memberId)

issues = [i for i in created]
existingIssues = {}
for i in issues:
    existingIssues[i.getURL()] = 1

for a in assigned:
    if a.getURL() not in existingIssues:
        issues.append(a)
        existingIssues[a.getURL()] = 1

return issues