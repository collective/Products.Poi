import reStructuredText as rst
import textwrap

from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZODB.POSException import ConflictError
from collective.watcherlist.browser import BaseMail
from collective.watcherlist.utils import su
from collective.watcherlist.utils import get_charset
from zope.component.hooks import getSite
from zope.component import getMultiAdapter
from zope.i18n import translate

from Products.Poi import PoiMessageFactory as _
from Products.Poi.adapters import IResponseContainer

wrapper = textwrap.TextWrapper(initial_indent='    ', subsequent_indent='    ')


class BasePoiMail(BaseMail):

    index = ViewPageTemplateFile('templates/poi_mail.pt')
    plain_index = ''
    css_file_name = 'poi-email.css'

    def plain2rst(self):
        """Try to interpret the plain text as reStructuredText.
        """
        charset = get_charset()
        rstText = self.plain
        ignored, warnings = rst.render(
            rstText, input_encoding=charset, output_encoding=charset)
        if len(warnings.messages) == 0:
            body = rst.HTML(
                rstText, input_encoding=charset, output_encoding=charset)
        else:
            # There are warnings, so we keep it simple.
            body = '<pre>%s</pre>' % rstText
        return body

    @property
    def css(self):
        """Render the styling for the html e-mail.
        """
        if not self.css_file_name:
            return u''
        pps = getMultiAdapter((self.context, self.request),
                              name="plone_portal_state")
        portal = pps.portal()
        if not portal:
            return u''
        try:
            # Render the css, in a way that seems to work for both
            # dtml and plain css files.
            css = '%s' % portal.restrictedTraverse(self.css_file_name)
        except (ConflictError, KeyboardInterrupt):
            raise
        except:
            return u''
        return css

    def options(self):
        # Options to pass to the templates.
        return {}

    @property
    def plain(self):
        if not self.plain_index:
            return u''
        output = self.plain_index(**self.options())
        return output

    @property
    def html(self):
        """Render the html version of the e-mail.
        """
        return self.index(**self.options())


class NewIssueMail(BasePoiMail):

    index = ViewPageTemplateFile('templates/poi_email_new_issue_html.pt')
    plain_index = ViewPageTemplateFile(
        'templates/poi_email_new_issue_plain.pt')

    def options(self):
        context = aq_inner(self.context)
        portal = getSite()
        fromName = portal.getProperty('email_from_name', '')
        portal_membership = getToolByName(portal, 'portal_membership')
        issueCreator = context.Creator()
        issueCreatorInfo = portal_membership.getMemberInfo(issueCreator)
        issueAuthor = issueCreator
        if issueCreatorInfo:
            issueAuthor = issueCreatorInfo['fullname'] or issueCreator

        issueText = context.details.output
        paras = issueText.splitlines()
        issueDetails = '\n\n'.join([wrapper.fill(p) for p in paras])
        tracker = context.getTracker()
        mapping = dict(
            issue_title=su(context.title_or_id()),
            tracker_title=su(tracker.title_or_id()),
            issue_author=su(issueAuthor),
            issue_details=su(issueDetails),
            issue_url=su(context.absolute_url()),
            from_name=su(fromName))
        return mapping

    @property
    def subject(self):
        context = aq_inner(self.context)
        tracker = context.getTracker()
        subject = _(
            'poi_email_new_issue_subject_template',
            u"[${tracker_title}] #${issue_id} - New issue: ${issue_title}",
            mapping=dict(
                tracker_title=su(tracker.Title()),
                issue_id=su(context.getId()),
                issue_title=su(context.Title())))
        # Make the subject unicode and translate it too.
        subject = su(subject)
        subject = translate(subject, 'Poi', context=self.request)
        return subject


