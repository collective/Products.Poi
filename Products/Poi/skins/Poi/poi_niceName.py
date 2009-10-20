## Python Script "poi_niceName"
##title=
##parameters=username=None,user=None

if not username and not user:
    raise ValueError('Both username and user cannot be empty')

if username:
    from Products.CMFCore.utils import getToolByName
    portal_membership = getToolByName(context, 'portal_membership')
    user = portal_membership.getMemberById(username)
else:
    username = user.getUserName()

niceName = username
if user:
    niceName = user.getProperty('fullname') or username

return niceName
