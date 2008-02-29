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

