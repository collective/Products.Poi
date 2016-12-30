import logging

from AccessControl import Unauthorized
from Acquisition import aq_inner
from plone.namedfile import NamedBlobFile
from plone.namedfile.browser import Download as BlobDownload
from Products.Archetypes.atapi import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from plone.memoize.view import memoize
from zope.cachedescriptors.property import Lazy
from zope.i18n import translate
from zope.interface import implements
from zope.lifecycleevent import modified

from Products.Poi import PoiMessageFactory as _
from Products.Poi import permissions
from Products.Poi.adapters import IResponseContainer
from Products.Poi.adapters import Response
from Products.Poi.browser.interfaces import IResponseAdder
from Products.Poi.config import DEFAULT_ISSUE_MIME_TYPE
from Products.Poi.utils import normalize_filename


logger = logging.getLogger('Poi')


def pretty_size(size):
    if size <= 0:
        return "0 Kb"
    kb = size / 1024
    size = "%d Kb" % kb
    if kb > 999:
        mb = kb / 1024
        size = "%d Mb" % mb
        if mb > 999:
            gb = mb / 1024
            size = "%d Gb" % gb
    return size


def voc2dict(vocab, current=None):
    """Make a dictionary from a vocabulary.

    >>> from Products.Archetypes.atapi import DisplayList
    >>> vocab = DisplayList()
    >>> vocab.add('a', "The letter A")
    >>> voc2dict(vocab)
    [{'checked': '', 'value': 'a', 'label': 'The letter A'}]
    >>> vocab.add('b', "The letter B")
    >>> voc2dict(vocab)
    [{'checked': '', 'value': 'a', 'label': 'The letter A'},
    {'checked': '', 'value': 'b', 'label': 'The letter B'}]
    >>> voc2dict(vocab, current='c')
    [{'checked': '', 'value': 'a', 'label': 'The letter A'},
    {'checked': '', 'value': 'b', 'label': 'The letter B'}]
    >>> voc2dict(vocab, current='b')
    [{'checked': '', 'value': 'a', 'label': 'The letter A'},
    {'checked': 'checked', 'value': 'b', 'label': 'The letter B'}]

    """
    options = []
    for value, label in vocab.items():
        checked = (value == current) and "checked" or ""
        options.append(dict(value=value, label=label,
                            checked=checked))
    return options


