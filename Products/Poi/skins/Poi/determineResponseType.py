## Python Script "determineResponseType"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Return a string indicating the type of response this is
##

responseCreator = context.Creator()
if responseCreator == '(anonymous)':
    return 'additional'

issueCreator = context.aq_parent.Creator()
if responseCreator == issueCreator:
    return 'clarification'

managers = context.getManagers()
if responseCreator in managers:
    return 'reply'

return 'additional'