import logging

from Products.CMFCore.utils import getToolByName
from collective.watcherlist.interfaces import IWatcherList
from collective.watcherlist.utils import get_member_email
from Products.Poi.interfaces import IIssue

logger = logging.getLogger('Poi')


def add_contact_to_issue_watchers(object, event=None):
    """Add the contactEmail of the issue to the watchers.

    Try to add the userid instead of the email.

    Called when an issue has been initialized or edited.
    """
    value = object.getContactEmail()
    logger.info('Calling add_contact_to_issue_watchers with value: %r', value)
    if not value:
        logger.info('No value; done.')
        return
    member_email = get_member_email()
    if member_email == value:
        logger.info('member email is value')
        # We can add the userid instead of the email.
        portal_membership = getToolByName(object, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        value = member.getId()
    watchers = list(object.getWatchers())
    if value not in watchers:
        logger.info('value not in watchers, so adding')
        watchers.append(value)
        object.setWatchers(tuple(watchers))
    logger.info('done')


def post_issue(object, event):
    """Finalise posting of an issue.

    If an anonymous user is posting, Creator would normally be set to
    the root zope manager, as this user will become the owner.
    Instead we give a more sensible default.

    And we do the 'post' transition.

    And send the initial email.

    """
    portal_membership = getToolByName(object, 'portal_membership')
    if portal_membership.isAnonymousUser():
        object.setCreators(('(anonymous)',))
    add_contact_to_issue_watchers(object, event)
    portal_workflow = getToolByName(object, 'portal_workflow')
    portal_workflow.doActionFor(object, 'post')


def mail_issue_change(object, event):
    """Send an email on some transitions of an issue.

    Specifically: new issue and resolved issue.
    """
    if event.transition and event.transition.id == 'post':
        watchers = IWatcherList(object)
        watchers.send('new-issue-mail')
    elif event.new_state.id == 'resolved':
        watchers = IWatcherList(object)
        # Only mail the original poster, if available.
        address = object.getContactEmail()
        if address:
            watchers.send('resolved-issue-mail',
                          only_these_addresses=[address])


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
        sendResponseNotificationMail(issue)


def sendResponseNotificationMail(issue):
    # As we take the last response by default, we can keep this simple.
    watchers = IWatcherList(issue)
    watchers.send('new-response-mail')