class Base(BrowserView):
    """Base view for PoiIssues.

    Mostly meant as helper for adding a response.
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
            if response is None:
                # Has been removed.
                continue
            # Use the already rendered response when available
            if response.rendered_text is None:
                rendering_success = True
                if response.mimetype in ('text/html', 'text/x-html-safe'):
                    html = response.text
                else:
                    html = trans.convertTo('text/html',
                                           response.text,
                                           mimetype=response.mimetype)
                    if html is None:
                        logger.debug("Conversion to text/html failed for "
                                     "response id %s of %s", id,
                                     context.absolute_url())
                        html = u''
                        rendering_success = False
                    else:
                        html = html.getData()
                if rendering_success:
                    # Detect links like #1 and r1234
                    html = linkDetection(html)
                    response.rendered_text = html

            html = response.rendered_text or u''
            info = dict(id=id,
                        response=response,
                        attachment=self.attachment_info(id),
                        html=html)
            items.append(info)
        return items

    @property
    @memoize
    def portal_url(self):
        context = aq_inner(self.context)
        plone = context.restrictedTraverse('@@plone_portal_state')
        return plone.portal_url()

    def attachment_info(self, id):
        """Get icon and other info for attachment

        Taken partly from Archetypes/skins/archetypes/getBestIcon.py
        """
        context = aq_inner(self.context)
        response = self.folder[id]
        attachment = response.attachment
        if attachment is None:
            return None

        from zExceptions import NotFound

        icon = None
        mtr = getToolByName(context, 'mimetypes_registry', None)
        if mtr is None:
            icon = context.getIcon()
        content_type = getattr(
            attachment, 'contentType', 'application/octet-stream')
        size = getattr(attachment, 'get_size', 0)
        if callable(size):
            size = size()
        lookup = mtr.lookup(content_type)
        if lookup:
            mti = lookup[0]
            try:
                context.restrictedTraverse(mti.icon_path)
                icon = mti.icon_path
            except (NotFound, KeyError, AttributeError):
                pass
        if icon is None:
            icon = context.getIcon()
        filename = getattr(attachment, 'filename', '')
        info = dict(
            icon=self.portal_url + '/' + icon,
            url=context.absolute_url() +
            '/@@poi_response_attachment?response_id=' + str(id),
            content_type=content_type,
            size=pretty_size(size),
            filename=filename,
        )
        return info

    @Lazy
    def memship(self):
        context = aq_inner(self.context)
        return getToolByName(context, 'portal_membership')

    @property
    @memoize
    def can_edit_response(self):
        context = aq_inner(self.context)
        return self.memship.checkPermission('Poi: Edit response', context)

    @property
    @memoize
    def can_delete_response(self):
        context = aq_inner(self.context)
        return self.memship.checkPermission('Delete objects', context)

    def validate_response_id(self):
        """Validate the response id from the request.

        Return -1 if for example the response id does not exist.
        Return the response id otherwise.

        Side effect: an informative status message is set.
        """
        status = IStatusMessage(self.request)
        response_id = self.request.form.get('response_id', None)
        if response_id is None:
            msg = _(u"No response selected.")
            msg = translate(msg, 'Poi', context=self.request)
            status.addStatusMessage(msg, type='error')
            return -1
        else:
            try:
                response_id = int(response_id)
            except ValueError:
                msg = _(u"Response id ${response_id} is no integer.",
                        mapping=dict(response_id=response_id))
                msg = translate(msg, 'Poi', context=self.request)
                status.addStatusMessage(msg, type='error')
                return -1
            if response_id >= len(self.folder):
                msg = _(u"Response id ${response_id} does not exist.",
                        mapping=dict(response_id=response_id))
                msg = translate(msg, 'Poi', context=self.request)
                status.addStatusMessage(msg, type='error')
                return -1
            else:
                return response_id
        # fallback
        return -1

    @property
    def severity(self):
        context = aq_inner(self.context)
        return context.getSeverity()

    @property
    def targetRelease(self):
        context = aq_inner(self.context)
        return context.getTargetRelease()

    @property
    def responsibleManager(self):
        context = aq_inner(self.context)
        return context.getResponsibleManager()

    @property
    @memoize
    def transitions_for_display(self):
        """Display the available transitions for this issue.
        """
        context = aq_inner(self.context)
        if not self.memship.checkPermission(permissions.ModifyIssueState,
                                            context):
            return []
        wftool = getToolByName(context, 'portal_workflow')
        transitions = []
        transitions.append(dict(value='', label=PMF(u'No change'),
                                checked="checked"))
        for tdef in wftool.getTransitionsFor(context):
            transitions.append(dict(value=tdef['id'],
                                    label=tdef['title_or_id'], checked=''))
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
        if not self.memship.checkPermission(
                permissions.ModifyIssueSeverity, context):
            return []
        return context.getAvailableSeverities()

    @property
    def releases_for_display(self):
        """Get the releases from the project.

        Usually nothing, unless you use Poi in combination with
        PloneSoftwareCenter.
        """
        vocab = self.available_releases
        current = self.targetRelease
        return voc2dict(vocab, current)

    @property
    @memoize
    def available_releases(self):
        """Get the releases from the project.

        Usually nothing, unless you use Poi in combination with
        PloneSoftwareCenter.
        """
        # get vocab from issue
        context = aq_inner(self.context)
        if not self.memship.checkPermission(
                permissions.ModifyIssueTargetRelease, context):
            return DisplayList()
        return context.getReleasesVocab()

    @property
    def show_target_releases(self):
        """Should the option for selecting a target release be shown?

        There is always at least one option: None.  So only show when
        there is more than one option.
        """
        return len(self.available_releases) > 1

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
        if not self.memship.checkPermission(
                permissions.ModifyIssueAssignment, context):
            return DisplayList()
        return context.getManagersVocab()

    @property
    @memoize
    def upload_allowed(self):
        """Is the user allowed to upload on attachment?
        """
        context = aq_inner(self.context)
        return self.memship.checkPermission(
            permissions.UploadAttachment, context)


class AddForm(Base):
    implements(IResponseAdder)

    def __init__(self, context, request, view):
        super(AddForm, self).__init__(context, request)
        self.__parent__ = view

    def __getitem__(self, name):
        # If we do not add this method, you keep getting a warning at Zope
        # startup: Init Class Products.Five.viewlet.manager.<ViewletManager
        # providing IResponseAdder> has a security declaration for nonexistent
        # method '__getitem__'.
        raise IndexError(
            'This is not meant to be used as viewlet manager. '
            'It is just a contentprovider.')

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
        form = self.request.form
        context = aq_inner(self.context)
        if not self.memship.checkPermission('Poi: Add Response', context):
            raise Unauthorized

        response_text = form.get('response', u'')
        new_response = Response(response_text)
        new_response.mimetype = self.mimetype
        new_response.type = self.determine_response_type(new_response)

        issue_has_changed = False
        transition = form.get('transition', u'')
        if transition and transition in self.available_transitions:
            wftool = getToolByName(context, 'portal_workflow')
            before = wftool.getInfoFor(context, 'review_state')
            before = wftool.getTitleForStateOnType(before, 'PoiIssue')
            wftool.doActionFor(context, transition)
            after = wftool.getInfoFor(context, 'review_state')
            after = wftool.getTitleForStateOnType(after, 'PoiIssue')
            new_response.add_change('review_state', _(u'Issue state'),
                                    before, after)
            issue_has_changed = True

        options = [
            ('severity', _(u'Severity'), 'available_severities'),
            ('responsibleManager', _(u'Responsible manager'),
             'available_managers'),
        ]
        # Changes that need to be applied to the issue (apart from
        # workflow changes that need to be handled separately).
        changes = {}
        for option, title, vocab in options:
            new = form.get(option, u'')
            if new and new in self.__getattribute__(vocab):
                current = self.__getattribute__(option)
                if current != new:
                    changes[option] = new
                    new_response.add_change(option, title,
                                            current, new)
                    issue_has_changed = True

        new = form.get('targetRelease', u'')
        if new and new in self.available_releases:
            current = self.targetRelease
            if current != new:
                # from value (uid) to key (id)
                new_label = self.available_releases.getValue(new)
                current_label = self.available_releases.getValue(current)
                changes['targetRelease'] = new
                new_response.add_change('targetRelease', _(u'Target release'),
                                        current_label, new_label)
                issue_has_changed = True

        attachment = form.get('attachment')
        if attachment:
            # File(id, title, file)
            # data = File(attachment.filename, attachment.filename, attachment)
            data = NamedBlobFile(
                attachment, filename=safe_unicode(attachment.filename))
            new_response.attachment = data
            issue_has_changed = True

        if len(response_text) == 0 and not issue_has_changed:
            status = IStatusMessage(self.request)
            msg = _(u"No response text added and no issue changes made.")
            msg = translate(msg, 'Poi', context=self.request)
            status.addStatusMessage(msg, type='error')
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
            msg = _(u"You are not allowed to edit responses.")
            msg = translate(msg, 'Poi', context=self.request)
            status.addStatusMessage(msg, type='error')
        else:
            response_id = form.get('response_id', None)
            if response_id is None:
                msg = _(u"No response selected for saving.")
                msg = translate(msg, 'Poi', context=self.request)
                status.addStatusMessage(msg, type='error')
            elif self.folder[response_id] is None:
                msg = _(u"Response does not exist anymore; perhaps it was "
                        "removed by another user.")
                msg = translate(msg, 'Poi', context=self.request)
                status.addStatusMessage(msg, type='error')
            else:
                response = self.folder[response_id]
                response_text = form.get('response', u'')
                response.text = response_text
                # Remove cached rendered response.
                response.rendered_text = None
                msg = _(u"Changes saved to response id ${response_id}.",
                        mapping=dict(response_id=response_id))
                msg = translate(msg, 'Poi', context=self.request)
                status.addStatusMessage(msg, type='info')
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
            msg = _(u"You are not allowed to delete responses.")
            msg = translate(msg, 'Poi', context=self.request)
            status.addStatusMessage(msg, type='error')
        else:
            response_id = self.request.form.get('response_id', None)
            if response_id is None:
                msg = _(u"No response selected for removal.")
                msg = translate(msg, 'Poi', context=self.request)
                status.addStatusMessage(msg, type='error')
            else:
                try:
                    response_id = int(response_id)
                except ValueError:
                    msg = _(u"Response id ${response_id} is no integer so it "
                            "cannot be removed.",
                            mapping=dict(response_id=response_id))
                    msg = translate(msg, 'Poi', context=self.request)
                    status.addStatusMessage(msg, type='error')
                    self.request.response.redirect(context.absolute_url())
                    return
                if response_id >= len(self.folder):
                    msg = _(u"Response id ${response_id} does not exist so it "
                            "cannot be removed.",
                            mapping=dict(response_id=response_id))
                    msg = translate(msg, 'Poi', context=self.request)
                    status.addStatusMessage(msg, type='error')
                else:
                    self.folder.delete(response_id)
                    msg = _(u"Removed response id ${response_id}.",
                            mapping=dict(response_id=response_id))
                    msg = translate(msg, 'Poi', context=self.request)
                    status.addStatusMessage(msg, type='info')
        self.request.response.redirect(context.absolute_url())


class Download(Base, BlobDownload):
    """Download the attachment of a response.
    """

    def __call__(self):
        context = aq_inner(self.context)
        request = self.request
        response_id = self.validate_response_id()
        file = None
        if response_id != -1:
            response = self.folder[response_id]
            file = response.attachment
            if file is None:
                status = IStatusMessage(request)
                msg = _(u"Response id ${response_id} has no attachment.",
                        mapping=dict(response_id=response_id))
                msg = translate(msg, 'Poi', context=context)
                status.addStatusMessage(msg, type='error')
        if file is None:
            request.response.redirect(context.absolute_url())

        # From now on we know that an attachment exists.
        # Set attributes on self, so BlobDownload can do its work.
        self.fieldname = 'attachment'
        self.file = file
        filename = getattr(file, 'filename', self.fieldname)
        if filename is not None:
            filename = normalize_filename(filename, request)
        self.filename = filename
        return BlobDownload.__call__(self)

    def _getFile(self):
        return self.file
