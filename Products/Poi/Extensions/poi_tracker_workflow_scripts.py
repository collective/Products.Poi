## Workflow scripts
## ['giveManagerLocalrole']

def giveManagerLocalrole(self,state_change,**kw):
    """Give the object's owner the 'Manager' localrole."""
    
    context = state_change.object
    owner = context.Creator()
    context.manage_setLocalRoles(owner, ['Manager'])

