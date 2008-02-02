## Controller Python Script "poi_response_update_issue"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Update the parent issue when a response is saved
##

from Products.CMFCore.utils import getToolByName

# Ensure only manager can edit/delete the response from now on
portal_workflow = getToolByName(context, 'portal_workflow')
portal_membership = getToolByName(context, 'portal_membership')
if portal_workflow.getInfoFor(context, 'review_state') == 'new':
    # If an anonymous user is posting, Creator will be set to the root zope
    # manager, as this user will become the owner. Give a more sensible
    # default.
    if portal_membership.isAnonymousUser():
        context.setCreators(('(anonymous)',))
    portal_workflow.doActionFor(context, 'post')

return state

