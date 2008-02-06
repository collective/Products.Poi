from Products.CMFCore.utils import getToolByName
from Products.Poi.browser.interfaces import IResponseAdder
from zope.interface import implements
from zope.viewlet.manager import ViewletManagerBase
from Acquisition import Explicit
from Acquisition import aq_inner
from Products.Archetypes.atapi import DisplayList
from Products.Five.browser import BrowserView
from Products.Poi.adapters import IResponseContainer
from Products.Poi.adapters import Response


def voc2dict(vocab):
    """Make a dictionary from a vocabulary.

    ('a', "The letter A") -> dict(value='a', label="The letter A")
    """
    options = []
    for value, label in vocab.items():
        options.append(dict(value=value, label=label))
    return options


class Base(BrowserView):
    """Base view for PoiIssues.

    Mostly meant as helper for adding a PoiResponse.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def responses(self):
        folder = IResponseContainer(self.context)
        items = folder.items()
        items.sort()
        return items

    def getCurrentIssueSeverity(self):
        return self.context.getSeverity()

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
        # get vocab from tracker so use aq_inner
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
        # get vocab from issue
        context = aq_inner(self.context)
        vocab = context.getReleasesVocab()
        return voc2dict(vocab)

    def getManagersVocab(self):
        """Get the tracker managers.
        """
        # get vocab from issue
        context = aq_inner(self.context)
        vocab = context.getManagersVocab()
        return voc2dict(vocab)


class AddForm(Base):
    implements(IResponseAdder)
    #template = ViewPageTemplateFile('response.pt')

    def __init__(self, context, request, view):
        super(Base, self).__init__(context, request)
        self.__parent__ = view

    def update(self):
        pass

    def render(self):
        # self.template is defined in zcml
        return self.template()


def create_response(context, **kwargs):
    """Create a response.
    """

    idx = 1
    while str(idx) in context.objectIds():
        idx = idx + 1

    """
    response = Response(kwargs.get('response'))
    response.add_change(id="test", name="Test", before="bad", after="good")
    folder = IResponseContainer(context)
    folder.add_response(response)
    """
    context.invokeFactory('PoiResponse', id=str(idx), **kwargs)


class Create(Base):

    def __call__(self):
        update = {}
        form = self.request.form
        response_text = form.get('response', u'')
        new_response = Response(response_text)
        issueTransition = form.get('issueTransition', u'')
        newSeverity = form.get('newSeverity', u'')
        newResponsibleManager = form.get('newResponsibleManager', u'')
        if newSeverity:
            currentIssueSeverity = self.getCurrentIssueSeverity()
            if currentIssueSeverity != newSeverity:
                new_response.add_change('severity', 'Severity',
                                        currentIssueSeverity, newSeverity)
                update['newSeverity'] = newSeverity
            
        context = aq_inner(self.context)
        folder = IResponseContainer(context)
        folder.add(new_response)
        create_response(context, response=response_text,
                        issueTransition=issueTransition,
                        newResponsibleManager=newResponsibleManager,
                        **update)
        self.request.response.redirect(context.absolute_url())
