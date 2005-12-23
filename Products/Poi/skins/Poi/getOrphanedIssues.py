## Python Script "getMyIssues"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=openStates=['open', 'in-progress'],memberId=None
##title=Get a catalog query result set of all open issues not assigned to anyone, not owned by the given user
##

from Products.CMFCore.utils import getToolByName

if not memberId:
    mtool = getToolByName(context, 'portal_membership')
    member = mtool.getAuthenticatedMember()
    memberId = member.getId()

open = context.getFilteredIssues(state=openStates)
issues = []

for i in open:
    responsible = i.getResponsibleManager
    creator = i.Creator
    
    if creator != memberId and responsible == '(UNASSIGNED)':
        issues.append(i)

return issues