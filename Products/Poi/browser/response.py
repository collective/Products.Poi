from Products.CMFCore.utils import getToolByName
from Products.Poi.browser.interfaces import IResponseAdder
from zope.interface import implements
from zope.viewlet.manager import ViewletManagerBase
from Acquisition import Explicit
from Acquisition import aq_inner
from Products.Archetypes.atapi import DisplayList
from Products.Five.browser import BrowserView


class AddForm(Explicit):
    implements(IResponseAdder)
    #template = ViewPageTemplateFile('response.pt')

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.__parent__ = view

    def update(self):
        pass

    def render(self):
        # self.template is defined in zcml
        return self.template()

    def getAvailableIssueTransitions(self):
        """Get the available transitions for this issue.
        """
        context = aq_inner(self.context)
        wftool = getToolByName(context, 'portal_workflow')
        transitions = []
        transitions.append(dict(value='', label='No change'))
        for tdef in wftool.getTransitionsFor(context):
            transitions.append(dict(value=tdef['id'], label=tdef['title_or_id']))
        return transitions

    def getAvailableSeverities(self):
        """Get the available severities for this issue.
        """
        context = aq_inner(self.context)
        vocab = context.getAvailableSeverities()
        options = []
        for value in vocab:
            options.append(dict(value=value, label=value))
        return options

    def getReleasesVocab(self):
        """Get the releases from the project.

        Usually nothing, unless you use Poi in combination with
        PloneSoftwareCenter.
        """
        context = aq_inner(self.context)
        vocab = context.getReleasesVocab()
        options = []
        for value, label in vocab.items():
            options.append(dict(value=value, label=label))
        return options

    def getManagersVocab(self):
        """Get the tracker managers.
        """
        context = aq_inner(self.context)
        vocab = context.getManagersVocab()
        options = []
        for value, label in vocab.items():
            options.append(dict(value=value, label=label))
        return options


def create_response(context, **kwargs):
    """Create a response.
    """

    idx = 1
    while str(idx) in context.objectIds():
        idx = idx + 1
    context.invokeFactory('PoiResponse', id=str(idx), **kwargs)


class Create(BrowserView):
    def __call__(self):
        form = self.request.form
        response = form.get('response', '')
        issueTransition = form.get('issueTransition', '')
        newSeverity = form.get('newSeverity', '')
        newResponsibleManager = form.get('newResponsibleManager', '')
        context = aq_inner(self.context)
        create_response(context, response=response,
                        issueTransition=issueTransition,
                        newSeverity=newSeverity,
                        newResponsibleManager=newResponsibleManager)
        self.request.response.redirect(context.absolute_url())


