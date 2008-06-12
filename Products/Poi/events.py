from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
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

    portal_membership = getToolByName(issue, 'portal_membership')
    portal_url = getToolByName(issue, 'portal_url')
    portal = portal_url.getPortalObject()
    fromName = portal.getProperty('email_from_name', None)

    tracker = aq_parent(issue)

    creator = response.creator
    creatorInfo = portal_membership.getMemberInfo(creator)
    responseAuthor = creator
    if creatorInfo:
        responseAuthor = creatorInfo['fullname'] or creator

    responseText = response.text
    paras = responseText.split('\n\n')[:2]
    wrapper = textwrap.TextWrapper(initial_indent='    ',
                                   subsequent_indent='    ')
    responseDetails = '\n\n'.join([wrapper.fill(p) for p in paras])

    if not responseDetails.strip():
        responseDetails = None
    else:
        responseDetails = "**Response Details**::\n\n\n" + responseDetails

    addresses = tracker.getNotificationEmailAddresses(issue)
    # XXX

    changes = ''
    for change in response.changes:
        changes += change.get('before') + " -> " + change.get('before') + '\n'

    mailText = poi_email_new_response_template % dict(
        issue_title = issue.title_or_id(),
        tracker_title = tracker.title_or_id(),
        response_author = responseAuthor,
        response_details = responseDetails,
        issue_url = issue.absolute_url(),
        changes = changes,
        from_name = fromName)

    subject = "[%s] #%s - Re: %s" % (tracker.getExternalTitle(),
                                     issue.getId(), issue.Title())

    tracker.sendNotificationEmail(addresses, subject, mailText)


poi_email_new_response_template = """
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
