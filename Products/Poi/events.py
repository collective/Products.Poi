import logging

from Products.CMFCore.utils import getToolByName
from collective.watcherlist.interfaces import IWatcherList
from Products.Poi.interfaces import IIssue

logger = logging.getLogger('Poi')


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
    portal_workflow = getToolByName(object, 'portal_workflow')
    portal_workflow.doActionFor(object, 'post')


def mail_issue_change(object, event):
    """Send an email on some transitions of an issue.

    Specificiall: new issue and resolved issue.
    """
    if event.transition == 'post':
        watchers = IWatcherList(object)
        watchers.send('new-issue-mail')
    elif event.new_state == 'resolved':
        watchers = IWatcherList(object)
        watchers.send('resolved-issue-mail')


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
