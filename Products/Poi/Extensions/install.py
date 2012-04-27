from Products.CMFCore.utils import getToolByName

PROFILE_ID = 'profile-Products.Poi:uninstall'


def uninstall(portal, reinstall=False):
    """Handle some steps that are not done by the default uninstall code.
    """
    setup_tool = getToolByName(portal, 'portal_setup')
    return setup_tool.runAllImportStepsFromProfile(PROFILE_ID)
