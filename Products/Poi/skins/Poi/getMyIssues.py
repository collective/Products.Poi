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

isManager = (memberId in context.getManagers())

open = context.getFilteredIssues(state=openStates)
issues = []

for i in open:
    responsible = i.getResponsibleManager
    creator = i.Creator
    
    if creator == memberId or \
        (isManager and (responsible == '(UNASSIGNED)' or responsible == memberId)):
        issues.append(i)

return issues