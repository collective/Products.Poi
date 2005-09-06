## Python Script "toggleWatchingIssue"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Toggle the current user's watching of this issue
##

context.toggleWatching()
return context.REQUEST.RESPONSE.redirect(context.absolute_url())