import reStructuredText as rst
import textwrap

from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.watcherlist.browser import BaseMail
from collective.watcherlist.utils import su
from collective.watcherlist.utils import get_charset
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter
from zope.i18n import translate

from Products.Poi import PoiMessageFactory as _
from Products.Poi.adapters import IResponseContainer

wrapper = textwrap.TextWrapper(initial_indent='    ', subsequent_indent='    ')


class BasePoiMail(BaseMail):

    index = ViewPageTemplateFile('poi_mail.pt')

    @property
    def html(self):
        """Render the html version by interpreting the plain text as RST.

        So we parse it as reStructuredText.
        """
        rstText = self.plain
        pps = getMultiAdapter((self.context, self.request),
                              name="plone_portal_state")
        lang = pps.language()
        charset = get_charset()
        ignored, warnings = rst.render(
            rstText, input_encoding=charset, output_encoding=charset)
        if len(warnings.messages) == 0:
            body = rst.HTML(
                rstText, input_encoding=charset, output_encoding=charset)
        else:
            # There are warnings, so we keep it simple.
            body = '<pre>%s</pre>' % rstText

        # Try to get some styling.
        css = u''
        portal = getSite()
        if portal is not None:
            try:
                # Render the css, in a way that seems to work for both
                # dtml and plain css files.
                css = '%s' % portal.restrictedTraverse('poi-email.css')
            except:
                pass

        # Pass some options to the template and render it.
        options = dict(
            lang=lang,
            charset=charset,
            body=body,
            css=css,
            )
        return self.index(**options)


class NewIssueMail(BasePoiMail):

    @property
    def plain(self):
        context = aq_inner(self.context)
        portal = getSite()
        fromName = portal.getProperty('email_from_name', '')
        portal_membership = getToolByName(portal, 'portal_membership')
        issueCreator = context.Creator()
        issueCreatorInfo = portal_membership.getMemberInfo(issueCreator)
        issueAuthor = issueCreator
        if issueCreatorInfo:
            issueAuthor = issueCreatorInfo['fullname'] or issueCreator

        issueText = context.getDetails(mimetype="text/x-web-intelligent")
        paras = issueText.splitlines()
        issueDetails = '\n\n'.join([wrapper.fill(p) for p in paras])
        tracker = context.getTracker()

        mail_text = _(
            'poi_email_new_issue_template',
            u"""A new issue has been submitted to the **${tracker_title}**
tracker by **${issue_author}** and awaits confirmation.

Issue Information
-----------------

Issue
  ${issue_title} (${issue_url})


**Issue Details**::

${issue_details}


* This is an automated email, please do not reply - ${from_name}""",
            mapping=dict(
                issue_title=su(context.title_or_id()),
                tracker_title=su(tracker.title_or_id()),
                issue_author=su(issueAuthor),
                issue_details=su(issueDetails),
                issue_url=su(context.absolute_url()),
                from_name=su(fromName)))
        # Translate the body text
        mail_text = translate(mail_text, 'Poi', context=self.request)
        return mail_text

    @property
    def subject(self):
        context = aq_inner(self.context)
        tracker = context.getTracker()
        subject = _(
            'poi_email_new_issue_subject_template',
            u"[${tracker_title}] #${issue_id} - New issue: ${issue_title}",
            mapping=dict(
                tracker_title=su(tracker.getExternalTitle()),
                issue_id=su(context.getId()),
                issue_title=su(context.Title())))
        # Make the subject unicode and translate it too.
        subject = su(subject)
        subject = translate(subject, 'Poi', context=self.request)
        return subject


