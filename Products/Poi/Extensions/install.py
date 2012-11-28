from Products.CMFCore.utils import getToolByName

PROFILE_ID = 'profile-Products.Poi:uninstall'


def uninstall(portal, reinstall=False):
    """Handle some steps that are not done by the default uninstall code.

    When we are reinstalling, some steps must NOT be done, as
    information may get lost then, for example when removing catalog
    indexes or metadata.
    """
    if reinstall:
        return
    setup_tool = getToolByName(portal, 'portal_setup')
    return setup_tool.runAllImportStepsFromProfile(PROFILE_ID)
