## Python Script "poi_issue_quicksearch"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=searchText
##title=Parse a quicksearch string and jump to the appropriate issue or search result page
##
from Products.PythonScripts.standard import url_quote

tracker = context
response = context.REQUEST.RESPONSE

issueId = searchText
if issueId.startswith('#'):
    issueId = issueId[1:]

if tracker.has_key(issueId):
    response.redirect('%s/%s' % (tracker.absolute_url(), issueId,))
else:
    response.redirect('%s/poi_issue_search?SearchableText=%s' % (tracker.absolute_url(), url_quote(searchText),))