class NewResponseMail(BasePoiMail):

    index = ViewPageTemplateFile('templates/poi_email_new_response_html.pt')
    plain_index = ViewPageTemplateFile(
        'templates/poi_email_new_response_plain.pt')

    def __init__(self, context, request):
        super(NewResponseMail, self).__init__(context, request)
        # With -1 we take the last response, which is a sensible default.
        self.response_id = int(self.request.get('response_id', -1))

    def options(self):
        context = aq_inner(self.context)
        folder = IResponseContainer(context)
        response = folder[self.response_id]
        tracker = aq_parent(context)

        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()
        portal_membership = getToolByName(portal, 'portal_membership')
        fromName = su(portal.getProperty('email_from_name', ''))

        creator = response.creator
        creatorInfo = portal_membership.getMemberInfo(creator)
        if creatorInfo and creatorInfo['fullname']:
            responseAuthor = creatorInfo['fullname']
        else:
            responseAuthor = creator
        responseAuthor = su(responseAuthor)

        responseText = su(response.text)
        paras = responseText.splitlines()

        # Indent the response details so they are correctly
        # interpreted as a literal block after the double colon behind
        # the 'Response Details' header.  This only really matters
        # when someone interprets this as reStructuredText though.
        responseDetails = u'\n\n'.join([wrapper.fill(p) for p in paras])

        changes = []
        for change in response.changes:
            before = su(change.get('before'))
            after = su(change.get('after'))
            name = su(change.get('name'))
            # Some changes are workflow changes, which can be translated.
            # Note that workflow changes are in the plone domain.
            before = translate(before, 'plone', context=self.request)
            after = translate(after, 'plone', context=self.request)
            name = translate(name, 'Poi', context=self.request)
            changes.append(dict(name=name, before=before, after=after))
        if response.attachment:
            attachment_id = response.attachment.getId()
        else:
            attachment_id = u''

        mapping = dict(
            issue_title=su(context.title_or_id()),
            tracker_title=su(tracker.title_or_id()),
            response_author=responseAuthor,
            response_details=responseDetails,
            issue_url=su(context.absolute_url()),
            changes=changes,
            from_name=fromName,
            attachment_id=attachment_id)
        return mapping

    @property
    def subject(self):
        context = aq_inner(self.context)
        tracker = context.getTracker()
        subject = _(
            'poi_email_new_response_subject_template',
            u"[${tracker_title}] #${issue_id} - Re: ${issue_title}",
            mapping=dict(
                tracker_title=su(tracker.Title()),
                issue_id=su(context.getId()),
                issue_title=su(context.Title())))
        # Ensure that the subject is unicode and translate it too.
        subject = su(subject)
        subject = translate(subject, 'Poi', context=self.request)
        return subject


class ResolvedIssueMail(BasePoiMail):

    index = ViewPageTemplateFile('templates/poi_email_resolved_issue_html.pt')
    plain_index = ViewPageTemplateFile(
        'templates/poi_email_resolved_issue_plain.pt')

    def options(self):
        context = aq_inner(self.context)
        portal = getSite()
        fromName = portal.getProperty('email_from_name', '')
        portal_membership = getToolByName(portal, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        memberInfo = portal_membership.getMemberInfo(member.getUserName())
        stateChanger = member.getUserName()
        if memberInfo:
            stateChanger = memberInfo['fullname'] or stateChanger
        tracker = context.getTracker()
        mapping = dict(
            issue_title=su(context.title_or_id()),
            tracker_title=su(tracker.title_or_id()),
            response_author=su(stateChanger),
            issue_url=su(context.absolute_url()),
            from_name=su(fromName))
        return mapping

    @property
    def subject(self):
        context = aq_inner(self.context)
        tracker = context.getTracker()
        subject = _(
            'poi_email_issue_resolved_subject_template',
            u"[${tracker_title}] Resolved #${issue_id} - ${issue_title}",
            mapping=dict(
                tracker_title=su(tracker.Title()),
                issue_id=su(context.getId()),
                issue_title=su(context.Title())))
        # Make the subject unicode and translate it too.
        subject = su(subject)
        subject = translate(subject, 'Poi', context=self.request)
        return subject
