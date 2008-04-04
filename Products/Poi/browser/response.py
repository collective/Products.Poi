from Products.CMFCore.utils import getToolByName
from Products.Poi.browser.interfaces import IResponseAdder
from zope.interface import implements
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Poi.adapters import IResponseContainer
from Products.Poi.adapters import Response
from plone.memoize.view import memoize
from Products.Poi.config import DEFAULT_ISSUE_MIME_TYPE
from Products.Poi import PoiMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from zope.lifecycleevent import modified


def voc2dict(vocab, current=None):
    """Make a dictionary from a vocabulary.

    >>> from Products.Archetypes.atapi import DisplayList
    >>> vocab = DisplayList()
    >>> vocab.add('a', "The letter A")
    >>> voc2dict(vocab)
    [{'checked': '', 'value': 'a', 'label': 'The letter A'}]
    >>> vocab.add('b', "The letter B")
    >>> voc2dict(vocab)
    [{'checked': '', 'value': 'a', 'label': 'The letter A'}, {'checked': '', 'value': 'b', 'label': 'The letter B'}]
    >>> voc2dict(vocab, current='c')
    [{'checked': '', 'value': 'a', 'label': 'The letter A'}, {'checked': '', 'value': 'b', 'label': 'The letter B'}]
    >>> voc2dict(vocab, current='b')
    [{'checked': '', 'value': 'a', 'label': 'The letter A'}, {'checked': 'checked', 'value': 'b', 'label': 'The letter B'}]

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
        self.folder = IResponseContainer(context)
        self.mimetype = DEFAULT_ISSUE_MIME_TYPE
        self.use_wysiwyg = (self.mimetype == 'text/html')

    def responses(self):
        context = aq_inner(self.context)
        trans = context.portal_transforms
        items = []
        linkDetection = context.linkDetection
        for id, response in enumerate(self.folder):
            if response.mimetype == 'text/html':
                html = response.text
            else:
                html = trans.convertTo('text/html',
                                       response.text,
                                       mimetype=response.mimetype)
                html = html.getData()
            # Detect links like #1 and r1234
            html = linkDetection(html)
            info = dict(id=id,
                        response=response,
                        html=html)
            items.append(info)
        return items


    @property
    @memoize
    def can_edit_response(self):
        context = aq_inner(self.context)
        memship = getToolByName(context, 'portal_membership')
        return memship.checkPermission('Modify portal content', context)

    @property
    @memoize
    def can_delete_response(self):
        context = aq_inner(self.context)
        memship = getToolByName(context, 'portal_membership')
        return memship.checkPermission('Delete objects', context)

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
        super(AddForm, self).__init__(context, request)
        self.__parent__ = view

    def update(self):
        pass

    def render(self):
        # self.template is defined in zcml
        return self.template()

class Create(Base):

    def determine_response_type(self, response):
        """Return a string indicating the type of response this is.
        """
        responseCreator = response.creator
        if responseCreator == '(anonymous)':
            return 'additional'

        issue = aq_inner(self.context)
        if responseCreator == issue.Creator():
            return 'clarification'

        if responseCreator in self.available_managers:
            return 'reply'

        # default:
        return 'additional'

    def __call__(self):
        update = {}
        form = self.request.form
        context = aq_inner(self.context)
        response_text = form.get('response', u'')
        new_response = Response(response_text)
        new_response.mimetype = self.mimetype
        new_response.type = self.determine_response_type(new_response)

        transition = form.get('transition', u'')
        if transition and transition in self.available_transitions:
            wftool = getToolByName(context, 'portal_workflow')
            before = wftool.getInfoFor(context, 'review_state')
            wftool.doActionFor(context, transition)
            after = wftool.getInfoFor(context, 'review_state')
            new_response.add_change('review_state', 'Issue state',
                                    before, after)

        options = [
            ('severity', 'Severity', 'available_severities'),
            ('targetRelease', 'Target release', 'available_releases'),
            ('responsibleManager', 'Responsible manager', 'available_managers'),
            ]
        changes = {}
        for option, title, vocab in options:
            new = form.get(option, u'')
            if new and new in self.__getattribute__(vocab):
                current = self.__getattribute__(option)
                if current != new:
                    changes[option] = new
                    new_response.add_change(option, title,
                                            current, new)
        if len(response_text) + len(changes) == 0:
            status = IStatusMessage(self.request)
            status.addStatusMessage(
                _(u"No response text added and no issue changes made."),
                type='error')
        else:
            # Apply changes to issue
            context.update(**changes)
            # Add response
            self.folder.add(new_response)
        self.request.response.redirect(context.absolute_url())


class Edit(Base):

    @property
    @memoize
    def response(self):
        form = self.request.form
        context = aq_inner(self.context)
        response_id = form.get('response_id', None)
        if response_id is None:
            return None
        try:
            response_id = int(response_id)
        except ValueError:
            return None
        if response_id >= len(self.folder):
            return None
        return self.folder[response_id]

    @property
    def response_found(self):
        return self.response is not None


class Save(Base):

    def __call__(self):
        form = self.request.form
        context = aq_inner(self.context)
        status = IStatusMessage(self.request)
        if not self.can_edit_response:
            status.addStatusMessage(
                _(u"You are not allowed to edit responses."),
                type='error')
        else:
            response_id = form.get('response_id', None)
            if response_id is None:
                status.addStatusMessage(
                    _(u"No response selected for saving."),
                    type='error')
            else:
                response = self.folder[response_id]
                response_text = form.get('response', u'')
                response.text = response_text
                status.addStatusMessage(
                    _(u"Changes saved to response id ${response_id}.",
                      mapping=dict(response_id=response_id)),
                    type='info')
                # Fire event.  We put the context in the descriptions
                # so event handlers can use this fully acquisition
                # wrapped object to do their thing.  Feels like
                # cheating, but it gets the job done.  Arguably we
                # could turn the two arguments around and signal that
                # the issue has changed, with the response in the
                # event descriptions.
                modified(response, context)
        self.request.response.redirect(context.absolute_url())


class Delete(Base):

    def __call__(self):
        context = aq_inner(self.context)
        status = IStatusMessage(self.request)
        if not self.can_delete_response:
            status.addStatusMessage(
                _(u"You are not allowed to delete responses."),
                type='error')
        else:
            response_id = self.request.form.get('response_id', None)
            if response_id is None:
                status.addStatusMessage(
                    _(u"No response selected for removal."),
                    type='error')
            else:
                try:
                    response_id = int(response_id)
                except ValueError:
                    status.addStatusMessage(
                        _(u"Response id ${response_id} is no integer so it cannot be removed.",
                          mapping=dict(response_id=response_id)),
                        type='error')
                if response_id >= len(self.folder):
                    status.addStatusMessage(
                        _(u"Response id ${response_id} does not exist so it cannot be removed.",
                          mapping=dict(response_id=response_id)),
                        type='error')
                else:
                    self.folder.delete(response_id)
                    status.addStatusMessage(
                        _(u"Removed response id ${response_id}.",
                          mapping=dict(response_id=response_id)),
                        type='info')
        self.request.response.redirect(context.absolute_url())
