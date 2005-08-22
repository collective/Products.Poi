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

issue = context.aq_parent
issue.reindexObject(('SearchableText'))

return state

