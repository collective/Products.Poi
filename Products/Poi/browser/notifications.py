import reStructuredText as rst
import textwrap

from Acquisition import aq_inner
from plone.app.textfield.interfaces import ITransformer
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
from Products.Poi.interfaces import IIssue
from Products.Poi.interfaces import ITracker

wrapper = textwrap.TextWrapper(initial_indent='    ', subsequent_indent='    ')


class BasePoiMail(BaseMail):

    index = ViewPageTemplateFile('templates/poi_mail.pt')
    plain_index = ''
    css_file_name = '++resource++poi/poi-email.css'

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
            # read in the contents of the CSS file
            css_resource = portal.restrictedTraverse(self.css_file_name)
            css = open(css_resource.context.path).read()
        except (ConflictError, KeyboardInterrupt):
            raise
        except:
            return u''
        return css

    def options(self):
        # Options to pass to the templates.  We used to return an empty
        # dictionary by default, but we might as well return something useful
        # for most cases.
        context = aq_inner(self.context)
        portal = getSite()
        fromName = portal.getProperty('email_from_name', '')
        portal_membership = getToolByName(portal, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        memberInfo = portal_membership.getMemberInfo(member.getUserName())
        stateChanger = member.getUserName()
        if memberInfo:
            stateChanger = memberInfo['fullname'] or stateChanger
        # We expect to be called with an issue as context, but perhaps there
        # are other use cases, like a tracker or a brain or a response.
        # Get hold of the tracker if we can.
        if IIssue.providedBy(context):
            tracker = context.getTracker()
        elif ITracker.providedBy(context):
            tracker = context
        else:
            # This would be strange.
            tracker = None
        if tracker is None:
            tracker_title = ''
        else:
            tracker_title = tracker.title_or_id()
        mapping = dict(
            issue_title=su(context.title_or_id()),
            tracker_title=su(tracker_title),
            response_author=su(stateChanger),
            issue_url=su(context.absolute_url()),
            from_name=su(fromName))
        return mapping

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
        mapping = super(NewIssueMail, self).options()
        context = aq_inner(self.context)
        portal = getSite()
        portal_membership = getToolByName(portal, 'portal_membership')
        issueCreator = context.Creator()
        issueCreatorInfo = portal_membership.getMemberInfo(issueCreator)
        issueAuthor = issueCreator
        if issueCreatorInfo:
            issueAuthor = issueCreatorInfo['fullname'] or issueCreator

        issueText = context.details.output
        paras = issueText.splitlines()
        issueDetails = '\n'.join([wrapper.fill(p) for p in paras])
        transformer = ITransformer(context)
        issuePlainText = transformer(context.details, 'text/plain')
        issuePlainDetails = '\n'.join([wrapper.fill(p) for p in paras])
        paras = issuePlainText.splitlines()
        mapping['issue_author'] = su(issueAuthor)
        mapping['issue_details'] = su(issueDetails)
        mapping['issue_plain_details'] = su(issuePlainDetails)
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
        mapping = super(NewResponseMail, self).options()
        context = aq_inner(self.context)
        folder = IResponseContainer(context)
        response = folder[self.response_id]
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
            attachment_id = getattr(response.attachment, 'filename', u'')
        else:
            attachment_id = u''

        mapping['response_details'] = responseDetails
        mapping['changes'] = changes
        mapping['attachment_id'] = attachment_id
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
