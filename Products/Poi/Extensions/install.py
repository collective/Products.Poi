from plone import api

PROFILE_ID = 'profile-Products.Poi:uninstall'


def uninstall(portal, reinstall=False):
    """Handle some steps that are not done by the default uninstall code.

    When we are reinstalling, some steps must NOT be done, as
    information may get lost then, for example when removing catalog
    indexes or metadata.
    """
    if reinstall:
        return

    qtypes = api.portal.get_registry_record('plone.parent_types_not_to_query')
    if u'Tracker' in qtypes:
        qtypes.remove(u'Tracker')
    if u'Issue' in qtypes:
        qtypes.remove(u'Issue')
    types = api.portal.get_registry_record('plone.displayed_types')
    if 'Tracker' in types:
        type_list = [x for x in types if x != 'Tracker']
        types = tuple(type_list)
        api.portal.set_registry_record('plone.displayed_types', types)

    setup_tool = api.portal.get_tool('portal_setup')
    return setup_tool.runAllImportStepsFromProfile(PROFILE_ID)
