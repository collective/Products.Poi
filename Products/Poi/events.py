from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from Products.Poi.interfaces import IIssue
import textwrap


def removedResponse(object, event):
    issue = event.oldParent
    if IIssue.providedBy(issue):
        issue.reindexObject(idxs=['SearchableText'])
        issue.notifyModified()


def modifiedResponse(object, event):
    """A response is modified or created so update its parent.
    """
    parent = aq_parent(object)
    if IIssue.providedBy(parent):
        parent.reindexObject(idxs=['SearchableText'])
        parent.notifyModified()


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
    paras = responseText.split(u'\n\n')[:2]
    wrapper = textwrap.TextWrapper(initial_indent=u'    ',
                                   subsequent_indent=u'    ')
    responseDetails = u'\n\n'.join([wrapper.fill(p) for p in paras])

    if not responseDetails.strip():
        responseDetails = u''
    else:
        responseDetails = u"**Response Details**::\n\n\n" + responseDetails

    changes = u''
    for change in response.changes:
        changes += u"%s -> %s" % (su(change.get('before')),
                                  su(change.get('after')))

    mailText = poi_email_new_response_template % dict(
        issue_title = su(issue.title_or_id()),
        tracker_title = su(tracker.title_or_id()),
        response_author = responseAuthor,
        response_details = responseDetails,
        issue_url = su(issue.absolute_url()),
        changes = changes,
        from_name = fromName)

    subject = u"[%s] #%s - Re: %s" % (su(tracker.getExternalTitle()),
                                      su(issue.getId()),
                                      su(issue.Title()))

    tracker.sendNotificationEmail(addresses, subject, mailText)


poi_email_new_response_template = u"""
A new response has been given to the issue **%(issue_title)s**
in the tracker **%(tracker_title)s** by **%(response_author)s**.

Response Information
--------------------

Issue
  %(issue_title)s (%(issue_url)s)

%(changes)s
%(response_details)s

\* This is an automated email, please do not reply - %(from_name)s
"""
