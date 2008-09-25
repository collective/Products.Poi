from Products.CMFCore.utils import getToolByName


def addAction(self, out, atool, id, name, action, condition='',
              permission='View', category='portal_tabs', visible=1,
              icon_category='', icon_expression='', icon_title='',
              icon_priority=0):
    """Generic function to add an action to any action provider.

    If the action (the id,category pair) is there already, it is
    deleted first. If action icon parameters are given, an icon is
    created.
    """
    if len([a for a in atool.listActions()
            if a.getId()==id and a.getCategory()==category]) > 0:
        out.write('Warning: Action "%s" in "%s" in category "%s" already exists\n' % (id, atool.getId(), category))
        removeAction(self, out, atool, id, category, icon_category)
    atool.addAction(id, name, action, condition, permission, category, visible)
    out.write('Added action "%s" to "%s" in category "%s"\n' % (
            id, atool.getId(), category))

    if icon_expression!='':   # also add an icon for the action
        atoolicons = getToolByName(self, 'portal_actionicons')
        try:
            atoolicons.addActionIcon(icon_category, id, icon_expression,
                                     icon_title, icon_priority)
            out.write('Added action icon "%s", category "%s"\n' % (
                    id, icon_category))
        except KeyError:
            out.write('Warning: Action icon "%s", category "%s" already exists, removing it before adding\n' % (id, category))
            atoolicons.removeActionIcon(icon_category, id)
            atoolicons.addActionIcon(icon_category, id, icon_expression,
                                     icon_title, icon_priority)


def removeAction(self, out, atool, id, category, icon_category=''):
    """Generic function to remove an action.

    The action (id, category pair) is removed from any action provider. If
    an icon_category is given the icon is removed as well.
    """
    #We use (id, category) as unique key.
    alist=[(a.getId(), a.getCategory()) for a in atool.listActions()]
    if (id, category) in alist:
        atool.deleteActions(selections=[alist.index((id, category))])
        out.write('Removed action "%s", category "%s" from "%s"\n' % (
                id, category, atool.getId()))
    else:
        out.write('Remove action: Warning: Action "%s", category "%s" in "%s" do not exist\n' % (id, category, atool.getId()))
    if icon_category!='':
        atoolicons = getToolByName(self, 'portal_actionicons')
        # remove icon if it exists:
        try:
            atoolicons.getActionIcon(icon_category, id)
            atoolicons.removeActionIcon(icon_category, id)
            out.write('Removed action icon "%s", category "%s"\n' % (
                    id, icon_category))
        except KeyError:
            out.write('Remove action icon: Warning: icon "%s", category "%s" do not exist\n' % (id, icon_category))
