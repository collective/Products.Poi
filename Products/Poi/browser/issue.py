from plone.dexterity.browser.edit import DefaultEditForm


class IssueEdit(DefaultEditForm):

    def __init__(self, context, request):
        """ disable controls in the edit bar
        """
        self.context = context
        self.request = request
        self.request.set('disable_border', 1)
