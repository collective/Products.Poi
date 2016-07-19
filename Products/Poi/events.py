import logging

from Products.CMFCore.utils import getToolByName
from collective.watcherlist.interfaces import IWatcherList
from collective.watcherlist.utils import get_member_email
from plone import api

from Products.Poi.interfaces import IIssue

from Acquisition import aq_inner
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission
from zc.relation.interfaces import ICatalog
from z3c.relationfield import RelationValue

logger = logging.getLogger('Poi')


def add_contact_to_issue_watchers(object, event=None):
    """Add the contact of the issue to the watchers.

    Called when an issue has been initialized or edited.
    """
    value = unicode(object.Creator())
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


def assign_id(new_issue, event):
    """Auto-increment ID numbers"""
    issue_id = 1
    tracker = api.content.get(UID=new_issue._tracker_uid)
    issues = api.content.find(context=tracker, object_provides=IIssue)
    existing_ids = [int(issue.id) for issue in issues if issue.id.isdigit()]
    if len(existing_ids):
        issue_id = max(existing_ids) + 1
    issue_id = str(issue_id)
    api.content.rename(obj=new_issue, new_id=issue_id)


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
    add_assignee_to_issue_watchers(object, event)
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


def update_references(object, event=None):
    """Get list of Related Issues set here, and relate them back
       Then check the getBRefs to remove references that have been removed
       Sort the issues in descending id order
    """
    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    objintid = intids.getId(aq_inner(object))

    # sort the relationvalues on this object by id
    relatedIssues = sorted(object.related_issue,
                           key=lambda issue: int(issue.to_object.id),
                           reverse=True)
    object.related_issue = relatedIssues

    # add this issue to its related issues where needed
    for issue in relatedIssues:
        others_related = issue.to_object.related_issue
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
