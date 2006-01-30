## Python Script "getMyIssues"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=openStates=['open', 'in-progress'],memberId=None,manager=False
##title=Get a catalog query result set of all issues assigned to or submitted by the current user
##

from Products.CMFCore.utils import getToolByName

if not memberId:
    mtool = getToolByName(context, 'portal_membership')
    member = mtool.getAuthenticatedMember()
    memberId = member.getId()

if manager:
    if 'unconfirmed' not in openStates:
        openStates += ['unconfirmed']

open = context.getFilteredIssues(state=openStates)
issues = []

for i in open:
    responsible = i.getResponsibleManager
    creator = i.Creator
    
    if creator == memberId or responsible == memberId or (manager and responsible == '(UNASSIGNED)'):
        issues.append(i)

return issues