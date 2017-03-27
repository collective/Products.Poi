from plone.dexterity.browser.edit import DefaultEditForm
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import alsoProvides


class IssueEdit(DefaultEditForm):

    def __init__(self, context, request):
        """ disable controls in the edit bar
        """
        self.context = context
        self.request = request
        self.request.set('disable_border', 1)


class IssueView(BrowserView):

    template = ViewPageTemplateFile('templates/poi_issue_view.pt')

    def __call__(self):
        if self.request.method == 'GET':
            alsoProvides(self.request, IDisableCSRFProtection)
        return self.template()
