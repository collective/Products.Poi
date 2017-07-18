import logging

from collective.watcherlist.interfaces import IWatcherList
from plone import api

from Products.Archetypes.atapi import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException

from Products.Poi import permissions
from Products.Poi.adapters import IResponseContainer
from Products.Poi.adapters import Response
from Products.Poi.interfaces import IIssue
from Products.Poi.content.issue import next_issue_id
from Products.Poi.content.tracker import possibleAssignees

from Acquisition import aq_inner
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectAddedEvent,\
    ObjectModifiedEvent, ObjectRemovedEvent
from zc.relation.interfaces import ICatalog
from z3c.relationfield import RelationValue

logger = logging.getLogger('Poi')


def add_contact_to_issue_watchers(object, event=None):
    """Add the contact of the issue to the watchers.

    Called when an issue has been initialized or edited.
    """
    if not object.contact_email:
        return
    value = unicode(object.contact_email)
    watchers = object.watchers or []
    if value in watchers:
        return
    logger.info('Adding contact %s to watchers of issue %r.', value, object)
    watchers.append(value)
    object.watchers = watchers


def add_assignee_to_issue_watchers(object, event=None):
    """Add assignee to issue watchers.

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
    assignee = object.assignee
    if not assignee or assignee == '(UNASSIGNED)':
        return
    watchers = object.watchers or []
    if assignee in watchers:
        return
    logger.info('Adding assignee %s to watchers of issue %r.', assignee, object)
    watchers.append(assignee)
    object.watchers = watchers


def merge_response_changes_to_issue(issue):
    """Update the issue with possible changes due to responses.

    Responses can influence their issue in several ways:

    - The text of the response should be added to the searchable text
      of the issue.

    - The responsible manager may have changed, so the watchers field
      may need to be updated.
    """
    add_assignee_to_issue_watchers(issue, event=None)
    issue.reindexObject(idxs=['SearchableText'])
    issue.notifyModified()


def remember_tracker(new_issue, event):
    """make a note of the tracker's UID"""
    new_issue._tracker_uid = event.newParent.UID()


def fix_copy_move_id(new_issue, event):
    """Fix the id of an issue when it is being copied or moved"""
    tracker = api.content.get(UID=new_issue._tracker_uid)
    issue_id = next_issue_id(tracker)
    api.content.rename(obj=new_issue, new_id=issue_id)


def assign_id(new_issue, event):
    """Auto-increment ID numbers when they are created.
       Don't run on copied issues
    """
    if new_issue.id.find('copy') >= 0 or new_issue.id.isdigit():
        # don't rename copied issues or those that already have a numeric ID
        return
    tracker = api.content.get(UID=new_issue._tracker_uid)
    issue_id = next_issue_id(tracker)
    api.content.rename(obj=new_issue, new_id=issue_id)


def post_issue(object, event):
    """Finalise posting of an issue.

    If an anonymous user is posting, Creator would normally be set to
    the root zope manager, as this user will become the owner.
    Instead we give a more sensible default.

    """
    portal_membership = api.portal.get_tool('portal_membership')
    if portal_membership.isAnonymousUser():
        object.setCreators(('(anonymous)',))


def mail_issue_change(object, event):
    """Send an email when an issue is resolved
    """
    if event.new_state.id == 'resolved':
        watchers = IWatcherList(object)
        # Only mail the original poster, if available.
        address = object.getContactEmail()
        if address:
            watchers.send('resolved-issue-mail',
                          only_these_addresses=[address])


def mail_issue_add(object, event):
    """Send an email when a new issue is created
    """
    if object.modified() != object.created():
        return
    if object.getReviewState()['state'] == 'unconfirmed':
        watchers = IWatcherList(object)
        watchers.send('new-issue-mail')


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


def update_references(object, event=None):
    """Get list of Related Issues set here, and relate them back
       Then check the getBRefs to remove references that have been removed
       Sort the issues in descending id order
    """
    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    objintid = intids.getId(aq_inner(object))

    if object.related_issue is None:
        return
    # sort the relationvalues on this object by id
    relatedIssues = sorted(object.related_issue,
                           key=lambda issue: int(issue.to_object.id),
                           reverse=True)
    object.related_issue = relatedIssues

    # add this issue to its related issues where needed
    for issue in relatedIssues:
        others_related = issue.to_object.related_issue
        if not others_related:
            others_related = []
        for other in others_related:
            if objintid == other.to_id:
                break
        else:
            rv = RelationValue(objintid)
            others_related.append(rv)
            issue.to_object.related_issue = sorted(
                others_related,
                key=lambda issue: int(issue.to_id),
                reverse=True)

    # find other issues related to this one
    issuesRelated = []
    for rel in catalog.findRelations(
        dict(to_id=objintid,
             from_attribute='related_issue')):
        issuesRelated.append(RelationValue(rel.from_id))

    # remove relations from those issues to this one if neeeded
    for issue in issuesRelated:
        if issue.to_id in [r.to_id for r in object.related_issue]:
            continue
        issue_object = intids.queryObject(issue.to_id)
        others_related = issue_object.related_issue
        if objintid not in [r.to_id for r in others_related]:
            continue
        others_related = [x for x in others_related if x.to_id != objintid]
        issue_object.related_issue = others_related


def available_assignees(issue):
    """Get the tracker assignees.
    """
    # get vocab from issue
    tracker = issue.aq_parent
    memship = getToolByName(tracker, 'portal_membership')

    if not memship.checkPermission(
            permissions.ModifyIssueAssignment, tracker):
        return DisplayList()
    return possibleAssignees(tracker)


def add_response_for_files(object, event):
    """If a file/image is added or deleted, add a response."""
    if isinstance(event, ObjectAddedEvent):
        parent = event.newParent
        # do not add response if attachment is migrating to DX
        checkid = object.id + '_MIGRATION_'
        if any(att.id == checkid for att in parent.getFolderContents()):
            return
        if parent.portal_type == "Issue":
            issue = parent
            new_response = Response("")
        else:
            return
    elif isinstance(event, ObjectModifiedEvent):
        if object.aq_parent.portal_type == "Issue":
            issue = object.aq_parent
            new_response = Response("")
        else:
            return
    elif isinstance(event, ObjectRemovedEvent):
        if event.oldParent.portal_type == "Issue":
            issue = event.oldParent
            new_response = Response("Attachment deleted: " + object.title)
        else:
            return

    if new_response:
        new_response.attachment = object
        new_response.mimetype =\
            api.portal.get_registry_record('poi.default_issue_mime_type')
        new_response.type = "file"
        folder = IResponseContainer(issue)
        folder.add(new_response)
