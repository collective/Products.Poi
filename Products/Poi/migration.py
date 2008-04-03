from StringIO import StringIO
from zope import interface
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Poi.interfaces import IIssue
from Products.Poi.adapters import Response
from Products.Poi.adapters import IResponseContainer
from Products.Poi.browser.response import Create
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
    request = issue.REQUEST
    createview = Create(issue, request)
    path = '/'.join(issue.getPhysicalPath())
    log.debug("Migrating %s responses for issue at %s.",
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
        log.info("Migrating %s issues in tracker %s.",
                 len(tracker.contentIds()), tracker.absolute_url())
        for issue in tracker.contentValues():
            replace_old_with_new_responses(issue)
        tracker.setSendNotificationEmails(original_send_emails)


def fix_descriptions(context):
    """Fix issue Descriptions.

    In revision 53855 a change was made that caused the Description
    field of issues that were first strings to now possibly turn into
    unicode.  That fixed this issue:
    http://plone.org/products/poi/issues/135

    But as stated at the bottom of that issue, this can give a
    UnicodeEncodeError when changing the issue or adding a response to
    it.  The Description string that is in the catalog brain is
    compared to the unicode Description from the object and this fails
    when the brain Description has non-ascii characters.

    A good workaround is to clear and rebuild the catalog.  But
    running this upgrade step also fixes it.
    """
    log.info("Start fixing issue descriptions.")
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults(portal_type='PoiIssue')
    log.info("Found %s PoiIssues.", len(brains))
    fixed = 0
    for brain in brains:
        if isinstance(brain.Description, str):
            issue = brain.getObject()
            if isinstance(issue.Description(), unicode):
                log.debug("Un/reindexing PoiIssue %s", brain.getURL())
                # This is the central point really: directly
                # reindexing this issue can fail if the description
                # has non-ascii characters.  So we unindex it first.
                catalog.unindexObject(issue)
                catalog.reindexObject(issue)
                fixed += 1
                if fixed % 100 == 0:
                    log.info("Fixed %s PoiIssues so far; still busy...", fixed)
    log.info("Fix completed.  %s PoiIssues needed fixing.", fixed)
