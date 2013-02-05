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
    if not value:
        return
    member_email = get_member_email()
    if member_email == value:
        # We can add the userid instead of the email.
        portal_membership = getToolByName(object, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        value = member.getId()
    watchers = list(object.getWatchers())
    if value in watchers:
        return
    logger.info('Adding contact %s to watchers of issue %r.', value, object)
    watchers.append(value)
    object.setWatchers(tuple(watchers))


def add_manager_to_issue_watchers(object, event=None):
    """Add manager to issue watchers.

    Add the responsible manager (can be TrackerManager or Technician)
    of the issue to the watchers.

    It might make sense to only do this when the manager is a
    Technician.  Some thoughts about this:

    - It should not matter, as TrackerManagers currently cannot really
      opt out of receiving issue emails, except temporarily until
      someone edits the tracker (see the update_tracker_watchers
      method).

    - But when a user is a TrackerManager, gets assigned an issue, and
      is then made Technician instead, he should still be a watcher.

    - But in any case, when a response is added to the issue, this
      method will get called, so the currently responsible manager
      will be added as watcher.

    """
    manager = object.getResponsibleManager()
    if not manager or manager == '(UNASSIGNED)':
        return
    watchers = list(object.getWatchers())
    if manager in watchers:
        return
    logger.info('Adding manager %s to watchers of issue %r.', manager, object)
    watchers.append(manager)
    object.setWatchers(tuple(watchers))


def update_tracker_watchers(object, event=None):
    """Update tracker watchers.

    If there is a mailing list, make sure it is in the
    extra_addresses.  Okay, this is actually handled automatically by
    the adapter.

    If there is NO mailing list, make sure all tracker managers are
    watchers.

    Note that this means that tracker managers can only temporarily
    unsubscribe: once someone edits the tracker, all tracker managers
    are added again, unless a mailing list has been set.

    """
    watchers = list(object.getWatchers())
    changed = False
    for manager in object.getManagers():
        if manager not in watchers:
            logger.info('Adding manager %s to watchers of tracker %r.',
                        manager, object)
            watchers.append(manager)
            changed = True
    if changed:
        object.setWatchers(tuple(watchers))


def merge_response_changes_to_issue(issue):
    """Update the issue with possible changes due to responses.

    Responses can influence their issue in several ways:

    - The text of the response should be added to the searchable text
      of the issue.

    - The responsible manager may have changed, so the watchers field
      may need to be updated.
    """
    add_manager_to_issue_watchers(issue, event=None)
    issue.reindexObject(idxs=['SearchableText'])
    issue.notifyModified()


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
    add_manager_to_issue_watchers(object, event)
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
        merge_response_changes_to_issue(issue)


def modifiedNewStyleResponse(object, event):
    """A response is modified or created so update its parent.
    """
    if len(event.descriptions) > 0:
        parent = event.descriptions[0]
        if IIssue.providedBy(parent):
            merge_response_changes_to_issue(parent)


def addedNewStyleResponse(object, event):
    """A response has been added.
    """
    issue = event.newParent
    if IIssue.providedBy(issue):
        merge_response_changes_to_issue(issue)
        sendResponseNotificationMail(issue)


def sendResponseNotificationMail(issue):
    # As we take the last response by default, we can keep this simple.
    watchers = IWatcherList(issue)
    watchers.send('new-response-mail')
