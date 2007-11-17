from Products.Poi.interfaces import IIssue


def removedResponse(object, event):
    issue = event.oldParent
    if IIssue.providedBy(issue):
        issue.reindexObject(idxs=['SearchableText'])
