from Acquisition import aq_parent
from Products.Poi.interfaces import IIssue


def removedResponse(object, event):
    issue = event.oldParent
    if IIssue.providedBy(issue):
        issue.reindexObject(idxs=['SearchableText'])
        issue.notifyModified()


def modifiedResponse(object, event):
    """A response is modified or created so update its parent.
    """
    # Old style response:
    parent = aq_parent(object)
    if parent is None:
        # New style response:
        parent = object.__parent__.context

    if IIssue.providedBy(parent):
        parent.reindexObject(idxs=['SearchableText'])
        parent.notifyModified()
