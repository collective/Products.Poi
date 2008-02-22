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
from plone.memoize.view import memoize


def voc2dict(vocab, current=None):
    """Make a dictionary from a vocabulary.

    ('a', "The letter A") -> dict(value='a', label="The letter A")
    """
    options = []
    for value, label in vocab.items():
        checked = (value == current) and "checked" or ""
        options.append(dict(value=value, label=label,
                            checked=checked))
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
        items = folder.sorted_items()
        return items

    @property
    def severity(self):
        return self.context.getSeverity()

    @property
    def targetRelease(self):
        return self.context.getTargetRelease()

    @property
    def responsibleManager(self):
        return self.context.getResponsibleManager()

    @property
    @memoize
    def transitions_for_display(self):
        """Display the available transitions for this issue.
        """
        context = aq_inner(self.context)
        wftool = getToolByName(context, 'portal_workflow')
        transitions = []
        transitions.append(dict(value='', label='No change', checked="checked"))
        for tdef in wftool.getTransitionsFor(context):
            transitions.append(dict(value=tdef['id'], label=tdef['title_or_id'],
                                    checked=''))
        return transitions

    @property
    def available_transitions(self):
        """Get the available transitions for this issue.
        """
        return [x['value'] for x in self.transitions_for_display]

    @property
    def severities_for_display(self):
        """Get the available severities for this issue.
        """
        vocab = self.available_severities
        options = []
        for value in vocab:
            checked = (value == self.severity) and "checked" or ""
            options.append(dict(value=value, label=value,
                                checked=checked))
        return options

    @property
    @memoize
    def available_severities(self):
        """Get the available severities for this issue.
        """
        # get vocab from tracker so use aq_inner
        context = aq_inner(self.context)
        return context.getAvailableSeverities()

    @property
    def releases_for_display(self):
        """Get the releases from the project.

        Usually nothing, unless you use Poi in combination with
        PloneSoftwareCenter.
        """
        vocab = self.available_releases
        return voc2dict(vocab)

    @property
    @memoize
    def available_releases(self):
        """Get the releases from the project.

        Usually nothing, unless you use Poi in combination with
        PloneSoftwareCenter.
        """
        # get vocab from issue
        context = aq_inner(self.context)
        return context.getReleasesVocab()

    @property
    def managers_for_display(self):
        """Get the tracker managers.
        """
        vocab = self.available_managers
        return voc2dict(vocab, self.responsibleManager)

    @property
    @memoize
    def available_managers(self):
        """Get the tracker managers.
        """
        # get vocab from issue
        context = aq_inner(self.context)
        return context.getManagersVocab()


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


class Create(Base):

    def __call__(self):
        update = {}
        form = self.request.form
        context = aq_inner(self.context)
        response_text = form.get('response', u'')
        new_response = Response(response_text)

        transition = form.get('transition', u'')
        if transition and transition in self.available_transitions:
            wftool = getToolByName(context, 'portal_workflow')
            before = wftool.getInfoFor(context, 'review_state')
            wftool.doActionFor(context, transition)
            after = wftool.getInfoFor(context, 'review_state')
            new_response.add_change('review_state', 'Issue state',
                                    before, after)

        options = [
            ('severity', 'Severity'),
            ('targetRelease', 'Target release'),
            ('responsibleManager', 'Responsible manager'),
            ]
        changes = {}
        for option, title in options:
            new = form.get(option, u'')
            if new:
                current = self.__getattribute__(option)
                if current != new:
                    changes[option] = new
                    new_response.add_change(option, title,
                                            current, new)
        context.update(**changes)
            
        folder = IResponseContainer(context)
        folder.add(new_response)
        self.request.response.redirect(context.absolute_url())
