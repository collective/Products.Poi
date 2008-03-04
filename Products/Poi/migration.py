from StringIO import StringIO
from zope import interface
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Poi.interfaces import IIssue
from Products.Poi.adapters import Response
from Products.Poi.adapters import IResponseContainer
from Products.Poi.browser.response import Create
from zope.publisher.browser import TestRequest
import logging
log = logging.getLogger("Poi")


class IMigration(interface.Interface):
    def fix_btrees():
        """The order of inheritance of PoiPscTracker was broken at
        some point.  We need to fix BTreeFolders without `self._tree`.
        """

class Migration(BrowserView):
    def __call__(self):
        migration_id = self.request.get('migration_id')
        assert migration_id in IMigration.names(), "Unknown migration"
        return getattr(self, migration_id)()

    def fix_btrees(self):
        out = StringIO()
        catalog = getToolByName(self.context, 'portal_catalog')
        for b in catalog(portal_type='PoiPscTracker'):
            tracker = b.getObject()
            if tracker._tree is None:
                tracker._initBTrees()
                out.write('Fixed BTreeFolder at %s\n' %
                          '/'.join(tracker.getPhysicalPath()))
        return out.getvalue()


def replace_old_with_new_responses(issue):
    if not IIssue.providedBy(issue):
        return
    responses = issue.contentValues(filter={'portal_type' : 'PoiResponse'})
    folder = IResponseContainer(issue)
    request = TestRequest()
    createview = Create(issue, request)
    path = '/'.join(issue.getPhysicalPath())
    log.info("Will migrate %s responses for issue at %s.",
             len(responses), path)
    for old_response in responses:
        field = old_response.getField('response')
        text = field.getRaw(old_response)
        new_response = Response(text)
        new_response.mime_type = field.getContentType(old_response)
        new_response.creator = old_response.Creator()
        new_response.date = old_response.CreationDate()
        new_response.type = createview.determine_response_type(new_response)
        changes = old_response.getIssueChanges()
        for change in changes:
            new_response.add_change(**change)
        folder.add(new_response)
        issue._delObject(old_response.getId())
    # This seems a good time to reindex the issue for good measure.
    issue.reindexObject()

def migrate_responses(context):
    log.info("Starting migration of old style to new style responses.")
    catalog = getToolByName(context, 'portal_catalog')
    tracker_brains = catalog.searchResults(portal_type='PoiTracker')
    log.info("Found %s PoiTrackers.", len(tracker_brains))
    for brain in tracker_brains:
        tracker = brain.getObject()
        # We definitely do not want to send any emails for responses
        # added or removed during this migration.
        original_send_emails = tracker.getSendNotificationEmails()
        tracker.setSendNotificationEmails(False)
        for issue in tracker.contentValues():
            replace_old_with_new_responses(issue)
        tracker.setSendNotificationEmails(original_send_emails)
