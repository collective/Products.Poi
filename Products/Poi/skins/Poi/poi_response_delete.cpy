## Controller Python Script "poi_response_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ids
##title=Delete responses to an issue
##

# Borrowed from Plone's folder_delete.cpy

from Products.CMFPlone.utils import transaction_note
titles=[]
titles_and_ids=[]

status='failure'
message='Please select one or more items to delete.'

for id in ids:
    obj=context.restrictedTraverse(id)
    titles.append(obj.title_or_id())
    titles_and_ids.append('%s (%s)' % (obj.title_or_id(), obj.getId()))

if ids:
    status='success'
    message=', '.join(titles)+' has been deleted.'
    transaction_note('Deleted %s from %s' % (', '.join(titles_and_ids), context.absolute_url()))
    context.manage_delObjects(ids)

return state.set(status=status, portal_status_message=message)

