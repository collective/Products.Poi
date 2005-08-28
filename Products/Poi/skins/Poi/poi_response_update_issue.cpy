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

# Update text
issue = context.aq_parent
issue.reindexObject(('SearchableText'))

# Ensure only manager can edit/delete the response from now on
portal_workflow = getToolByName(context, 'portal_workflow')
portal_workflow.doActionFor(context, 'post')

return state

