import logging
import textwrap

from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.PageTemplates.GlobalTranslationService import \
    getGlobalTranslationService

from Products.Poi.interfaces import IIssue
from Products.Poi import PoiMessageFactory as _

logger = logging.getLogger('Poi')


def removedResponse(object, event):
    issue = event.oldParent
    if IIssue.providedBy(issue):
        issue.reindexObject(idxs=['SearchableText'])
        issue.notifyModified()


def modifiedNewStyleResponse(object, event):
    """A response is modified or created so update its parent.
    """

    if len(event.descriptions) > 0:
        parent = event.descriptions[0]
        if IIssue.providedBy(parent):
            parent.reindexObject(idxs=['SearchableText'])
            parent.notifyModified()


def addedNewStyleResponse(object, event):
    """A response has been added.
    """
    issue = event.newParent
    if IIssue.providedBy(issue):
        issue.reindexObject(idxs=['SearchableText'])
        issue.notifyModified()
        sendResponseNotificationMail(issue, object)


def sendResponseNotificationMail(issue, response):
    """When a response is created, send a notification email to all
    tracker managers, unless emailing is turned off.
    """

    tracker = aq_parent(issue)
    addresses = tracker.getNotificationEmailAddresses(issue)
    if not addresses:
        # This also catches the case where there may be addresses but
        # the tracker is not configured to send emails.
        return

    portal_url = getToolByName(issue, 'portal_url')
    portal = portal_url.getPortalObject()
    portal_membership = getToolByName(portal, 'portal_membership')
    plone_utils = getToolByName(portal, 'plone_utils')
    ts = getGlobalTranslationService()

    charset = plone_utils.getSiteEncoding()

    # We are going to use the same encoding everywhere, so we will
    # make that easy.

    def su(value):
        return safe_unicode(value, encoding=charset)

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
        header = ts.translate('Poi', header, context=issue)
        responseDetails = u"**%s**::\n\n\n%s" % (header, responseDetails)

    changes = u''
    for change in response.changes:
        before = su(change.get('before'))
        after = su(change.get('after'))
        # Some changes are workflow changes, which can be translated.
        # Note that workflow changes are in the plone domain.
        before = ts.translate('plone', before, context=issue)
        after = ts.translate('plone', after, context=issue)
        changes += u"%s -> %s\n" % (before, after)
        if response.attachment:
            extra = _(
                'poi_attachment_added',
                u"An attachment has been added with id ${attachment_id}",
                mapping=dict(
                    attachment_id=response.attachment.getId()))
            extra = ts.translate(extra, 'Poi', context=issue)
            changes += extra + "\n"

    mailText = _(
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
            issue_title = su(issue.title_or_id()),
            tracker_title = su(tracker.title_or_id()),
            response_author = responseAuthor,
            response_details = responseDetails,
            issue_url = su(issue.absolute_url()),
            changes = changes,
            from_name = fromName))

    subject = _(
        'poi_email_new_response_subject_template',
        u"[${tracker_title}] #${issue_id} - Re: ${issue_title}",
        mapping=dict(
            tracker_title = su(tracker.getExternalTitle()),
            issue_id = su(issue.getId()),
            issue_title = su(issue.Title())))

    tracker.sendNotificationEmail(addresses, subject, mailText)