class NewResponseMail(BasePoiMail):

    def __init__(self, context, request):
        super(NewResponseMail, self).__init__(context, request)
        # With -1 we take the last response, which is a sensible default.
        self.response_id = int(self.request.get('response_id', -1))

    @property
    def plain(self):
        """When a response is created, send a notification email to all
        tracker managers, unless emailing is turned off.
        """
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

        # Indent the response details so they are correctly interpreted as
        # a literal block after the double colon behind the 'Response
        # Details' header.
        wrapper = textwrap.TextWrapper(initial_indent=u'    ',
                                       subsequent_indent=u'    ')
        responseDetails = u'\n\n'.join([wrapper.fill(p) for p in paras])

        if responseDetails:
            header = _(
                'poi_heading_response_details',
                u"Response Details")
            header = translate(header, 'Poi', context=self.request)
            responseDetails = u"**%s**::\n\n\n%s" % (header, responseDetails)

        changes = u''
        for change in response.changes:
            before = su(change.get('before'))
            after = su(change.get('after'))
            name = su(change.get('name'))
            # Some changes are workflow changes, which can be translated.
            # Note that workflow changes are in the plone domain.
            before = translate(before, 'plone', context=self.request)
            after = translate(after, 'plone', context=self.request)
            name = translate(name, 'Poi', context=self.request)
            changes += u"- %s: %s -> %s\n" % (name, before, after)
        if response.attachment:
            extra = _(
                'poi_attachment_added',
                u"An attachment has been added with id ${attachment_id}",
                mapping=dict(
                    attachment_id=response.attachment.getId()))
            extra = translate(extra, 'Poi', context=self.request)
            changes += extra + "\n"

        mail_text = _(
            'poi_email_new_response_template',
            u"""A new response has been given to the issue **${issue_title}**
in the tracker **${tracker_title}** by **${response_author}**.

Response Information
--------------------

Issue
  ${issue_title} (${issue_url})

${changes}

${response_details}

* This is an automated email, please do not reply - ${from_name}""",
            mapping=dict(
                issue_title=su(context.title_or_id()),
                tracker_title=su(tracker.title_or_id()),
                response_author=responseAuthor,
                response_details=responseDetails,
                issue_url=su(context.absolute_url()),
                changes=changes,
                from_name=fromName))
        mail_text = translate(mail_text, 'Poi', context=self.request)
        return mail_text

    @property
    def subject(self):
        context = aq_inner(self.context)
        tracker = context.getTracker()
        subject = _(
            'poi_email_new_response_subject_template',
            u"[${tracker_title}] #${issue_id} - Re: ${issue_title}",
            mapping=dict(
                tracker_title=su(tracker.getExternalTitle()),
                issue_id=su(context.getId()),
                issue_title=su(context.Title())))
        # Ensure that the subject is unicode and translate it too.
        subject = su(subject)
        subject = translate(subject, 'Poi', context=self.request)
        return subject


class ResolvedIssueMail(BasePoiMail):

    @property
    def plain(self):
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
        mail_text = _(
            'poi_email_issue_resolved_template',
            u"""The issue **${issue_title}** in the **${tracker_title}**
tracker has been marked as resolved by **${response_author}**.
Please visit the issue and either confirm that it has been
satisfactorily resolved or re-open it.

Response Information
--------------------

Issue
  ${issue_title} (${issue_url})


* This is an automated email, please do not reply - ${from_name}""",
            mapping=dict(
                issue_title=su(context.title_or_id()),
                tracker_title=su(tracker.title_or_id()),
                response_author=su(stateChanger),
                issue_url=su(context.absolute_url()),
                from_name=su(fromName)))

        # Translate the body text
        mail_text = translate(mail_text, 'Poi', context=self.request)
        return mail_text

    @property
    def subject(self):
        context = aq_inner(self.context)
        tracker = context.getTracker()
        subject = _(
            'poi_email_issue_resolved_subject_template',
            u"[${tracker_title}] Resolved #${issue_id} - ${issue_title}",
            mapping=dict(
                tracker_title=su(tracker.getExternalTitle()),
                issue_id=su(context.getId()),
                issue_title=su(context.Title())))
        # Make the subject unicode and translate it too.
        subject = su(subject)
        subject = translate(subject, 'Poi', context=self.request)
        return subject
